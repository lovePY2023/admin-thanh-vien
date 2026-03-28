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
    #reader { 
        border: 2px solid #1E88E5 !important; 
        border-radius: 10px; 
        background: black; 
        margin-bottom: 10px;
    }
    /* Làm đẹp thông báo */
    .scan-status {
        padding: 10px;
        border-radius: 5px;
        background-color: #e3f2fd;
        color: #0d47a1;
        margin-bottom: 10px;
        font-weight: bold;
        text-align: center;
    }
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

if 'last_scanned_code' not in st.session_state:
    st.session_state.last_scanned_code = ""

# --- HÀM TRỢ GIÚP ---
def find_product_by_barcode(code):
    if not code: return None
    clean_code = str(code).strip()
    result = st.session_state.products[st.session_state.products['barcode'] == clean_code]
    return result.iloc[0] if not result.empty else None

# --- TRÌNH QUÉT MÃ TỰ ĐỘNG (CẢI TIẾN ĐỘ NHẠY) ---
def auto_scanner_component():
    """Trình quét mã sử dụng HTML5-QRCode với cơ chế xử lý lỗi và độ trễ thấp"""
    # Sử dụng Session Storage để giữ dữ liệu bền vững hơn trong iframe
    scanner_html = f"""
    <div id="reader" style="width: 100%;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const qrCodeSuccessCallback = (decodedText, decodedResult) => {{
            // Phát tiếng Beep nhẹ khi quét thành công (giả lập máy quét)
            const audio = new Audio('https://www.soundjay.com/button/beep-07.mp3');
            audio.play();

            // Gửi dữ liệu qua URL để đồng bộ với Streamlit
            const url = new URL(window.parent.location.href);
            url.searchParams.set('barcode', decodedText);
            url.searchParams.set('t', Date.now()); // Tránh cache trình duyệt
            window.parent.location.href = url.href;
            
            html5QrCode.stop().catch(err => console.error(err));
        }};

        const config = {{ 
            fps: 20, 
            qrbox: {{ width: 250, height: 250 }},
            aspectRatio: 1.0
        }};

        // Khởi chạy camera sau
        html5QrCode.start(
            {{ facingMode: "environment" }}, 
            config, 
            qrCodeSuccessCallback
        ).catch((err) => {{
            console.error("Không thể bật camera:", err);
        }});
    </script>
    """
    return components.html(scanner_html, height=350)

# --- XỬ LÝ MÃ QUÉT TỪ URL ---
query_params = st.query_params
if "barcode" in query_params:
    st.session_state.last_scanned_code = query_params["barcode"]
    # Lưu vào log để kiểm tra nếu cần
    st.query_params.clear()

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
            
            # Giao diện quét mã
            btn_scan = st.toggle("📷 BẬT MÁY ẢNH QUÉT MÃ")
            
            if btn_scan:
                auto_scanner_component()
            
            # Hiển thị mã đã quét hoặc cho phép nhập tay
            current_code = st.text_input(
                "Mã vạch / QR nhận được:", 
                value=st.session_state.last_scanned_code, 
                key="barcode_entry"
            )
            
            product = find_product_by_barcode(current_code)
            
            # Nếu tìm thấy sản phẩm, hiển thị thông tin nhanh
            if product is not None:
                st.markdown(f"""
                <div class="scan-status">
                    ✅ Đã nhận diện: {product['name']}<br>
                    Tồn kho: {product['stock']} {product['unit']}
                </div>
                """, unsafe_allow_html=True)
            elif current_code != "":
                st.warning("⚠️ Không tìm thấy sản phẩm với mã này.")

            with st.form("sale_form", clear_on_submit=True):
                cust = st.text_input("Tên khách hàng", "Khách lẻ")
                
                all_names = st.session_state.products['name'].tolist()
                # Tự động nhảy index đến sản phẩm quét được
                default_idx = all_names.index(product['name']) if product is not None else 0
                
                item_name = st.selectbox("Chọn sản phẩm", all_names, index=default_idx)
                item_info = st.session_state.products[st.session_state.products['name'] == item_name].iloc[0]
                
                col1, col2 = st.columns(2)
                with col1:
                    q = st.number_input(f"Số lượng ({item_info['unit']})", min_value=1, value=1)
                with col2:
                    p = st.number_input("Giá bán", value=int(item_info['price']), step=1000)
                
                total = q * p
                st.write(f"**Thành tiền: {total:,.0f} VNĐ**")
                
                if st.form_submit_button("XÁC NHẬN BÁN", use_container_width=True, type="primary"):
                    if item_info['category'] != "Dịch Vụ" and item_info['stock'] < q:
                        st.error("Lỗi: Số lượng trong kho không đủ!")
                    else:
                        # Trừ kho
                        if item_info['category'] != "Dịch Vụ":
                            idx = st.session_state.products[st.session_state.products['name'] == item_name].index[0]
                            st.session_state.products.at[idx, 'stock'] -= q
                        
                        # Lưu đơn
                        new_order = {
                            "Thời Gian": datetime.now().strftime("%d/%m/%Y %H:%M"), 
                            "Khách Hàng": cust, "Sản Phẩm": item_name, 
                            "Số Lượng": q, "Đơn Giá": p, "Tổng Tiền": total, 
                            "Loại": item_info['category']
                        }
                        st.session_state.orders = pd.concat([pd.DataFrame([new_order]), st.session_state.orders], ignore_index=True)
                        st.session_state.last_scanned_code = "" # Reset mã quét
                        st.success("Thành công!")
                        st.rerun()

    with col_view:
        st.subheader("Lịch sử bán hàng")
        st.dataframe(st.session_state.orders.head(15), use_container_width=True, hide_index=True)

# --- 2. QUẢN LÝ KHO ---
elif menu == "📦 Quản Lý Kho":
    st.markdown('<p class="main-header">📦 Quản Lý Kho & Nhập Hàng</p>', unsafe_allow_html=True)
    t1, t2 = st.tabs(["📋 Danh sách tồn kho", "📥 Nhập hàng mới"])
    
    with t1:
        st.dataframe(st.session_state.products, use_container_width=True, hide_index=True)
        
    with t2:
        col_scan, col_manual = st.columns([1, 1])
        with col_scan:
            st.subheader("Quét mã nhập kho")
            if st.toggle("Mở Camera"):
                auto_scanner_component()
            
            in_bar = st.text_input("Mã vạch đã quét:", value=st.session_state.last_scanned_code, key="in_bar_entry")
            p_in = find_product_by_barcode(in_bar)
            
            if p_in is not None:
                st.info(f"Đang nhập cho: {p_in['name']}")
                with st.form("import_form"):
                    qty_in = st.number_input("Số lượng nhập thêm", min_value=1)
                    if st.form_submit_button("Xác nhận nhập"):
                        idx = st.session_state.products[st.session_state.products['barcode'] == p_in['barcode']].index[0]
                        st.session_state.products.at[idx, 'stock'] += qty_in
                        st.session_state.last_scanned_code = ""
                        st.success("Đã cập nhật tồn!")
                        st.rerun()

# --- 3. BÁO CÁO ---
elif menu == "📊 Báo Cáo":
    st.markdown('<p class="main-header">📊 Báo Cáo Doanh Thu</p>', unsafe_allow_html=True)
    if not st.session_state.orders.empty:
        df = st.session_state.orders
        c1, c2 = st.columns(2)
        with c1:
            st.metric("Tổng doanh thu (VNĐ)", f"{df['Tổng Tiền'].sum():,.0f}")
        with c2:
            st.metric("Số đơn hàng", len(df))
        
        st.plotly_chart(px.pie(df, values='Tổng Tiền', names='Loại', title="Tỷ trọng doanh thu"), use_container_width=True)
        st.plotly_chart(px.bar(df, x="Sản Phẩm", y="Tổng Tiền", title="Doanh thu theo sản phẩm"), use_container_width=True)
