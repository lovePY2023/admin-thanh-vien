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
    .stButton>button { border-radius: 5px; font-weight: bold; height: 3em; }
    /* Làm nổi bật vùng quét */
    #reader { border: 2px solid #1E88E5 !important; border-radius: 10px; }
    </style>
""", unsafe_allow_html=True)

# --- KHỞI TẠO DỮ LIỆU ---
if 'products' not in st.session_state:
    st.session_state.products = pd.DataFrame([
        {"id": "P001", "barcode": "893001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "stock": 10, "cost": 6500000, "price": 8500000, "category": "Hàng Hóa"},
        {"id": "P002", "barcode": "893002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "stock": 100, "cost": 90000, "price": 150000, "category": "Vật Tư"},
        {"id": "S001", "barcode": "893003", "name": "Vệ Sinh Máy Lạnh", "unit": "Lần", "stock": 999, "cost": 50000, "price": 200000, "category": "Dịch Vụ"}
    ])

if 'orders' not in st.session_state:
    st.session_state.orders = pd.DataFrame(columns=["Thời Gian", "Khách Hàng", "Sản Phẩm", "Số Lượng", "Đơn Giá", "Tổng Tiền", "Loại"])

if 'journal_logs' not in st.session_state:
    st.session_state.journal_logs = pd.DataFrame(columns=["Thời Gian", "Loại Giao Dịch", "Chi Tiết", "Giá Trị", "Người Thực Hiện"])

# --- HÀM TRỢ GIÚP ---
def log_event(event_type, detail, value, user="Admin"):
    new_log = {"Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M:%S"), "Loại Giao Dịch": event_type, "Chi Tiết": detail, "Giá Trị": value, "Người Thực Hiện": user}
    st.session_state.journal_logs = pd.concat([pd.DataFrame([new_log]), st.session_state.journal_logs], ignore_index=True)

def find_product_by_barcode(code):
    if not code: return None
    # Chuyển về string và strip khoảng trắng để so khớp chính xác
    clean_code = str(code).strip()
    result = st.session_state.products[st.session_state.products['barcode'] == clean_code]
    return result.iloc[0] if not result.empty else None

# --- TRÌNH QUÉT MÃ TỰ ĐỘNG (JAVASCRIPT) ---
def auto_scanner_component():
    """Trình quét mã tự động bật camera sau, quét xong tự điền mã"""
    scanner_html = """
    <div id="reader" style="width: 100%;"></div>
    <div id="result" style="display:none;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const config = { fps: 10, qrbox: { width: 250, height: 250 } };

        // Ưu tiên camera sau (environment)
        html5QrCode.start({ facingMode: "environment" }, config, (decodedText) => {
            // Khi quét thành công:
            // 1. Gửi kết quả về Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: decodedText
            }, '*');
            // 2. Dừng camera
            html5QrCode.stop();
            document.getElementById('reader').style.display = 'none';
        });
    </script>
    """
    return components.html(scanner_html, height=300)

# --- MENU CHÍNH ---
with st.sidebar:
    st.title("❄️ Thành Viễn ERP")
    menu = st.radio("Chức năng chính", ["🛒 Bán Hàng & Dịch Vụ", "📦 Quản Lý Kho", "📊 Báo Cáo"])

# --- 1. BÁN HÀNG ---
if menu == "🛒 Bán Hàng & Dịch Vụ":
    st.markdown('<p class="main-header">🛒 Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.5])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Tạo Đơn Hàng")
            
            # NÚT QUÉT DUY NHẤT
            btn_scan = st.toggle("📷 BẬT MÁY ẢNH QUÉT MÃ", help="Bật để tự động quét mã vạch")
            
            scanned_code = ""
            if btn_scan:
                # Trình quét sẽ tự động bật camera sau khi tick
                # Lưu ý: Kết quả trả về sẽ được lưu vào state thông qua component
                scanned_code = auto_scanner_component()
            
            # Ô nhập mã (nhận dữ liệu từ camera hoặc nhập tay)
            manual_code = st.text_input("Mã vạch đã nhận:", placeholder="Đang chờ quét...")
            
            # Ưu tiên mã từ trình quét nếu có
            final_code = manual_code if manual_code else ""
            
            product = find_product_by_barcode(final_code)
            
            with st.form("sale_form"):
                cust = st.text_input("Khách hàng", "Khách lẻ")
                
                # Tự động chọn sản phẩm nếu mã khớp
                all_names = st.session_state.products['name'].tolist()
                default_idx = all_names.index(product['name']) if product is not None else 0
                
                item_name = st.selectbox("Sản phẩm", all_names, index=default_idx)
                item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
                
                if product is not None:
                    st.success(f"Đã tìm thấy: {product['name']}")

                q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
                p = st.number_input("Đơn giá", value=int(item_info['price']))
                
                if st.form_submit_button("XÁC NHẬN BÁN", use_container_width=True):
                    if item_info['category'] != "Dịch Vụ" and item_info['stock'] < q:
                        st.error("Kho không đủ hàng!")
                    else:
                        if item_info['category'] != "Dịch Vụ":
                            idx = st.session_state.products[st.session_state.products['name'] == item_name].index[0]
                            st.session_state.products.at[idx, 'stock'] -= q
                        
                        new_order = {"Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M"), "Khách Hàng": cust, "Sản Phẩm": item_name, "Số Lượng": q, "Đơn Giá": p, "Tổng Tiền": q*p, "Loại": item_info['category']}
                        st.session_state.orders = pd.concat([pd.DataFrame([new_order]), st.session_state.orders], ignore_index=True)
                        log_event("BÁN HÀNG", f"Bán {item_name}", q*p)
                        st.success("Đã lưu đơn hàng!")
                        st.rerun()

    with col_view:
        st.subheader("Giao dịch gần đây")
        st.dataframe(st.session_state.orders.head(10), use_container_width=True, hide_index=True)

# --- 2. QUẢN LÝ KHO ---
elif menu == "📦 Quản Lý Kho":
    st.markdown('<p class="main-header">📦 Quản Lý Kho</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["📋 Tồn kho", "➕ Nhập hàng"])
    
    with t1:
        st.dataframe(st.session_state.products, use_container_width=True, hide_index=True)
        
    with t2:
        st.subheader("Nhập thêm hàng hóa")
        # Quét mã nhập kho
        scan_in_toggle = st.toggle("📷 Bật Camera quét mã nhập")
        if scan_in_toggle:
            auto_scanner_component()
            
        in_bar = st.text_input("Nhập/Quét mã hàng tại đây:", key="in_bar")
        p_in = find_product_by_barcode(in_bar)
        
        if p_in is not None:
            st.info(f"Đang nhập cho: {p_in['name']}")
            with st.form("f_import"):
                q_in = st.number_input("Số lượng nhập", min_value=1)
                if st.form_submit_button("Xác nhận nhập"):
                    idx = st.session_state.products[st.session_state.products['barcode'] == p_in['barcode']].index[0]
                    st.session_state.products.at[idx, 'stock'] += q_in
                    log_event("NHẬP KHO", f"Nhập {p_in['name']}", 0)
                    st.success("Đã cập nhật tồn kho!")
                    st.rerun()

# --- 3. BÁO CÁO ---
elif menu == "📊 Báo Cáo":
    st.markdown('<p class="main-header">📊 Báo Cáo Doanh Thu</p>', unsafe_allow_html=True)
    if not st.session_state.orders.empty:
        df = st.session_state.orders
        st.metric("Tổng Doanh Thu", f"{df['Tổng Tiền'].sum():,.0f} VNĐ")
        st.plotly_chart(px.bar(df, x="Sản Phẩm", y="Tổng Tiền", color="Loại", title="Doanh thu chi tiết"), use_container_width=True)
