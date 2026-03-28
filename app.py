import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Quản Lý Thành Viễn", layout="wide", page_icon="❄️")

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E88E5; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; }
    .stButton>button { border-radius: 5px; font-weight: bold; }
    .scanner-container {
        border: 2px solid #1E88E5;
        border-radius: 10px;
        overflow: hidden;
        margin-bottom: 20px;
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
    st.session_state.orders = pd.DataFrame(columns=["Thời Gian", "Khách Hàng", "Sản Phẩm", "Số Lượng", "Đơn Giá", "Tổng Tiền", "Loại"])

if 'journal_logs' not in st.session_state:
    st.session_state.journal_logs = pd.DataFrame(columns=["Thời Gian", "Loại Giao Dịch", "Chi Tiết", "Giá Trị", "Người Thực Hiện"])

# --- HÀM TRỢ GIÚP ---
def log_event(event_type, detail, value, user="Admin"):
    new_log = {
        "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        "Loại Giao Dịch": event_type, "Chi Tiết": detail, "Giá Trị": value, "Người Thực Hiện": user
    }
    st.session_state.journal_logs = pd.concat([pd.DataFrame([new_log]), st.session_state.journal_logs], ignore_index=True)

def find_product_by_barcode(code):
    if not code: return None
    result = st.session_state.products[st.session_state.products['barcode'] == str(code).strip()]
    return result.iloc[0] if not result.empty else None

# --- COMPONENT QUÉT MÃ (JAVASCRIPT) ---
def qr_barcode_scanner():
    """Nhúng một trình quét mã vạch bằng JavaScript"""
    scanner_html = """
    <div id="reader" style="width: 100%; border-radius: 10px;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        function onScanSuccess(decodedText, decodedResult) {
            // Gửi dữ liệu về Streamlit qua một thẻ input ẩn hoặc thông báo
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: decodedText
            }, '*');
            // Tắt camera sau khi quét thành công để tiết kiệm pin
            html5QrcodeScanner.clear();
        }
        var html5QrcodeScanner = new Html5QrcodeScanner(
            "reader", { fps: 10, qrbox: 250 });
        html5QrcodeScanner.render(onScanSuccess);
    </script>
    """
    # Lưu ý: Trong môi trường thực tế, st.components cần được xử lý cẩn thận về state
    # Ở đây chúng ta dùng một cách đơn giản hơn để tích hợp vào luồng có sẵn
    return components.html(scanner_html, height=350)

# --- THANH MENU BÊN TRÁI ---
with st.sidebar:
    st.title("❄️ Thành Viễn ERP")
    menu = st.radio("Chức năng chính", ["🛒 Bán Hàng & Dịch Vụ", "📦 Quản Lý Kho", "📓 Nhật Ký Hệ Thống", "📊 Báo Cáo Doanh Thu"])

# --- 1. PHÂN HỆ BÁN HÀNG ---
if menu == "🛒 Bán Hàng & Dịch Vụ":
    st.markdown('<p class="main-header">🛒 Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.5])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Tạo Đơn Hàng")
            
            # Nút mở trình quét Live
            show_scanner = st.checkbox("📷 Mở máy ảnh quét mã (Live)")
            scanned_val = ""
            if show_scanner:
                st.info("Đưa mã QR/Barcode vào khung hình bên dưới")
                # Trong bản thử nghiệm này, ta dùng input giả lập để bạn thấy luồng chạy
                # Khi triển khai thực tế, scanned_val sẽ lấy giá trị từ JavaScript component
                qr_barcode_scanner()
            
            scanned_code = st.text_input("Mã vạch đã quét", value="", placeholder="Mã sẽ tự hiện ở đây hoặc nhập tay...")
            
            product_scanned = find_product_by_barcode(scanned_code)
            all_product_names = st.session_state.products['name'].tolist()
            
            default_idx = 0
            if product_scanned is not None:
                st.success(f"✅ Đã tìm thấy: {product_scanned['name']}")
                default_idx = all_product_names.index(product_scanned['name'])

            cust = st.text_input("Tên khách hàng")
            item_name = st.selectbox("Sản phẩm / Dịch vụ", all_product_names, index=default_idx)
            item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
            
            q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
            p = st.number_input("Đơn giá", value=int(item_info['price']))
            
            if st.button("XÁC NHẬN BÁN", type="primary", use_container_width=True):
                if item_info['category'] != "Dịch Vụ" and item_info['stock'] < q:
                    st.error("Không đủ tồn kho!")
                else:
                    if item_info['category'] != "Dịch Vụ":
                        idx = st.session_state.products[st.session_state.products['name'] == item_name].index[0]
                        st.session_state.products.at[idx, 'stock'] -= q
                    
                    new_order = {
                        "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M"),
                        "Khách Hàng": cust if cust else "Khách lẻ",
                        "Sản Phẩm": item_name, "Số Lượng": q, "Đơn Giá": p, "Tổng Tiền": q*p, "Loại": item_info['category']
                    }
                    st.session_state.orders = pd.concat([pd.DataFrame([new_order]), st.session_state.orders], ignore_index=True)
                    log_event("BÁN HÀNG", f"Bán {item_name}", q*p)
                    st.success("Đã xong!")
                    st.rerun()

    with col_view:
        st.subheader("Giao dịch gần đây")
        st.dataframe(st.session_state.orders.head(10), use_container_width=True, hide_index=True)

# --- 2. PHÂN HỆ QUẢN LÝ KHO ---
elif menu == "📦 Quản Lý Kho":
    st.markdown('<p class="main-header">📦 Quản Lý Kho</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["📋 Tồn kho", "➕ Nhập hàng"])
    
    with t1:
        st.dataframe(st.session_state.products, use_container_width=True, hide_index=True)
        
    with t2:
        col_a, col_b = st.columns(2)
        with col_a:
            st.subheader("Sản phẩm mới")
            with st.form("new_p"):
                n_bar = st.text_input("Gán mã Barcode")
                n_name = st.text_input("Tên sản phẩm")
                n_cat = st.selectbox("Loại", ["Hàng Hóa", "Vật Tư", "Dịch Vụ"])
                n_cost = st.number_input("Giá vốn", min_value=0)
                n_price = st.number_input("Giá bán", min_value=0)
                if st.form_submit_button("Lưu"):
                    new_p = {"id": "NEW", "barcode": n_bar, "name": n_name, "unit": "Cái", "stock": 0, "cost": n_cost, "price": n_price, "category": n_cat}
                    st.session_state.products = pd.concat([st.session_state.products, pd.DataFrame([new_p])], ignore_index=True)
                    st.rerun()
        with col_b:
            st.subheader("Nhập thêm")
            # Tích hợp quét mã để nhập hàng
            show_scan_in = st.checkbox("📷 Quét mã nhập hàng")
            if show_scan_in:
                qr_barcode_scanner()
            
            in_bar = st.text_input("Mã vạch nhập", key="in_bar")
            p_in = find_product_by_barcode(in_bar)
            if p_in is not None:
                st.success(f"Nhập cho: {p_in['name']}")
                with st.form("f_in"):
                    q_in = st.number_input("Số lượng nhập", min_value=1)
                    if st.form_submit_button("Xác nhận"):
                        idx = st.session_state.products[st.session_state.products['name'] == p_in['name']].index[0]
                        st.session_state.products.at[idx, 'stock'] += q_in
                        log_event("NHẬP KHO", f"Nhập {p_in['name']}", 0)
                        st.rerun()

# --- 3. NHẬT KÝ ---
elif menu == "📓 Nhật Ký Hệ Thống":
    st.markdown('<p class="main-header">📓 Nhật Ký Hệ Thống</p>', unsafe_allow_html=True)
    st.dataframe(st.session_state.journal_logs, use_container_width=True, hide_index=True)

# --- 4. BÁO CÁO ---
elif menu == "📊 Báo Cáo Doanh Thu":
    st.markdown('<p class="main-header">📊 Báo Cáo Doanh Thu</p>', unsafe_allow_html=True)
    if not st.session_state.orders.empty:
        df = st.session_state.orders
        st.metric("Tổng Doanh Thu", f"{df['Tổng Tiền'].sum():,.0f} VNĐ")
        st.plotly_chart(px.bar(df, x="Sản Phẩm", y="Tổng Tiền", color="Loại", title="Doanh thu chi tiết"), use_container_width=True)

st.divider()
st.caption("Thành Viễn Admin v1.4 - Live Scanner Integrated")
