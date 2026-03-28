import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Quản Lý Thành Viễn", layout="wide")

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E88E5; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    div[data-testid="stExpander"] { border: 1px solid #e6e6e6; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU (SESSION STATE - BẢN NHÁP) ---
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"id": "P001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "stock": 10, "cost": 6500000, "price": 8500000, "category": "Hàng Hóa"},
        {"id": "P002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "stock": 100, "cost": 90000, "price": 150000, "category": "Vật Tư"},
        {"id": "S001", "name": "Vệ Sinh Máy Lạnh", "unit": "Lần", "stock": 999, "cost": 50000, "price": 200000, "category": "Dịch Vụ"}
    ])

if 'orders' not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=[
        "Thời Gian", "Khách Hàng", "Sản Phẩm", "Số Lượng", "Đơn Giá", "Tổng Tiền", "Loại"
    ])

if 'journal_logs' not in st.session_state:
    # Nhật ký ghi lại mọi biến động (Bán hàng, Nhập kho)
    st.session_state.journal_logs = pd.DataFrame(columns=[
        "Thời Gian", "Loại Giao Dịch", "Chi Tiết", "Giá Trị", "Người Thực Hiện"
    ])

# --- HÀM GHI NHẬT KÝ ---
def log_event(event_type, detail, value, user="Admin"):
    new_log = {
        "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Loại Giao Dịch": event_type,
        "Chi Tiết": detail,
        "Giá Trị": value,
        "Người Thực Hiện": user
    }
    st.session_state.journal_logs = pd.concat([pd.DataFrame([new_log]), st.session_state.journal_logs], ignore_index=True)

# --- THANH MENU BÊN TRÁI ---
with st.sidebar:
    st.title("❄️ Thành Viễn ERP")
    menu = st.radio("Chức năng chính", [
        "🛒 Bán Hàng & Dịch Vụ", 
        "📦 Quản Lý Kho", 
        "📓 Nhật Ký Hệ Thống",
        "📊 Báo Cáo Doanh Thu"
    ])
    st.divider()
    st.caption("Dữ liệu hiện tại là bản nháp (Session State)")

# --- 1. PHÂN HỆ BÁN HÀNG ---
if menu == "🛒 Bán Hàng & Dịch Vụ":
    st.markdown('<p class="main-header">🛒 Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.5])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Tạo Đơn Hàng")
            cust = st.text_input("Tên khách hàng", placeholder="Anh A, Chị B...")
            
            item_name = st.selectbox("Chọn Sản phẩm / Dịch vụ", st.session_state.products['name'])
            item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
            
            q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
            p = st.number_input("Đơn giá bán (VNĐ)", value=int(item_info['price']), step=10000)
            
            total_amount = q * p
            st.markdown(f"### Tổng: :blue[{total_amount:,.0f} VNĐ]")
            
            if st.button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                if item_info['category'] != "Dịch Vụ" and item_info['stock'] < q:
                    st.error(f"Không đủ hàng! Kho hiện còn: {item_info['stock']}")
                else:
                    # 1. Trừ kho
                    if item_info['category'] != "Dịch Vụ":
                        idx = st.session_state.products[st.session_state.products['name'] == item_name].index[0]
                        st.session_state.products.at[idx, 'stock'] -= q
                    
                    # 2. Lưu đơn hàng
                    new_order = {
                        "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Khách Hàng": cust if cust else "Khách vãng lai",
                        "Sản Phẩm": item_name,
                        "Số Lượng": q,
                        "Đơn Giá": p,
                        "Tổng Tiền": total_amount,
                        "Loại": item_info['category']
                    }
                    st.session_state.orders = pd.concat([pd.DataFrame([new_order]), st.session_state.orders], ignore_index=True)
                    
                    # 3. Ghi Nhật ký
                    log_event("BÁN HÀNG", f"Bán {item_name} cho {cust}", total_amount)
                    
                    st.success("Đã chốt đơn thành công!")
                    st.rerun()

    with col_view:
        st.subheader("Giao dịch gần đây")
        st.dataframe(st.session_state.orders.head(10), use_container_width=True, hide_index=True)

# --- 2. PHÂN HỆ QUẢN LÝ KHO ---
elif menu == "📦 Quản Lý Kho":
    st.markdown('<p class="main-header">📦 Quản Lý Tồn Kho</p>', unsafe_allow_html=True)
    
    t_stock, t_add = st.tabs(["📋 Danh sách tồn kho", "➕ Nhập hàng / Thêm mới"])
    
    with t_stock:
        search = st.text_input("🔍 Tìm kiếm sản phẩm...", "")
        df_stock = st.session_state.products.copy()
        if search:
            df_stock = df_stock[df_stock['name'].str.contains(search, case=False)]
        st.dataframe(df_stock, use_container_width=True, hide_index=True)
        
    with t_add:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Thêm Sản Phẩm Mới")
            with st.form("new_product"):
                new_id = st.text_input("Mã SP")
                new_name = st.text_input("Tên sản phẩm")
                new_unit = st.selectbox("Đơn vị", ["Cái", "Bộ", "Mét", "Lần", "Kg"])
                new_cat = st.selectbox("Phân loại", ["Hàng Hóa", "Vật Tư", "Dịch Vụ"])
                new_cost = st.number_input("Giá vốn", min_value=0)
                new_price = st.number_input("Giá bán", min_value=0)
                new_stock = st.number_input("Tồn đầu kỳ", min_value=0)
                
                if st.form_submit_button("Lưu sản phẩm"):
                    new_p = {"id": new_id, "name": new_name, "unit": new_unit, "stock": new_stock, "cost": new_cost, "price": new_price, "category": new_cat}
                    st.session_state.products = pd.concat([st.session_state.products, pd.DataFrame([new_p])], ignore_index=True)
                    log_event("DANH MỤC", f"Thêm sản phẩm mới: {new_name}", 0)
                    st.success("Đã thêm sản phẩm!")
                    st.rerun()
        
        with col_b:
            st.subheader("Nhập Thêm Hàng")
            with st.form("add_stock"):
                p_select = st.selectbox("Sản phẩm", st.session_state.products[st.session_state.products['category'] != "Dịch Vụ"]['name'])
                q_add = st.number_input("Số lượng nhập", min_value=1)
                cost_in = st.number_input("Giá nhập thực tế", min_value=0)
                if st.form_submit_button("Xác nhận nhập"):
                    idx = st.session_state.products[st.session_state.products['name'] == p_select].index[0]
                    st.session_state.products.at[idx, 'stock'] += q_add
                    log_event("NHẬP KHO", f"Nhập thêm {q_add} {p_select}", q_add * cost_in)
                    st.success(f"Đã nhập kho {p_select}")
                    st.rerun()

# --- 3. PHÂN HỆ NHẬT KÝ ---
elif menu == "📓 Nhật Ký Hệ Thống":
    st.markdown('<p class="main-header">📓 Nhật Ký Giao Dịch & Biến Động</p>', unsafe_allow_html=True)
    st.write("Dưới đây là lịch sử ghi lại toàn bộ hoạt động của hệ thống (Bán hàng, nhập kho, chỉnh sửa danh mục).")
    
    if not st.session_state.journal_logs.empty:
        st.dataframe(st.session_state.journal_logs, use_container_width=True, hide_index=True)
        
        # Nút xóa nhật ký (Chỉ dùng cho bản nháp)
        if st.button("Xóa trắng nhật ký"):
            st.session_state.journal_logs = st.session_state.journal_logs.iloc[0:0]
            st.rerun()
    else:
        st.info("Chưa có ghi chép nào trong nhật ký.")

# --- 4. PHÂN HỆ BÁO CÁO ---
elif menu == "📊 Báo Cáo Doanh Thu":
    st.markdown('<p class="main-header">📊 Báo Cáo Kinh Doanh</p>', unsafe_allow_html=True)
    
    if not st.session_state.orders.empty:
        df_o = st.session_state.orders
        total_sales = df_o['Tổng Tiền'].sum()
        
        c1, c2 = st.columns(2)
        c1.metric("Tổng Doanh Thu", f"{total_sales:,.0f} VNĐ")
        c2.metric("Tổng Số Đơn Hàng", len(df_o))
        
        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            fig_bar = px.bar(df_o, x="Loại", y="Tổng Tiền", color="Loại", title="Doanh thu theo nhóm")
            st.plotly_chart(fig_bar, use_container_width=True)
        with col_chart2:
            fig_pie = px.pie(df_o, values='Tổng Tiền', names='Sản Phẩm', hole=0.4, title="Tỷ trọng sản phẩm")
            st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.warning("Chưa có dữ liệu đơn hàng.")

st.divider()
st.caption("Thành Viễn Admin - Giao diện thử nghiệm vận hành")
