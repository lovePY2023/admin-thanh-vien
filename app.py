import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import time

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Quản Lý Thành Viễn", layout="wide", page_icon="❄️")

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E88E5; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    /* Giả lập khung quét QR chuyên nghiệp */
    .qr-scanner-sim {
        border: 2px dashed #4CAF50;
        padding: 20px;
        text-align: center;
        background-color: #f1f8e9;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU (SESSION STATE) ---
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"id": "P001", "barcode": "893001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "stock": 10, "cost": 6500000, "price": 8500000, "category": "Hàng Hóa"},
        {"id": "P002", "barcode": "893002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "stock": 100, "cost": 90000, "price": 150000, "category": "Vật Tư"},
        {"id": "S001", "barcode": "SERVICE01", "name": "Vệ Sinh Máy Lạnh", "unit": "Lần", "stock": 999, "cost": 50000, "price": 200000, "category": "Dịch Vụ"}
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
    st.session_state.journal_logs = pd.concat([pd.DataFrame([new_log])], ignore_index=True)

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
    st.info("💡 Mẹo: Dùng máy quét cầm tay hoặc camera điện thoại để nhập liệu nhanh hơn.")

# --- 1. PHÂN HỆ BÁN HÀNG ---
if menu == "🛒 Bán Hàng & Dịch Vụ":
    st.markdown('<p class="main-header">🛒 Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.5])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Tạo Đơn Hàng")
            
            # Giao diện quét mã cải tiến
            tab_manual, tab_scan = st.tabs(["⌨️ Nhập tay", "📷 Quét QR/Barcode"])
            
            scanned_code = ""
            
            with tab_scan:
                st.markdown('<div class="qr-scanner-sim">Hệ thống đang sẵn sàng nhận diện qua Camera</div>', unsafe_allow_html=True)
                cam_file = st.camera_input("Chụp mã sản phẩm", label_visibility="collapsed")
                if cam_file:
                    with st.spinner("Đang nhận diện mã vạch..."):
                        time.sleep(1) # Giả lập độ trễ AI
                        # Giả lập kết quả nhận diện (Trong thực tế sẽ dùng thư viện giải mã ảnh)
                        st.info("Ảnh đã được ghi nhận. Hệ thống AI (Gemini) sẽ sớm được kích hoạt tại đây.")

            with tab_manual:
                scanned_code = st.text_input("Mã vạch / QR", placeholder="Quét hoặc nhập mã...")
            
            product_scanned = find_product_by_barcode(scanned_code)
            
            # Logic tự động chọn sản phẩm
            all_product_names = st.session_state.products['name'].tolist()
            default_idx = 0
            if product_scanned is not None:
                st.success(f"✅ Tìm thấy: {product_scanned['name']}")
                default_idx = all_product_names.index(product_scanned['name'])

            cust = st.text_input("Tên khách hàng", placeholder="Tên hoặc SĐT khách...")
            item_name = st.selectbox("Sản phẩm / Dịch vụ", all_product_names, index=default_idx)
            item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
            
            q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
            p = st.number_input("Đơn giá bán (VNĐ)", value=int(item_info['price']), step=10000)
            
            total_amount = q * p
            st.markdown(f"### Tổng: :blue[{total_amount:,.0f} VNĐ]")
            
            if st.button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                if item_info['category'] != "Dịch Vụ" and item_info['stock'] < q:
                    st.error(f"Lỗi: Kho không đủ hàng ({item_info['stock']} còn lại)")
                else:
                    if item_info['category'] != "Dịch Vụ":
                        idx = st.session_state.products[st.session_state.products['name'] == item_name].index[0]
                        st.session_state.products.at[idx, 'stock'] -= q
                    
                    new_order = {
                        "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Khách Hàng": cust if cust else "Khách lẻ",
                        "Sản Phẩm": item_name, "Số Lượng": q, "Đơn Giá": p, "Tổng Tiền": total_amount, "Loại": item_info['category']
                    }
                    st.session_state.orders = pd.concat([pd.DataFrame([new_order]), st.session_state.orders], ignore_index=True)
                    log_event("BÁN HÀNG", f"Bán {item_name} cho {cust}", total_amount)
                    st.success("Giao dịch thành công!")
                    st.rerun()

    with col_view:
        st.subheader("Giao dịch gần đây")
        st.dataframe(st.session_state.orders.head(10), use_container_width=True, hide_index=True)

# --- 2. PHÂN HỆ QUẢN LÝ KHO ---
elif menu == "📦 Quản Lý Kho":
    st.markdown('<p class="main-header">📦 Quản Lý Kho & Vật Tư</p>', unsafe_allow_html=True)
    t_stock, t_add = st.tabs(["📋 Tồn kho hiện tại", "➕ Nhập hàng mới"])
    
    with t_stock:
        df_stock = st.session_state.products.copy()
        st.dataframe(df_stock, use_container_width=True, hide_index=True)
        
    with t_add:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("🛒 Thêm vào Danh mục")
            with st.form("new_product"):
                n_id = st.text_input("Mã nội bộ")
                n_bar = st.text_input("Mã Barcode / QR (Quét mã để gán)")
                n_name = st.text_input("Tên hàng hóa")
                n_unit = st.selectbox("Đơn vị", ["Bộ", "Máy", "Mét", "Cái", "Lần"])
                n_cat = st.selectbox("Phân loại", ["Hàng Hóa", "Vật Tư", "Dịch Vụ"])
                n_cost = st.number_input("Giá nhập dự kiến", min_value=0)
                n_price = st.number_input("Giá bán niêm yết", min_value=0)
                n_stock = st.number_input("Số lượng ban đầu", min_value=0)
                if st.form_submit_button("Lưu Danh Mục"):
                    new_p = {"id": n_id, "barcode": n_bar, "name": n_name, "unit": n_unit, "stock": n_stock, "cost": n_cost, "price": n_price, "category": n_cat}
                    st.session_state.products = pd.concat([st.session_state.products, pd.DataFrame([new_p])], ignore_index=True)
                    st.success("Đã thêm vào danh mục!")
                    st.rerun()
        with col_b:
            st.subheader("📦 Phiếu Nhập Kho")
            scan_in = st.text_input("Quét mã hàng nhập", key="in_scan")
            p_in = find_product_by_barcode(scan_in)
            with st.form("import_stock"):
                selected_in = p_in['name'] if p_in is not None else st.selectbox("Chọn SP", st.session_state.products['name'])
                q_in = st.number_input("Số lượng thực nhập", min_value=1)
                cost_actual = st.number_input("Giá nhập thực tế", min_value=0)
                if st.form_submit_button("Xác nhận nhập kho"):
                    idx = st.session_state.products[st.session_state.products['name'] == selected_in].index[0]
                    st.session_state.products.at[idx, 'stock'] += q_in
                    log_event("NHẬP KHO", f"Nhập {q_in} {selected_in}", q_in * cost_actual)
                    st.success("Đã tăng tồn kho!")
                    st.rerun()

# --- 3. PHÂN HỆ NHẬT KÝ ---
elif menu == "📓 Nhật Ký Hệ Thống":
    st.markdown('<p class="main-header">📓 Nhật Ký Giao Dịch</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.journal_logs, use_container_width=True, hide_index=True)

# --- 4. PHÂN HỆ BÁO CÁO ---
elif menu == "📊 Báo Cáo Doanh Thu":
    st.markdown('<p class="main-header">📊 Doanh Thu & Hiệu Quả</p>', unsafe_allow_html=True)
    if not st.session_state.orders.empty:
        df = st.session_state.orders
        st.metric("Tổng doanh thu", f"{df['Tổng Tiền'].sum():,.0f} VNĐ")
        st.plotly_chart(px.bar(df, x="Sản Phẩm", y="Tổng Tiền", color="Loại", title="Doanh thu theo sản phẩm"), use_container_width=True)
    else:
        st.info("Chưa có dữ liệu giao dịch.")

st.divider()
st.caption("Hệ thống quản lý Thành Viễn v1.3 - Barcode & QR Optimized")
