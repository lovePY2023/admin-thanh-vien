import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Thành Viễn ERP - Hệ Thống Tổng Hợp",
    page_icon="🏢",
    layout="wide"
)

# --- CSS TÙY CHỈNH (Giữ lại phong cách Excel trực quan) ---
st.markdown("""
<style>
    /* Style cho các label nhập nhanh */
    .label-mb { background-color: #c6d9f1; padding: 10px; border: 1px solid #95b3d7; font-weight: bold; border-radius: 4px 0 0 4px; height: 45px; display: flex; align-items: center; }
    .label-vt { background-color: #f2dcda; padding: 10px; border: 1px solid #e6b8b7; font-weight: bold; border-radius: 4px 0 0 4px; height: 45px; display: flex; align-items: center; }
    .label-dl { background-color: #e2efda; padding: 10px; border: 1px solid #c6e0b4; font-weight: bold; border-radius: 4px 0 0 4px; height: 45px; display: flex; align-items: center; }
    .stock-val { background-color: #ffffff; padding: 10px; border: 1px solid #ccc; text-align: center; font-family: monospace; height: 45px; display: flex; align-items: center; justify-content: center; }
    
    /* Căn chỉnh lại input number để khớp với label */
    div[data-baseweb="input"] { height: 45px !important; }
    
    /* Section Headers */
    .section-header {
        padding: 10px; background: #333; color: white; border-radius: 5px; margin-bottom: 15px; font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU ---
if 'db_inventory' not in st.session_state:
    st.session_state.db_inventory = {
        "MB": [
            {"name": "MB 20K", "stock": 110, "price": 20000},
            {"name": "MB 50K", "stock": 104, "price": 50000},
            {"name": "MB 100K", "stock": 113, "price": 100000},
        ],
        "VT": [
            {"name": "VT 20K", "stock": 90, "price": 20000},
            {"name": "VT 50K", "stock": 97, "price": 50000},
            {"name": "VT 100K", "stock": 103, "price": 100000},
        ],
        "DL": [
            {"name": "Vệ sinh Máy lạnh", "stock": "∞", "price": 150000, "unit": "Bộ"},
            {"name": "Ống đồng Phi 6/10", "stock": 150, "price": 160000, "unit": "Mét"},
        ]
    }

# --- CÁC PHÂN HỆ CHỨC NĂNG ---

def page_ban_hang():
    st.markdown('<div class="section-header">🛒 PHÂN HỆ BÁN HÀNG (QUICK POS)</div>', unsafe_allow_html=True)
    
    # 1. Thông tin khách hàng
    with st.container(border=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        cust_name = c1.text_input("Tên khách hàng / Đơn vị", placeholder="Nhập tên khách hàng...")
        cust_phone = c2.text_input("Số điện thoại", placeholder="090x...")
        cust_area = c3.selectbox("Khu vực", ["Quận 1", "Quận 3", "Bình Thạnh", "Gò Vấp", "Khác"])
        
        c4, c5, c6 = st.columns([2, 1, 1])
        cust_addr = c4.text_input("Địa chỉ chi tiết")
        order_date = c5.date_input("Ngày chứng từ", datetime.now())
        sale_mode = c6.radio("CHẾ ĐỘ NHẬP", ["Viễn Thông", "Điện Lạnh"], horizontal=True)

    st.write("")
    order_items = {}

    # 2. Lưới nhập liệu (Grid)
    if sale_mode == "Viễn Thông":
        col_l, col_r = st.columns(2)
        with col_l:
            st.subheader("🟦 MOBIFONE")
            for i, item in enumerate(st.session_state.db_inventory["MB"]):
                c_lbl, c_stk, c_in = st.columns([3, 1.2, 2.5])
                c_lbl.markdown(f'<div class="label-mb">{item["name"]}</div>', unsafe_allow_html=True)
                c_stk.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
                qty = c_in.number_input("", min_value=0, step=1, key=f"mb_{i}", label_visibility="collapsed")
                if qty > 0: order_items[item["name"]] = {"qty": qty, "price": item["price"], "unit": "Thẻ"}
        
        with col_r:
            st.subheader("🟥 VIETTEL")
            for i, item in enumerate(st.session_state.db_inventory["VT"]):
                c_lbl, c_stk, c_in = st.columns([3, 1.2, 2.5])
                c_lbl.markdown(f'<div class="label-vt">{item["name"]}</div>', unsafe_allow_html=True)
                c_stk.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
                qty = c_in.number_input("", min_value=0, step=1, key=f"vt_{i}", label_visibility="collapsed")
                if qty > 0: order_items[item["name"]] = {"qty": qty, "price": item["price"], "unit": "Thẻ"}

    else:
        st.subheader("❄️ DỊCH VỤ & VẬT TƯ ĐIỆN LẠNH")
        for i, item in enumerate(st.session_state.db_inventory["DL"]):
            c_lbl, c_stk, c_in = st.columns([4, 1.2, 3])
            c_lbl.markdown(f'<div class="label-dl">{item["name"]}</div>', unsafe_allow_html=True)
            c_stk.markdown(f'<div class="stock-val">{item["stock"]}</div>', unsafe_allow_html=True)
            qty = c_in.number_input("", min_value=0, step=1, key=f"dl_{i}", label_visibility="collapsed")
            if qty > 0: order_items[item["name"]] = {"qty": qty, "price": item["price"], "unit": item.get("unit", "Cái")}

    # 3. Tóm tắt đơn hàng (Frame Data)
    if order_items:
        st.divider()
        st.subheader("📋 Tóm tắt đơn hàng")
        if cust_name:
            st.info(f"Khách hàng: **{cust_name}** - SĐT: **{cust_phone}**")
        
        summary_list = []
        total_all = 0
        for name, info in order_items.items():
            subtotal = info['qty'] * info['price']
            total_all += subtotal
            summary_list.append({
                "Mặt hàng": name,
                "Số lượng": info['qty'],
                "Đơn giá": f"{info['price']:,}đ",
                "Thành tiền": f"{subtotal:,}đ"
            })
        
        st.table(pd.DataFrame(summary_list))
        
        col_btn1, col_btn2 = st.columns([2, 1])
        col_btn1.markdown(f"### TỔNG CỘNG: :red[{total_all:,.0f} VNĐ]")
        if col_btn2.button("XÁC NHẬN & XUẤT HÓA ĐƠN", type="primary", use_container_width=True):
            st.success("Đã ghi nhận đơn hàng thành công!")
            st.balloons()

def page_nhap_hang():
    st.markdown('<div class="section-header">📦 NHẬP HÀNG VÀO KHO</div>', unsafe_allow_html=True)
    st.info("Chức năng cập nhật tồn kho từ nhà cung cấp.")

def page_thu_chi():
    st.markdown('<div class="section-header">💰 QUẢN LÝ THU CHI NỘI BỘ</div>', unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔴 Phiếu Chi", "🟢 Phiếu Thu"])
    with tab1:
        st.number_input("Số tiền chi", min_value=0)
        st.text_area("Lý do chi")
        st.button("Lưu phiếu chi")

def page_nhat_ky():
    st.markdown('<div class="section-header">📓 NHẬT KÝ GIAO DỊCH</div>', unsafe_allow_html=True)
    st.write("Lịch sử bán hàng và biến động kho.")

def page_bao_cao():
    st.markdown('<div class="section-header">📊 BÁO CÁO DOANH THU & KẾ TOÁN</div>', unsafe_allow_html=True)
    st.button("Xuất Excel MISA")

# --- ĐIỀU HƯỚNG NAVBAR SIDEBAR ---
def main():
    with st.sidebar:
        st.title("❄️ THÀNH VIỄN")
        choice = st.radio(
            "DANH MỤC CHÍNH",
            ["🛒 Bán Hàng", "📦 Nhập Hàng", "💰 Thu Chi", "📓 Nhật Ký", "📊 Báo Cáo"],
            index=0
        )
        st.divider()
        st.caption("User: Admin | POS-01")

    if choice == "🛒 Bán Hàng":
        page_ban_hang()
    elif choice == "📦 Nhập Hàng":
        page_nhap_hang()
    elif choice == "💰 Thu Chi":
        page_thu_chi()
    elif choice == "📓 Nhật Ký":
        page_nhat_ky()
    elif choice == "📊 Báo Cáo":
        page_bao_cao()

if __name__ == "__main__":
    main()
