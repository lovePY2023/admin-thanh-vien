import streamlit as st
import pandas as pd
import streamlit.components.v1 as components
from datetime import datetime

# --- CẤU HÌNH TRANG ---
st.set_page_config(
    page_title="Thành Viễn ERP - Smart Scanner",
    page_icon="❄️",
    layout="wide"
)

# --- GIẢ LẬP DỮ LIỆU ---
if 'inventory' not in st.session_state:
    st.session_state.inventory = pd.DataFrame([
        {"barcode": "893001", "name": "Máy Lạnh Inverter 1HP", "unit": "Bộ", "price": 8500000, "stock": 10},
        {"barcode": "893002", "name": "Ống Đồng Phi 6/10", "unit": "Mét", "price": 150000, "stock": 100},
        {"barcode": "123456", "name": "Vật Tư Test", "unit": "Cái", "price": 50000, "stock": 50},
    ])

if 'last_scanned' not in st.session_state:
    st.session_state.last_scanned = None

# --- COMPONENT QUÉT MÃ VẠCH (HTML/JS) ---
# Sử dụng thư viện html5-qrcode để tối ưu trên mobile
def barcode_scanner():
    # Đoạn mã HTML/JS nhúng vào Streamlit
    scanner_html = """
    <div id="reader" style="width: 100%; border-radius: 10px; overflow: hidden; background: #000;"></div>
    <div id="result" style="margin-top: 10px; padding: 10px; background: #f0f2f5; border-radius: 5px; color: #333; font-weight: bold; text-align: center;">
        Chưa quét được mã
    </div>

    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const qrCodeSuccessCallback = (decodedText, decodedResult) => {
            document.getElementById('result').innerText = "Đã tìm thấy: " + decodedText;
            document.getElementById('result').style.background = "#d4edda";
            
            // Gửi dữ liệu về cho Streamlit
            window.parent.postMessage({
                type: 'streamlit:setComponentValue',
                value: decodedText
            }, '*');
            
            // Tạm dừng quét sau khi thành công
            html5QrCode.pause(true);
            setTimeout(() => { html5QrCode.resume(); }, 3000); 
        };
        
        const config = { fps: 20, qrbox: {width: 250, height: 150} };

        // Ưu tiên camera sau và tự động lấy nét
        html5QrCode.start({ facingMode: "environment" }, config, qrCodeSuccessCallback);
    </script>
    """
    # Nhúng vào giao diện Streamlit
    return components.html(scanner_html, height=450)

# --- GIAO DIỆN CHÍNH ---
def main():
    st.sidebar.title("🛠️ THÀNH VIỄN ERP")
    app_mode = st.sidebar.selectbox("CHẾ ĐỘ LÀM VIỆC", ["📱 QUÉT MÃ LEO KỆ", "🖥️ QUẢN LÝ TỔNG THỂ"])

    if app_mode == "📱 QUÉT MÃ LEO KỆ":
        st.header("📱 Quét Mã Vạch Tốc Độ Cao")
        st.info("Hướng camera về phía mã vạch trên sản phẩm hoặc kệ hàng.")
        
        # Hiển thị trình quét
        scanned_code = barcode_scanner()
        
        # Khi có mã được trả về từ JavaScript
        if scanned_code:
            st.session_state.last_scanned = scanned_code
            
        if st.session_state.last_scanned:
            code = st.session_state.last_scanned.strip()
            product = st.session_state.inventory[st.session_state.inventory['barcode'] == code]
            
            if not product.empty:
                st.success(f"Khớp dữ liệu: **{product.iloc[0]['name']}**")
                with st.container(border=True):
                    col1, col2 = st.columns(2)
                    col1.metric("Tồn kho", f"{product.iloc[0]['stock']} {product.iloc[0]['unit']}")
                    col2.metric("Giá bán", f"{product.iloc[0]['price']:,.0f}đ")
                    
                    qty = st.number_input("Số lượng thao tác", min_value=1, value=1)
                    op = st.radio("Loại giao dịch", ["Xuất kho", "Nhập kho"], horizontal=True)
                    
                    if st.button("XÁC NHẬN CẬP NHẬT", type="primary", use_container_width=True):
                        st.balloons()
                        st.toast("Đã cập nhật dữ liệu lên hệ thống!")
                        st.session_state.last_scanned = None
                        st.rerun()
            else:
                st.error(f"Mã vạch [{code}] không tồn tại trong danh mục sản phẩm.")
                if st.button("Thêm mới sản phẩm này"):
                    st.info("Chuyển sang trang danh mục...")

    else:
        render_pc_dashboard()

def render_pc_dashboard():
    st.title("🖥️ Trung Tâm Điều Hành PC")
    tab1, tab2, tab3 = st.tabs(["📊 Báo cáo", "🛒 Đơn hàng", "📦 Kho hàng"])
    
    with tab1:
        st.subheader("Hiệu suất bán hàng")
        # Giả lập dữ liệu báo cáo
        df = pd.DataFrame({'Ngày': ['T2', 'T3', 'T4', 'T5', 'T6'], 'Doanh thu': [5, 7, 4, 9, 12]})
        st.bar_chart(df.set_index('Ngày'))
        
    with tab2:
        st.write("Chức năng nhập đơn hàng chi tiết (PC Mode)")
        st.data_editor(pd.DataFrame([{"Khách": "Công ty A", "Tổng": 12000000, "Trạng thái": "Chưa thanh toán"}]), use_container_width=True)

    with tab3:
        st.subheader("Danh mục sản phẩm")
        st.dataframe(st.session_state.inventory, use_container_width=True)

if __name__ == "__main__":
    main()
