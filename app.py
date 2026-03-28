import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# --- CẤU HÌNH GIAO DIỆN RỘNG CHO PC ---
st.set_page_config(
    page_title="Thành Viễn ERP - Dashboard Trung Tâm",
    page_icon="🖥️",
    layout="wide"
)

# --- GIẢ LẬP DỮ LIỆU TỪ KHO CHUNG (SUPABASE) ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"barcode": "893001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "price": 8500000, "stock": 10},
        {"barcode": "893002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "price": 150000, "stock": 100},
    ])

if 'journal' not in st.session_state:
    # Dữ liệu này bao gồm cả các dòng quét mã từ Mobile đổ về
    st.session_state.journal = pd.DataFrame([
        {"time": "2024-03-28 08:30", "type": "XUẤT (Mobile)", "item": "Máy Lạnh Inverter 1HP", "qty": 1, "total": 8500000, "user": "NV_Kho_Tuan", "note": "Quét mã kệ tầng 3"},
        {"time": "2024-03-28 09:15", "type": "NHẬP (PC)", "item": "Ống Đồng Phi 6/10", "qty": 50, "total": 0, "user": "KeToan_Lan", "note": "Nhập kho theo lô"},
    ])

# --- GIAO DIỆN CHÍNH ---
def main():
    st.sidebar.markdown("### 🖥️ THÀNH VIỄN ERP")
    st.sidebar.info("Trạm điều hành dành cho PC/Laptop")
    
    menu = st.sidebar.radio("PHÂN HỆ QUẢN LÝ", [
        "📊 Dashboard Tổng Quan",
        "🛒 Bán Hàng & Đơn Hàng",
        "📦 Quản Lý Kho & Giá",
        "📒 Nhật Ký Toàn Hệ Thống",
        "📥 Kết Xuất MISA"
    ])

    if menu == "📊 Dashboard Tổng Quan":
        render_dashboard()
    elif menu == "🛒 Bán Hàng & Đơn Hàng":
        render_order_entry()
    elif menu == "📒 Nhật Ký Toàn Hệ Thống":
        render_combined_journal()
    elif menu == "📦 Quản Lý Kho & Giá":
        render_inventory_management()

# --- 1. DASHBOARD TỔNG QUAN ---
def render_dashboard():
    st.title("📊 Trung Tâm Giám Sát Real-time")
    
    # Chỉ số nhanh (KPIs)
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Tổng doanh thu", "125,000,000đ", "+8%")
    with c2:
        st.metric("Giao dịch Mobile", "15 lượt", "Sôi nổi")
    with c3:
        st.metric("Sản phẩm dưới hạn mức", "2 mã", "-1", delta_color="inverse")
    with c4:
        st.metric("Trạng thái Sync", "Đang kết nối", "Ổn định")

    st.divider()
    
    col_chart, col_logs = st.columns([2, 1])
    with col_chart:
        st.subheader("Biến động xuất nhập kho")
        # Giả lập biểu đồ trực quan
        df_chart = pd.DataFrame({
            'Ngày': pd.date_range(start='2024-03-20', periods=7),
            'Nhập': [10, 20, 15, 30, 25, 40, 35],
            'Xuất': [5, 15, 20, 25, 20, 30, 45]
        })
        st.line_chart(df_chart.set_index('Ngày'))

    with col_logs:
        st.subheader("Hoạt động mới nhất")
        for index, row in st.session_state.journal.iloc[::-1].head(5).iterrows():
            st.write(f"🕒 **{row['time'].split(' ')[1]}** | {row['user']}")
            st.caption(f"{row['type']}: {row['item']} ({row['qty']})")
            st.divider()

# --- 2. NHẬP ĐƠN HÀNG CHI TIẾT ---
def render_order_entry():
    st.title("🛒 Lập Đơn Bán Hàng (PC Mode)")
    st.info("Sử dụng khi có đơn hàng nhiều món hoặc cần làm hóa đơn chuyên nghiệp.")
    
    with st.container(border=True):
        c1, c2 = st.columns(2)
        with c1:
            customer = st.selectbox("Khách hàng/Đại lý", ["Công ty A", "Khách hàng B", "Đại lý C"])
        with c2:
            order_date = st.date_input("Ngày xuất hóa đơn")
        
        # Bảng nhập liệu kiểu Excel
        items_df = pd.DataFrame([
            {"Mặt hàng": "Máy Lạnh Inverter 1HP", "SL": 1, "Đơn giá": 8500000},
            {"Mặt hàng": "Ống Đồng Phi 6/10", "SL": 10, "Đơn giá": 150000}
        ])
        
        st.write("Chi tiết đơn hàng:")
        edited_df = st.data_editor(items_df, num_rows="dynamic", use_container_width=True)
        
        total = (edited_df['SL'] * edited_df['Đơn giá']).sum()
        st.subheader(f"Tổng giá trị đơn: :blue[{total:,.0f} VNĐ]")
        
        if st.button("XUẤT HÓA ĐƠN & TRỪ KHO", type="primary"):
            st.success("Đã ghi nhận giao dịch và đồng bộ dữ liệu!")

# --- 3. NHẬT KÝ HỢP NHẤT ---
def render_combined_journal():
    st.title("📒 Sổ Nhật Ký Giao Dịch Hợp Nhất")
    st.markdown("""
    <style> .stDataFrame { border: 1px solid #ddd; border-radius: 10px; } </style>
    """, unsafe_allow_html=True)
    
    st.write("Nơi kiểm soát mọi hành động từ App Điện Thoại và Máy Tính.")
    
    # Bộ lọc chuyên sâu cho PC
    f1, f2, f3 = st.columns([1, 1, 2])
    with f1:
        st.selectbox("Lọc theo nguồn", ["Tất cả", "Mobile App", "PC Admin"])
    with f2:
        st.selectbox("Lọc theo loại", ["Tất cả", "NHẬP", "XUẤT"])
    with f3:
        st.text_input("Tìm kiếm theo tên sản phẩm hoặc ghi chú...")

    st.dataframe(st.session_state.journal, use_container_width=True, hide_index=True)

# --- 4. QUẢN LÝ KHO ---
def render_inventory_management():
    st.title("📦 Quản Lý Danh Mục & Kho Hàng")
    
    tab1, tab2 = st.tabs(["Sửa giá & Tồn kho", "Thiết lập vị trí kệ"])
    
    with tab1:
        st.data_editor(st.session_state.inventory, use_container_width=True)
        if st.button("Cập nhật bảng giá mới"):
            st.toast("Đã đồng bộ giá mới lên điện thoại của nhân viên!")

if __name__ == "__main__":
    main()
