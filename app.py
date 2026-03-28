import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Thành Viễn ERP - Nhập Nhanh Multi-POS",
    page_icon="⚡",
    layout="wide"
)

# --- CSS TÙY CHỈNH GIỐNG MẪU EXCEL ---
st.markdown("""
<style>
    .label-mb {
        background-color: #c6d9f1; padding: 10px; border: 1px solid #95b3d7;
        font-weight: bold; text-align: left; border-radius: 4px 0 0 4px;
    }
    .label-vt {
        background-color: #f2dcda; padding: 10px; border: 1px solid #e6b8b7;
        font-weight: bold; text-align: left; border-radius: 4px 0 0 4px;
    }
    .label-dien-lanh {
        background-color: #e2efda; padding: 10px; border: 1px solid #c6e0b4;
        font-weight: bold; text-align: left; border-radius: 4px 0 0 4px;
    }
    .stock-val {
        background-color: #ffffff; padding: 10px; border: 1px solid #ccc;
        text-align: center; font-family: monospace;
    }
    div[data-baseweb="input"] {
        border-radius: 0 4px 4px 0 !important;
    }
    .section-header {
        padding: 10px;
        background: #333;
        color: white;
        border-radius: 5px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU ---
def init_data():
    if 'inv_telecom' not in st.session_state:
        st.session_state.inv_telecom = {
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
    
    if 'inv_cooling' not in st.session_state:
        st.session_state.inv_cooling = [
            {"name": "Vệ sinh Máy lạnh (Bộ)", "stock": "∞", "price": 150000, "unit": "Bộ"},
            {"name": "Lắp máy mới (Công)", "stock": "∞", "price": 350000, "unit": "Bộ"},
            {"name": "Ống đồng Phi 6/10", "stock": 150, "price": 160000, "unit": "Mét"},
            {"name": "Gas R32 (Sạc bổ sung)", "stock": 20, "price": 250000, "unit": "Lần"},
            {"name": "Gas R410A (Trọn gói)", "stock": 15, "price": 450000, "unit": "Bình"},
            {"name": "Thay Tụ quạt/Block", "stock": 30, "price": 180000, "unit": "Cái"},
        ]

init_data()

def main():
    st.title("⚡ Nhập Đơn Hàng Thành Viễn")
    
    # Thông tin khách hàng & Chế độ
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        customer = c1.selectbox("Chọn Khách Hàng", ["Khách lẻ", "Đại lý Thành Viễn", "Cửa hàng vật tư X"])
        date = c2.date_input("Ngày chứng từ", datetime.now())
        mode = c3.radio("PHÂN HỆ BÁN HÀNG", ["Viễn Thông", "Điện Lạnh"], horizontal=True)

    order_items = {} 

    if mode == "Viễn Thông":
        st.markdown('<div class="section-header">📶 PHÂN HỆ VIỄN THÔNG (THẺ CÀO)</div>', unsafe_allow_html=True)
        col_left, col_right = st.columns(2)
        
        with col_left:
            st.subheader("🟦 MOBIFONE")
            for i, item in enumerate(st.session_state.inv_telecom["MB"]):
                c_lbl, c_stk, c_in = st.columns([3, 1.5, 3])
                c_lbl.markdown(f'<div class="label-mb">{item["name"]}</div>', unsafe_allow_html=True)
                c_stk.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
                qty = c_in.number_input("", min_value=0, step=1, key=f"mb_{i}", label_visibility="collapsed")
                order_items[item["name"]] = {"qty": qty, "price": item["price"], "unit": "Thẻ"}

        with col_right:
            st.subheader("🟥 VIETTEL")
            for i, item in enumerate(st.session_state.inv_telecom["VT"]):
                c_lbl, c_stk, c_in = st.columns([3, 1.5, 3])
                c_lbl.markdown(f'<div class="label-vt">{item["name"]}</div>', unsafe_allow_html=True)
                c_stk.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
                qty = c_in.number_input("", min_value=0, step=1, key=f"vt_{i}", label_visibility="collapsed")
                order_items[item["name"]] = {"qty": qty, "price": item["price"], "unit": "Thẻ"}

    else: # Điện Lạnh
        st.markdown('<div class="section-header">❄️ PHÂN HỆ DỊCH VỤ & VẬT TƯ ĐIỆN LẠNH</div>', unsafe_allow_html=True)
        mid = len(st.session_state.inv_cooling) // 2
        col_l, col_r = st.columns(2)
        
        for i, item in enumerate(st.session_state.inv_cooling):
            target_col = col_l if i < mid else col_r
            with target_col:
                c_lbl, c_stk, c_in = st.columns([4, 1.5, 3])
                c_lbl.markdown(f'<div class="label-dien-lanh">{item["name"]}</div>', unsafe_allow_html=True)
                c_stk.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
                qty = c_in.number_input("", min_value=0, step=1, key=f"dl_{i}", label_visibility="collapsed")
                order_items[item["name"]] = {"qty": qty, "price": item["price"], "unit": item["unit"]}

    st.divider()

    # XỬ LÝ DỮ LIỆU TÓM TẮT ĐƠN HÀNG
    summary_data = []
    total_bill = 0
    for name, info in order_items.items():
        if info["qty"] > 0:
            subtotal = info["qty"] * info["price"]
            total_bill += subtotal
            summary_data.append({
                "Mặt hàng": name,
                "Số lượng": info["qty"],
                "Đơn vị": info["unit"],
                "Đơn giá": info["price"],
                "Thành tiền": subtotal
            })

    # HIỂN THỊ FRAME TÓM TẮT
    st.subheader("📋 Tóm tắt đơn hàng")
    if summary_data:
        df_summary = pd.DataFrame(summary_data)
        # Định dạng tiền tệ cho bảng
        df_display = df_summary.copy()
        df_display['Đơn giá'] = df_display['Đơn giá'].map('{:,.0f}đ'.format)
        df_display['Thành tiền'] = df_display['Thành tiền'].map('{:,.0f}đ'.format)
        
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        c_f1, c_f2 = st.columns([2, 1])
        c_f1.markdown(f"### TỔNG CỘNG: <span style='color:red'>{total_bill:,.0f} VNĐ</span>", unsafe_allow_html=True)
        if c_f2.button("XÁC NHẬN & LƯU HÓA ĐƠN", type="primary", use_container_width=True):
            st.success("Đã ghi nhận giao dịch thành công!")
            st.balloons()
    else:
        st.write("*(Chưa có mặt hàng nào được chọn)*")

if __name__ == "__main__":
    main()
