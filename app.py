import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_db import supabase, load_products, insert_order

# --- CẤU HÌNH TRANG CHUẨN 2026 ---
st.set_page_config(page_title="Thành Viễn ERP", layout="wide", page_icon="🏢")

# Hàm lấy dữ liệu sản phẩm và xử lý kiểu dữ liệu Pandas
def get_product_df():
    res = load_products()
    if res and res.data:
        df = pd.DataFrame(res.data)
        return df
    return pd.DataFrame(columns=["id", "name", "sale_price", "stock_quantity"])

st.title("🏢 Hệ Thống Quản Lý Thành Viễn")

# 1. Lấy dữ liệu sản phẩm mới nhất
df_p = get_product_df()

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.subheader("🛒 Tạo Đơn Hàng")
    if df_p.empty:
        st.warning("Chưa có sản phẩm. Vui lòng thêm dữ liệu vào bảng 'products'.")
    else:
        with st.form("sale_form", clear_on_submit=True):
            cust = st.text_input("Tên khách hàng", "Khách lẻ")
            
            p_names = df_p['name'].tolist()
            sel_name = st.selectbox("Chọn sản phẩm", p_names)
            
            # Lấy thông tin sản phẩm đang chọn từ DataFrame
            p_info = df_p[df_p['name'] == sel_name].iloc[0]
            
            c1, c2 = st.columns(2)
            qty = c1.number_input("Số lượng", min_value=1, value=1)
            prc = c2.number_input("Giá bán (VNĐ)", value=int(p_info['sale_price']))
            
            # Nút xác nhận với chuẩn width='stretch'
            if st.form_submit_button("XÁC NHẬN BÁN", type="primary", width='stretch'):
                if p_info['stock_quantity'] < qty:
                    st.error(f"Kho không đủ! Hiện còn: {p_info['stock_quantity']}")
                else:
                    try:
                        # --- BƯỚC QUAN TRỌNG: ÉP KIỂU DỮ LIỆU SẠCH (FIX LỖI JSON) ---
                        p_id_clean = str(p_info['id'])
                        new_stk = int(p_info['stock_quantity'] - qty)
                        
                        data_to_insert = {
                            "customer_name": str(cust),
                            "product_id": p_id_clean,
                            "quantity": int(qty),
                            "price": float(prc), 
                            "total_amount": float(qty * prc),
                            "order_date": datetime.now().isoformat()
                        }
                        
                        # 2. Ghi đè đơn hàng vào bảng 'orders'
                        res_insert = insert_order(data_to_insert)
                        
                        if res_insert:
                            # 3. Cập nhật trừ tồn kho trong bảng 'products'
                            supabase.table("products").update(
                                {"stock_quantity": new_stk}
                            ).eq("id", p_id_clean).execute()
                            
                            st.success(f"Đã bán {qty} {sel_name}. Cập nhật kho thành công!")
                            st.rerun()
                            
                    except Exception as e:
                        st.error(f"Lỗi khi xử lý giao dịch: {e}")

with col_out:
    st.subheader("📜 Nhật Ký 10 Đơn Hàng Gần Nhất")
    try:
        # Truy vấn Join để lấy tên sản phẩm
        res_h = supabase.table("orders").select(
            "order_date, customer_name, quantity, total_amount, products(name)"
        ).order("order_date", desc=True).limit(10).execute()
        
        if res_h.data:
            df_h = pd.DataFrame(res_h.data)
            # Xử lý lấy tên từ object 'products'
            df_h['Sản phẩm'] = df_h['products'].apply(lambda x: x['name'] if x else "N/A")
            
            # Chọn cột hiển thị
            view_df = df_h[['order_date', 'customer_name', 'Sản phẩm', 'quantity', 'total_amount']]
            view_df.columns = ['Ngày giờ', 'Khách hàng', 'Sản phẩm', 'SL', 'Tổng tiền']
            
            st.dataframe(view_df, width='stretch', hide_index=True)
        else:
            st.info("Chưa có lịch sử giao dịch.")
    except Exception as e:
        st.error(f"Lỗi hiển thị lịch sử: {e}")

    st.divider()
    st.subheader("📦 Tình Trạng Kho Thực Tế")
    # Hiển thị bảng tồn kho với định dạng mới
    st.dataframe(
        df_p[['name', 'stock_quantity', 'sale_price']], 
        width='stretch', 
        hide_index=True
    )
