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
    /* Giúp ô nhập mã nổi bật hơn */
    input[aria-label="Nhập hoặc Quét mã Barcode/QR"] {
        background-color: #fff9c4;
        border: 2px solid #fbc02d;
    }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU (SESSION STATE) ---
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"id": "P001", "barcode": "893001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "stock": 10, "cost": 6500000, "price": 8500000, "category": "Hàng Hóa"},
        {"id": "P002", "barcode": "893002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "stock": 100, "cost": 90000, "price": 150000, "category": "Vật Tư"},
        {"id": "S001", "barcode": "", "name": "Vệ Sinh Máy Lạnh", "unit": "Lần", "stock": 999, "cost": 50000, "price": 200000, "category": "Dịch Vụ"}
    ])

if 'orders' not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=[
        "Thời Gian", "Khách Hàng", "Sản Phẩm", "Số Lượng", "Đơn Giá", "Tổng Tiền", "Loại"
    ])

if 'journal_logs' not in st.session_state:
    st.session_state.journal_logs = pd.DataFrame(columns=[
        "Thời Gian", "Loại Giao Dịch", "Chi Tiết", "Giá Trị", "Người Thực Hiện"
    ])

# --- HÀM TRỢ GIÚP ---
def log_event(event_type, detail, value, user="Admin"):
    new_log = {
        "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Loại Giao Dịch": event_type,
        "Chi Tiết": detail,
        "Giá Trị": value,
        "Người Thực Hiện": user
    }
    st.session_state.journal_logs = pd.concat([pd.DataFrame([new_log]), st.session_state.journal_logs], ignore_index=True)

def find_product_by_barcode(code):
    if not code: return None
    result = st.session_state.products[st.session_state.products['barcode'] == code]
    return result.iloc[0] if not result.empty else None

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
    st.caption("Dữ liệu hiện tại là bản nháp")

# --- 1. PHÂN HỆ BÁN HÀNG ---
if menu == "🛒 Bán Hàng & Dịch Vụ":
    st.markdown('<p class="main-header">🛒 Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.5])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Tạo Đơn Hàng")
            
            # CHỨC NĂNG QUÉT MÃ
            scanned_code = st.text_input("🔍 Nhập hoặc Quét mã Barcode/QR", key="sale_barcode", help="Dùng máy quét hoặc nhập mã vạch tại đây")
            product_scanned = find_product_by_barcode(scanned_code)
            
            if product_scanned is not None:
                st.info(f"Đã nhận diện: **{product_scanned['name']}**")
                default_item = product_scanned['name']
            else:
                if scanned_code: st.warning("Không tìm thấy mã này trong kho!")
                default_item = st.session_state.products['name'].iloc[0]

            cust = st.text_input("Tên khách hàng", placeholder="Anh A, Chị B...")
            
            item_name = st.selectbox("Chọn Sản phẩm / Dịch vụ", st.session_state.products['name'], 
                                     index=list(st.session_state.products['name']).index(default_item))
            
            item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
            
            q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
            p = st.number_input("Đơn giá bán (VNĐ)", value=int(item_info['price']), step=10000)
            
            total_amount = q * p
            st.markdown(f"### Tổng: :blue[{total_amount:,.0f} VNĐ]")
            
            if st.button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                if item_info['category'] != "Dịch Vụ" and item_info['stock'] < q:
                    st.error(f"Không đủ hàng! Kho hiện còn: {item_info['stock']}")
                else:
                    if item_info['category'] != "Dịch Vụ":
                        idx = st.session_state.products[st.session_state.products['name'] == item_name].index[0]
                        st.session_state.products.at[idx, 'stock'] -= q
                    
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
        search = st.text_input("🔍 Tìm theo tên hoặc mã vạch...", "")
        df_stock = st.session_state.products.copy()
        if search:
            df_stock = df_stock[(df_stock['name'].str.contains(search, case=False)) | (df_stock['barcode'].str.contains(search))]
        st.dataframe(df_stock, use_container_width=True, hide_index=True)
        
    with t_add:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Thêm Sản Phẩm Mới")
            with st.form("new_product"):
                new_id = st.text_input("Mã SP (Nội bộ)")
                new_barcode = st.text_input("Mã Barcode / QR (Quét vào đây)")
                new_name = st.text_input("Tên sản phẩm")
                new_unit = st.selectbox("Đơn vị", ["Cái", "Bộ", "Mét", "Lần", "Kg"])
                new_cat = st.selectbox("Phân loại", ["Hàng Hóa", "Vật Tư", "Dịch Vụ"])
                new_cost = st.number_input("Giá vốn", min_value=0)
                new_price = st.number_input("Giá bán", min_value=0)
                new_stock = st.number_input("Tồn đầu kỳ", min_value=0)
                
                if st.form_submit_button("Lưu sản phẩm"):
                    new_p = {"id": new_id, "barcode": new_barcode, "name": new_name, "unit": new_unit, "stock": new_stock, "cost": new_cost, "price": new_price, "category": new_cat}
                    st.session_state.products = pd.concat([st.session_state.products, pd.DataFrame([new_p])], ignore_index=True)
                    log_event("DANH MỤC", f"Thêm mới SP: {new_name} (Mã: {new_barcode})", 0)
                    st.success("Đã thêm sản phẩm!")
                    st.rerun()
        
        with col_b:
            st.subheader("Nhập Thêm Hàng")
            # Quét mã để nhập kho nhanh
            in_code = st.text_input("🔍 Quét mã để tìm nhanh", key="import_barcode")
            prod_in = find_product_by_barcode(in_code)
            
            with st.form("add_stock"):
                if prod_in is not None:
                    st.success(f"Đang nhập cho: {prod_in['name']}")
                    selected_name = prod_in['name']
                else:
                    selected_name = st.selectbox("Hoặc chọn thủ công", st.session_state.products[st.session_state.products['category'] != "Dịch Vụ"]['name'])
                
                q_add = st.number_input("Số lượng nhập thêm", min_value=1)
                cost_in = st.number_input("Giá nhập thực tế", min_value=0)
                
                if st.form_submit_button("Xác nhận nhập"):
                    idx = st.session_state.products[st.session_state.products['name'] == selected_name].index[0]
                    st.session_state.products.at[idx, 'stock'] += q_add
                    log_event("NHẬP KHO", f"Nhập thêm {q_add} {selected_name}", q_add * cost_in)
                    st.success(f"Đã cập nhật kho cho {selected_name}")
                    st.rerun()

# --- 3. PHÂN HỆ NHẬT KÝ ---
elif menu == "📓 Nhật Ký Hệ Thống":
    st.markdown('<p class="main-header">📓 Nhật Ký Giao Dịch & Biến Động</p>', unsafe_allow_html=True)
    if not st.session_state.journal_logs.empty:
        st.dataframe(st.session_state.journal_logs, use_container_width=True, hide_index=True)
    else:
        st.info("Chưa có ghi chép nào.")

# --- 4. PHÂN HỆ BÁO CÁO ---
elif menu == "📊 Báo Cáo Doanh Thu":
    st.markdown('<p class="main-header">📊 Báo Cáo Kinh Doanh</p>', unsafe_allow_html=True)
    if not st.session_state.orders.empty:
        df_o = st.session_state.orders
        c1, c2 = st.columns(2)
        c1.metric("Tổng Doanh Thu", f"{df_o['Tổng Tiền'].sum():,.0f} VNĐ")
        c2.metric("Tổng Số Đơn Hàng", len(df_o))
        st.divider()
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.plotly_chart(px.bar(df_o, x="Loại", y="Tổng Tiền", color="Loại", title="Doanh thu theo nhóm"), use_container_width=True)
        with col_chart2:
            st.plotly_chart(px.pie(df_o, values='Tổng Tiền', names='Sản Phẩm', hole=0.4, title="Tỷ trọng sản phẩm"), use_container_width=True)
    else:
        st.warning("Chưa có dữ liệu.")

st.divider()
st.caption("Thành Viễn Admin - Hỗ trợ Barcode/QR Scanning")
