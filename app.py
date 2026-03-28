import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import io

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(
    page_title="Thành Viễn ERP - Tất Cả Trong Một",
    page_icon="❄️",
    layout="wide"
)

# --- GIẢ LẬP DỮ LIỆU TỪ SUPABASE ---
# (Sẽ được thay thế bằng kết nối Supabase thực tế khi bạn cung cấp URL/Key)
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"barcode": "893001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "price": 8500000, "stock": 10},
        {"barcode": "893002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "price": 150000, "stock": 100},
    ])

if 'journal' not in st.session_state:
    st.session_state.journal = pd.DataFrame([
        {"time": "2024-03-28 08:30", "type": "XUẤT (Mobile)", "item": "Máy Lạnh Inverter 1HP", "qty": 1, "total": 8500000, "user": "NV_Kho_Tuan", "note": "Quét mã kệ tầng 3"},
        {"time": "2024-03-28 09:15", "type": "NHẬP (PC)", "item": "Ống Đồng Phi 6/10", "qty": 50, "total": 0, "user": "KeToan_Lan", "note": "Nhập kho theo lô"},
    ])

# --- GIAO DIỆN CHÍNH ---
def main():
    # Sidebar: Chế độ làm việc
    st.sidebar.markdown("### 🛠️ THÀNH VIỄN ERP")
    app_mode = st.sidebar.selectbox("CHẾ ĐỘ LÀM VIỆC", ["📱 QUÉT MÃ NHANH (Mobile)", "🖥️ QUẢN LÝ TỔNG THỂ (PC)"])
    
    if app_mode == "📱 QUÉT MÃ NHANH (Mobile)":
        render_mobile_mode()
    else:
        render_pc_mode()

# --- PHÂN HỆ MOBILE (Tích hợp trong cùng App) ---
def render_mobile_mode():
    st.header("📱 Chế độ Di động (Leo kệ / Quét mã)")
    st.info("Dùng camera điện thoại để quét mã vạch và cập nhật kho tức thì.")
    
    # Giả lập quét mã (Trên Streamlit có thể dùng widget Camera Input)
    img_file = st.camera_input("Quét mã vạch sản phẩm")
    
    if img_file:
        st.warning("Hệ thống đang phân tích ảnh... (Kết nối AI để đọc barcode)")
        # Logic đọc mã vạch sẽ nằm ở đây
        st.success("Đã tìm thấy: Máy Lạnh Inverter 1HP (Tồn: 10)")
        
    c1, c2 = st.columns(2)
    with c1:
        qty = st.number_input("Số lượng", min_value=1, value=1)
    with c2:
        action = st.radio("Thao tác", ["NHẬP KHO", "XUẤT KHO"])
        
    if st.button("XÁC NHẬN GỬI DỮ LIỆU", use_container_width=True, type="primary"):
        st.balloons()
        st.success(f"Đã {action} {qty} sản phẩm. Dữ liệu đã đẩy lên Supabase!")

# --- PHÂN HỆ PC (Quản lý chi tiết) ---
def render_pc_mode():
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

def render_dashboard():
    st.title("📊 Trung Tâm Giám Sát")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Tổng doanh thu", "125,000,000đ", "+8%")
    c2.metric("Giao dịch Mobile", f"{len(st.session_state.journal)} lượt", "Sôi nổi")
    c3.metric("Sản phẩm sắp hết", "2 mã", "-1", delta_color="inverse")
    c4.metric("Trạng thái Sync", "Supabase Online", "0.2s")

    st.divider()
    col_chart, col_logs = st.columns([2, 1])
    with col_chart:
        st.subheader("Biến động xuất nhập")
        df_chart = pd.DataFrame({'Ngày': pd.date_range(start='2024-03-20', periods=7), 'Nhập': [10, 20, 15, 30, 25, 40, 35], 'Xuất': [5, 15, 20, 25, 20, 30, 45]})
        st.line_chart(df_chart.set_index('Ngày'))

    with col_logs:
        st.subheader("Hoạt động mới nhất")
        for index, row in st.session_state.journal.iloc[::-1].head(5).iterrows():
            st.write(f"🕒 **{row['time'].split(' ')[1]}** | {row['user']}")
            st.caption(f"{row['type']}: {row['item']}")
            st.divider()

def render_order_entry():
    st.title("🛒 Lập Đơn Bán Hàng")
    with st.container(border=True):
        c1, c2 = st.columns(2)
        customer = c1.selectbox("Khách hàng", ["Công ty A", "Khách hàng B"])
        date = c2.date_input("Ngày lập")
        
        items_df = pd.DataFrame([{"Mặt hàng": "Máy Lạnh Inverter 1HP", "SL": 1, "Đơn giá": 8500000}])
        edited_df = st.data_editor(items_df, num_rows="dynamic", use_container_width=True)
        
        total = (edited_df['SL'] * edited_df['Đơn giá']).sum()
        st.subheader(f"Tổng: :blue[{total:,.0f} VNĐ]")
        if st.button("XUẤT HÓA ĐƠN", type="primary"):
            st.success("Đã ghi sổ thành công!")

def render_combined_journal():
    st.title("📒 Nhật Ký Hợp Nhất")
    st.dataframe(st.session_state.journal, use_container_width=True, hide_index=True)

def render_inventory_management():
    st.title("📦 Quản Lý Kho")
    st.data_editor(st.session_state.inventory, use_container_width=True)

if __name__ == "__main__":
    main()
