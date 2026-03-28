import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Thành Viễn ERP - Nhập Nhanh",
    page_icon="⚡",
    layout="wide"
)

# --- CSS TÙY CHỈNH GIỐNG MẪU EXCEL ---
st.markdown("""
<style>
    .entry-container {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 10px;
    }
    .label-mb {
        background-color: #c6d9f1; /* Màu xanh nhạt cho MB */
        padding: 10px;
        border: 1px solid #95b3d7;
        font-weight: bold;
        text-align: left;
        border-radius: 4px 0 0 4px;
    }
    .label-vt {
        background-color: #f2dcda; /* Màu đỏ nhạt cho VT */
        padding: 10px;
        border: 1px solid #e6b8b7;
        font-weight: bold;
        text-align: left;
        border-radius: 4px 0 0 4px;
    }
    .stock-val {
        background-color: #ffffff;
        padding: 10px;
        border: 1px solid #ccc;
        text-align: center;
        font-family: monospace;
    }
    /* Tối ưu hóa ô nhập liệu */
    div[data-baseweb="input"] {
        border-radius: 0 4px 4px 0 !important;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU (Có kiểm tra cấu trúc để tránh KeyError) ---
def init_data():
    default_inventory = {
        "MB": [
            {"name": "MB 20K", "stock": 110, "price": 20000},
            {"name": "MB 50K", "stock": 104, "price": 50000},
            {"name": "MB 100K", "stock": 113, "price": 100000},
            {"name": "MB 200K", "stock": 97, "price": 200000},
            {"name": "MB 500K", "stock": 100, "price": 500000},
        ],
        "VT": [
            {"name": "VT 20K", "stock": 90, "price": 20000},
            {"name": "VT 50K", "stock": 97, "price": 50000},
            {"name": "VT 100K", "stock": 103, "price": 100000},
            {"name": "VT 200K", "stock": 92, "price": 200000},
            {"name": "VT 500K", "stock": 100, "price": 500000},
        ]
    }
    
    # Kiểm tra nếu inventory chưa có HOẶC đang ở định dạng DataFrame cũ thì reset lại
    if 'inventory' not in st.session_state or isinstance(st.session_state.inventory, pd.DataFrame):
        st.session_state.inventory = default_inventory

init_data()

def main():
    st.title("⚡ Nhập Số Lượng Bán Nhanh")
    
    # Khu vực thông tin chung
    with st.container(border=True):
        col_info1, col_info2, col_info3 = st.columns([2, 1, 1])
        with col_info1:
            st.selectbox("Chọn Khách Hàng", ["Khách vãng lai", "Đại lý Cấp 1", "Cửa hàng A"])
        with col_info2:
            st.date_input("Ngày bán", datetime.now())
        with col_info3:
            # Nút reset dữ liệu nếu cần
            if st.button("🔄 Làm mới trang"):
                st.session_state.clear()
                st.rerun()

    st.write("")

    # Lưu trữ số lượng nhập vào
    order_data = {} 

    col_left, col_right = st.columns(2)

    # CỘT MB (Xanh)
    with col_left:
        st.markdown("### 🟦 MOBIFONE")
        for i, item in enumerate(st.session_state.inventory["MB"]):
            c1, c2, c3 = st.columns([3, 1.5, 3])
            c1.markdown(f'<div class="label-mb">{item["name"]}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
            order_data[item["name"]] = c3.number_input(
                f"Qty {item['name']}", 
                min_value=0, 
                step=1, 
                key=f"in_mb_{i}", 
                label_visibility="collapsed"
            )

    # CỘT VT (Đỏ)
    with col_right:
        st.markdown("### 🟥 VIETTEL")
        for i, item in enumerate(st.session_state.inventory["VT"]):
            c1, c2, c3 = st.columns([3, 1.5, 3])
            c1.markdown(f'<div class="label-vt">{item["name"]}</div>', unsafe_allow_html=True)
            c2.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
            order_data[item["name"]] = c3.number_input(
                f"Qty {item['name']}", 
                min_value=0, 
                step=1, 
                key=f"in_vt_{i}", 
                label_visibility="collapsed"
            )

    st.divider()

    # TÍNH TOÁN TỔNG ĐƠN
    total_amount = 0
    items_to_sell = []
    for category in ["MB", "VT"]:
        for item in st.session_state.inventory[category]:
            qty = order_data.get(item["name"], 0)
            if qty > 0:
                amount = qty * item["price"]
                total_amount += amount
                items_to_sell.append(f"{item['name']} (x{qty})")

    # FOOTER: HIỂN THỊ TỔNG TIỀN VÀ NÚT XÁC NHẬN
    if items_to_sell:
        st.info(f"🛒 **Giỏ hàng:** {', '.join(items_to_sell)}")
    
    c_bottom1, c_bottom2 = st.columns([2, 1])
    with c_bottom1:
        st.markdown(f"### TỔNG CỘNG: <span style='color:red'>{total_amount:,.0f}đ</span>", unsafe_allow_html=True)
    with c_bottom2:
        if st.button("XÁC NHẬN & LƯU ĐƠN", type="primary", use_container_width=True):
            if total_amount > 0:
                st.success("Đã ghi nhận đơn hàng!")
                st.balloons()
            else:
                st.warning("Vui lòng nhập số lượng trước khi xác nhận.")

if __name__ == "__main__":
    main()
