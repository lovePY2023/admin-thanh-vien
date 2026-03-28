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

# --- KHỞI TẠO DỮ LIỆU (SESSION STATE) ---
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

# --- THANH MENU BÊN TRÁI ---
with st.sidebar:
    st.title("❄️ Thành Viễn ERP")
    menu = st.radio("Chức năng chính", ["🛒 Bán Hàng & Dịch Vụ", "📦 Quản Lý Kho", "📊 Báo Cáo Doanh Thu"])
    st.divider()
    st.caption("Giai đoạn: Vận hành & Kho")

# --- 1. PHÂN HỆ BÁN HÀNG ---
if menu == "🛒 Bán Hàng & Dịch Vụ":
    st.markdown('<p class="main-header">🛒 Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.5])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Tạo Đơn Hàng")
            cust = st.text_input("Tên khách hàng", placeholder="Anh A, Chị B...")
            
            # Lọc danh mục sản phẩm/dịch vụ
            item_name = st.selectbox("Chọn Sản phẩm / Dịch vụ", st.session_state.products['name'])
            item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
            
            q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
            p = st.number_input("Đơn giá bán (VNĐ)", value=int(item_info['price']), step=10000)
            
            total_amount = q * p
            st.markdown(f"### Tổng: :blue[{total_amount:,.0f} VNĐ]")
            
            if st.button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                # Kiểm tra tồn kho trước khi bán (nếu không phải dịch vụ)
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
                    st.success("Đã chốt đơn thành công!")
                    st.rerun()

    with col_view:
        st.subheader("Giao dịch vừa thực hiện")
        if not st.session_state.orders.empty:
            st.dataframe(st.session_state.orders.head(10), use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có đơn hàng nào trong phiên này.")

# --- 2. PHÂN HỆ QUẢN LÝ KHO ---
elif menu == "📦 Quản Lý Kho":
    st.markdown('<p class="main-header">📦 Quản Lý Tồn Kho</p>', unsafe_allow_html=True)
    
    t_stock, t_add = st.tabs(["📋 Danh sách tồn kho", "➕ Nhập hàng / Thêm mới"])
    
    with t_stock:
        # Tìm kiếm sản phẩm
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
                new_id = st.text_input("Mã SP (Ví dụ: P003)")
                new_name = st.text_input("Tên sản phẩm")
                new_unit = st.selectbox("Đơn vị", ["Cái", "Bộ", "Mét", "Lần", "Kg"])
                new_cat = st.selectbox("Phân loại", ["Hàng Hóa", "Vật Tư", "Dịch Vụ"])
                new_cost = st.number_input("Giá vốn nhập", min_value=0)
                new_price = st.number_input("Giá bán niêm yết", min_value=0)
                new_stock = st.number_input("Tồn kho ban đầu", min_value=0)
                
                if st.form_submit_button("Lưu sản phẩm"):
                    new_p = {
                        "id": new_id, "name": new_name, "unit": new_unit,
                        "stock": new_stock, "cost": new_cost, "price": new_price, "category": new_cat
                    }
                    st.session_state.products = pd.concat([st.session_state.products, pd.DataFrame([new_p])], ignore_index=True)
                    st.success("Đã thêm sản phẩm mới!")
                    st.rerun()
        
        with col_b:
            st.subheader("Nhập Thêm Hàng (Tăng kho)")
            with st.form("add_stock"):
                p_select = st.selectbox("Sản phẩm sẵn có", st.session_state.products[st.session_state.products['category'] != "Dịch Vụ"]['name'])
                q_add = st.number_input("Số lượng nhập thêm", min_value=1)
                if st.form_submit_button("Xác nhận nhập"):
                    idx = st.session_state.products[st.session_state.products['name'] == p_select].index[0]
                    st.session_state.products.at[idx, 'stock'] += q_add
                    st.success(f"Đã cập nhật tồn kho cho {p_select}")
                    st.rerun()

# --- 3. PHÂN HỆ BÁO CÁO ---
elif menu == "📊 Báo Cáo Doanh Thu":
    st.markdown('<p class="main-header">📊 Báo Cáo Kinh Doanh</p>', unsafe_allow_html=True)
    
    if not st.session_state.orders.empty:
        df_o = st.session_state.orders
        
        # Chỉ số tổng quát
        total_sales = df_o['Tổng Tiền'].sum()
        total_orders = len(df_o)
        
        c1, c2 = st.columns(2)
        c1.metric("Tổng Doanh Thu", f"{total_sales:,.0f} VNĐ")
        c2.metric("Tổng Số Đơn Hàng", total_orders)
        
        st.divider()
        
        col_chart1, col_chart2 = st.columns(2)
        
        with col_chart1:
            st.subheader("Doanh thu theo nhóm hàng")
            fig_bar = px.bar(df_o, x="Loại", y="Tổng Tiền", color="Loại", 
                             text_auto='.2s',
                             color_discrete_sequence=px.colors.qualitative.Pastel)
            st.plotly_chart(fig_bar, use_container_width=True)
            
        with col_chart2:
            st.subheader("Cơ cấu sản phẩm bán ra")
            fig_pie = px.pie(df_o, values='Tổng Tiền', names='Sản Phẩm', hole=0.4)
            st.plotly_chart(fig_pie, use_container_width=True)
        
        st.subheader("Chi tiết lịch sử bán hàng")
        st.dataframe(df_o, use_container_width=True, hide_index=True)
    else:
        st.warning("Chưa có dữ liệu đơn hàng để báo cáo.")

st.divider()
st.caption("MiniERP v1.2 - Tập trung vận hành Bán hàng & Kho")
