import streamlit as st
import pandas as pd
from datetime import datetime
from supabase_db import supabase, load_products, insert_order

# --- CẤU HÌNH ---
st.set_page_config(page_title="Thành Viễn ERP", layout="wide")

def get_product_df():
    res = load_products()
    if res and res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "name", "sale_price", "stock_quantity"])

st.title("🏢 Quản Lý Thành Viễn (Supabase)")

# Lấy dữ liệu sản phẩm
df_p = get_product_df()

col_in, col_out = st.columns([1, 1.5])

with col_in:
    st.subheader("🛒 Tạo Đơn Hàng")
    if df_p.empty:
        st.warning("Chưa có sản phẩm. Hãy thêm dữ liệu vào Supabase.")
    else:
        with st.form("sale_form", clear_on_submit=True):
            cust = st.text_input("Khách hàng", "Khách lẻ")
            p_names = df_p['name'].tolist()
            sel_name = st.selectbox("Sản phẩm", p_names)
            
            # Lấy thông tin sản phẩm đang chọn
            p_info = df_p[df_p['name'] == sel_name].iloc[0]
            
            c1, c2 = st.columns(2)
            qty = c1.number_input("Số lượng", min_value=1, value=1)
            prc = c2.number_input("Giá bán", value=int(p_info['sale_price']))
            
            if st.form_submit_button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                if p_info['stock_quantity'] < qty:
                    st.error(f"Không đủ kho! Còn: {p_info['stock_quantity']}")
                else:
                    # Chuẩn bị dữ liệu (Lưu ý: product_id là UUID)
                    data = {
                        "customer_name": cust,
                        "product_id": str(p_info['id']),
                        "quantity": qty,
                        "price": prc,
                        "total_amount": qty * prc,
                        "order_date": datetime.now().isoformat()
                    }
                    
                    if insert_order(data):
                        # Cập nhật tồn kho
                        new_stk = p_info['stock_quantity'] - qty
                        supabase.table("products").update({"stock_quantity": new_stk}).eq("id", p_info['id']).execute()
                        st.success("Đã ghi nhận đơn hàng!")
                        st.rerun()

with col_out:
    st.subheader("📜 Nhật Ký Đơn Hàng")
    try:
        # Truy vấn JOIN lấy tên sản phẩm nhờ Foreign Key (mắt xích xanh)
        res = supabase.table("orders").select("order_date, customer_name, quantity, total_amount, products(name)").order("order_date", desc=True).limit(10).execute()
        
        if res.data:
            df_h = pd.DataFrame(res.data)
            # Lấy tên sản phẩm từ cột quan hệ
            df_h['Sản phẩm'] = df_h['products'].apply(lambda x: x['name'] if x else "N/A")
            
            view_df = df_h[['order_date', 'customer_name', 'Sản phẩm', 'quantity', 'total_amount']]
            view_df.columns = ['Ngày', 'Khách', 'Sản phẩm', 'SL', 'Tổng tiền']
            st.dataframe(view_df, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có giao dịch.")
    except Exception as e:
        st.error(f"Lỗi hiển thị: {e}")

    st.divider()
    st.subheader("📦 Trạng Thái Kho")
    st.dataframe(df_p[['name', 'stock_quantity', 'sale_price']], use_container_width=True, hide_index=True)
