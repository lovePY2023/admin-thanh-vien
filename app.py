import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Hệ Thống Bán Hàng & Dịch Vụ", layout="wide")

# --- CSS TÙY CHỈNH CHO GIAO DIỆN CÂN ĐỐI ---
st.markdown("""
    <style>
    .main-header { font-size: 24px; font-weight: bold; color: #1E88E5; margin-bottom: 20px; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; font-weight: bold; }
    .stock-card { background-color: #f8f9fa; padding: 10px; border-radius: 8px; border-left: 5px solid #28a745; }
    div[data-testid="column"] { padding: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU (Giả lập) ---
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"id": "P001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "stock": 15, "price": 8500000, "category": "Hàng Hóa"},
        {"id": "P002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "stock": 200, "price": 150000, "category": "Vật Tư"},
        {"id": "S001", "name": "Vệ Sinh Máy Lạnh", "unit": "Lần", "stock": 999, "price": 200000, "category": "Dịch Vụ"},
        {"id": "S002", "name": "Nạp Gas R32 Full", "unit": "Lần", "stock": 999, "price": 350000, "category": "Dịch Vụ"}
    ])

if 'sales_history' not in st.session_state:
    st.session_state.sales_history = pd.DataFrame(columns=["Ngày", "Khách Hàng", "Nội Dung", "Loại", "Thành Tiền"])

# --- GIAO DIỆN CHÍNH (2 CỘT) ---
st.markdown('<p class="main-header">🛒 QUẢN LÝ BÁN HÀNG & DỊCH VỤ</p>', unsafe_allow_html=True)

left_col, right_col = st.columns([1.2, 1.8], gap="large")

# --- BÊN TRÁI: FORM NHẬP THÔNG TIN ---
with left_col:
    st.subheader("📋 Thông Tin Đơn Hàng")
    with st.container(border=True):
        customer = st.text_input("Tên Khách Hàng", placeholder="Ví dụ: Anh Thành - Gò Vấp")
        phone = st.text_input("Số Điện Thoại")
        
        type_sale = st.radio("Loại Hình", ["Dịch Vụ (Sửa chữa/Bảo trì)", "Bán Hàng (Vật tư/Máy)"], horizontal=True)
        
        # Lọc danh sách item dựa trên loại hình
        if type_sale == "Dịch Vụ (Sửa chữa/Bảo trì)":
            options = st.session_state.products[st.session_state.products['category'] == "Dịch Vụ"]
        else:
            options = st.session_state.products[st.session_state.products['category'] != "Dịch Vụ"]
            
        selected_item = st.selectbox("Chọn Sản Phẩm / Dịch Vụ", options['name'])
        item_info = options[options['name'] == selected_item].iloc[0]
        
        qty = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
        
        price_custom = st.number_input("Đơn giá tùy chỉnh (VNĐ)", value=int(item_info['price']), step=10000)
        
        total = qty * price_custom
        st.markdown(f"### Tổng tiền: :blue[{total:,.0f} VNĐ]")
        
        if st.button("XÁC NHẬN & LƯU ĐƠN", type="primary"):
            if customer:
                # 1. Cập nhật tồn kho nếu là Hàng hóa/Vật tư
                if item_info['category'] != "Dịch Vụ":
                    idx = st.session_state.products[st.session_state.products['name'] == selected_item].index[0]
                    st.session_state.products.at[idx, 'stock'] -= qty
                
                # 2. Lưu lịch sử
                new_sale = {
                    "Ngày": datetime.now().strftime("%d/%m/%Y %H:%M"),
                    "Khách Hàng": customer,
                    "Nội Dung": f"{selected_item} (x{qty})",
                    "Loại": "Dịch Vụ" if item_info['category'] == "Dịch Vụ" else "Bán Hàng",
                    "Thành Tiền": total
                }
                st.session_state.sales_history = pd.concat([pd.DataFrame([new_sale]), st.session_state.sales_history], ignore_index=True)
                
                st.success("Đã ghi nhận đơn hàng và cập nhật kho!")
                st.rerun()
            else:
                st.error("Vui lòng nhập tên khách hàng")

# --- BÊN PHẢI: KHO HÀNG & LỊCH SỬ ---
with right_col:
    tab1, tab2 = st.tabs(["📦 Trạng Thái Kho", "📜 Giao Dịch Gần Đây"])
    
    with tab1:
        st.subheader("Tra cứu tồn kho thực tế")
        # Tìm kiếm nhanh trong kho
        search_q = st.text_input("🔍 Tìm tên hàng hóa/vật tư...", placeholder="Nhập tên sản phẩm...")
        
        display_stock = st.session_state.products.copy()
        if search_q:
            display_stock = display_stock[display_stock['name'].str.contains(search_q, case=False)]
        
        # Hiển thị Grid Kho hàng
        for i in range(0, len(display_stock), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(display_stock):
                    row = display_stock.iloc[i + j]
                    with cols[j]:
                        color = "#d4edda" if row['stock'] > 10 else "#fff3cd"
                        if row['category'] == "Dịch Vụ": color = "#e2f0fe"
                        
                        st.markdown(f"""
                            <div style="background-color: {color}; padding: 15px; border-radius: 10px; border: 1px solid #ddd; margin-bottom: 10px;">
                                <div style="font-weight: bold; font-size: 16px;">{row['name']}</div>
                                <div style="display: flex; justify-content: space-between; margin-top: 5px;">
                                    <span>Tồn: <b>{row['stock']} {row['unit']}</b></span>
                                    <span style="color: #1E88E5;">{row['price']:,.0f} đ</span>
                                </div>
                                <div style="font-size: 12px; color: #666; margin-top: 3px;">Mã: {row['id']} | {row['category']}</div>
                            </div>
                        """, unsafe_allow_html=True)
    
    with tab2:
        st.subheader("Các đơn hàng đã chốt")
        if st.session_state.sales_history.empty:
            st.info("Chưa có đơn hàng nào trong phiên làm việc này.")
        else:
            st.dataframe(st.session_state.sales_history, use_container_width=True, hide_index=True)
            
            # Tính doanh thu nhanh
            total_rev = st.session_state.sales_history['Thành Tiền'].sum()
            st.metric("Tổng Doanh Thu Phiên Này", f"{total_rev:,.0f} VNĐ")

# --- FOOTER ---
st.divider()
st.caption("MiniERP v1.0 - Hệ thống hỗ trợ Bán hàng & Định khoản nháp")
