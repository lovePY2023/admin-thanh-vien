import streamlit as st
import pandas as pd
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Thành Viễn ERP - Hệ Thống Tổng Hợp",
    page_icon="🏢",
    layout="wide"
)

# --- CSS TÙY CHỈNH (Navbar & Giao diện) ---
st.markdown("""
<style>
    /* Style cho các label nhập nhanh */
    .label-mb { background-color: #c6d9f1; padding: 10px; border: 1px solid #95b3d7; font-weight: bold; border-radius: 4px 0 0 4px; }
    .label-vt { background-color: #f2dcda; padding: 10px; border: 1px solid #e6b8b7; font-weight: bold; border-radius: 4px 0 0 4px; }
    .label-dl { background-color: #e2efda; padding: 10px; border: 1px solid #c6e0b4; font-weight: bold; border-radius: 4px 0 0 4px; }
    .stock-val { background-color: #ffffff; padding: 10px; border: 1px solid #ccc; text-align: center; font-family: monospace; }
    
    /* Section Headers */
    .section-header {
        padding: 10px; background: #333; color: white; border-radius: 5px; margin-bottom: 15px; font-weight: bold;
    }
    
    /* Loại bỏ padding mặc định của Streamlit để Navbar sát trần */
    .main .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU GIẢ LẬP ---
if 'db_inventory' not in st.session_state:
    st.session_state.db_inventory = [
        {"name": "MB 20K", "stock": 100, "price": 20000, "cat": "Viễn Thông"},
        {"name": "VT 20K", "stock": 85, "price": 20000, "cat": "Viễn Thông"},
        {"name": "Vệ sinh Máy lạnh", "stock": 999, "price": 150000, "cat": "Điện Lạnh"},
    ]

if 'db_history' not in st.session_state:
    st.session_state.db_history = [] # Lưu nhật ký giao dịch

# --- CÁC HÀM GIAO DIỆN PHÂN HỆ ---

def page_ban_hang():
    st.markdown('<div class="section-header">🛒 PHÂN HỆ BÁN HÀNG (POS)</div>', unsafe_allow_html=True)
    
    # Form khách hàng
    with st.expander("👤 Thông tin khách hàng", expanded=True):
        c1, c2, c3 = st.columns([2, 1, 1])
        cust_name = c1.text_input("Tên khách hàng")
        cust_phone = c2.text_input("Số điện thoại")
        cust_area = c3.selectbox("Khu vực", ["Quận 1", "Quận 3", "Bình Thạnh", "Gò Vấp"])

    # Nhập nhanh
    st.write("---")
    order_items = {}
    col_l, col_r = st.columns(2)
    
    # Giả lập nhập nhanh cho 2 món tiêu biểu
    with col_l:
        st.markdown('<div class="label-mb">MB 20K (Tồn: 100)</div>', unsafe_allow_html=True)
        qty_mb = st.number_input("Số lượng MB", min_value=0, step=1, key="sell_mb", label_visibility="collapsed")
        if qty_mb > 0: order_items["MB 20K"] = {"qty": qty_mb, "price": 20000}
        
    with col_r:
        st.markdown('<div class="label-vt">VT 20K (Tồn: 85)</div>', unsafe_allow_html=True)
        qty_vt = st.number_input("Số lượng VT", min_value=0, step=1, key="sell_vt", label_visibility="collapsed")
        if qty_vt > 0: order_items["VT 20K"] = {"qty": qty_vt, "price": 20000}

    # Tóm tắt & Lưu
    if order_items:
        st.divider()
        st.subheader("📋 Tóm tắt đơn hàng")
        total = sum(v['qty'] * v['price'] for v in order_items.values())
        st.write(pd.DataFrame([{"Món": k, "SL": v['qty'], "Thành tiền": v['qty']*v['price']} for k, v in order_items.items()]))
        st.markdown(f"### Tổng cộng: :red[{total:,.0f}đ]")
        if st.button("LƯU ĐƠN HÀNG"):
            st.success("Đã lưu đơn hàng!")

def page_nhap_hang():
    st.markdown('<div class="section-header">📦 PHÂN HỆ NHẬP HÀNG (KHO)</div>', unsafe_allow_html=True)
    with st.form("form_nhap"):
        c1, c2, c3 = st.columns(3)
        item = c1.selectbox("Chọn mặt hàng nhập", [x['name'] for x in st.session_state.db_inventory])
        qty = c2.number_input("Số lượng nhập", min_value=1)
        price = c3.number_input("Giá vốn nhập", min_value=0)
        provider = st.text_input("Nhà cung cấp")
        if st.form_submit_button("XÁC NHẬN NHẬP KHO"):
            st.info(f"Đã nhập {qty} {item} vào kho.")

def page_thu_chi():
    st.markdown('<div class="section-header">💰 PHÂN HỆ QUẢN LÝ THU CHI</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("🔴 Phiếu Chi")
        st.text_input("Lý do chi (Tiền điện, nước, mặt bằng...)")
        st.number_input("Số tiền chi", min_value=0, key="chi_val")
        st.button("Lưu Phiếu Chi", type="primary")
    with c2:
        st.subheader("🟢 Phiếu Thu")
        st.text_input("Lý do thu (Thu nợ, thanh lý...)")
        st.number_input("Số tiền thu", min_value=0, key="thu_val")
        st.button("Lưu Phiếu Thu")

def page_nhat_ky():
    st.markdown('<div class="section-header">📓 NHẬT KÝ CHỨNG TỪ</div>', unsafe_allow_html=True)
    st.write("Tra cứu toàn bộ lịch sử giao dịch bán hàng, nhập hàng, thu chi.")
    # Giả lập bảng nhật ký
    df_log = pd.DataFrame([
        {"Ngày": "2024-03-20", "Loại": "Bán Hàng", "Nội dung": "Bán thẻ MB cho Khách A", "Số tiền": 500000, "Trạng thái": "Hoàn tất"},
        {"Ngày": "2024-03-21", "Loại": "Chi Phí", "Nội dung": "Thanh toán tiền điện", "Số tiền": -1200000, "Trạng thái": "Đã chi"},
    ])
    st.dataframe(df_log, use_container_width=True)

def page_bao_cao():
    st.markdown('<div class="section-header">📊 BÁO CÁO TỔNG HỢP & MISA</div>', unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    col1.metric("Doanh thu tháng", "150.000.000đ", "+10%")
    col2.metric("Lợi nhuận gộp", "45.000.000đ", "+5%")
    col3.metric("Số dư quỹ", "22.500.000đ")
    
    st.divider()
    st.subheader("📤 Kết xuất dữ liệu")
    st.button("XUẤT FILE EXCEL MISA (XML/XLSX)")

# --- ĐIỀU HƯỚNG CHÍNH (NAVBAR) ---
def main():
    # Sidebar làm Menu điều hướng (Navbar dọc)
    with st.sidebar:
        st.image("https://via.placeholder.com/150x50?text=THANH+VIEN+ERP", use_container_width=True)
        st.title("MENU CHÍNH")
        choice = st.radio(
            "Chọn chức năng:",
            ["🛒 Bán Hàng", "📦 Nhập Hàng", "💰 Thu Chi", "📓 Nhật Ký", "📊 Báo Cáo"]
        )
        st.write("---")
        st.caption("Phiên bản v2.0 - Thành Viễn")

    # Hiển thị trang tương ứng
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
