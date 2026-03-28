import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import streamlit.components.v1 as components
from supabase_db import supabase, load_products, insert_order

# --- CẤU HÌNH GIAO DIỆN ---
st.set_page_config(page_title="Thành Viễn ERP", layout="wide", page_icon="❄️")

# --- CSS TÙY CHỈNH ---
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #1E88E5; }
    .stMetric { background-color: #f0f2f6; padding: 10px; border-radius: 10px; border: 1px solid #e9ecef; }
    .stButton>button { border-radius: 5px; font-weight: bold; height: 3em; }
    #reader { 
        border: 2px solid #1E88E5 !important; 
        border-radius: 10px; 
        background: black; 
        margin-bottom: 10px;
    }
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

# --- KHỞI TẠO TRẠNG THÁI ---
if 'last_scanned_code' not in st.session_state:
    st.session_state.last_scanned_code = ""

# --- HÀM TRỢ GIÚP ---
def get_product_data():
    """Lấy dữ liệu sản phẩm từ Supabase và chuyển thành DataFrame"""
    res = load_products()
    if res and res.data:
        return pd.DataFrame(res.data)
    return pd.DataFrame(columns=["id", "barcode", "name", "unit", "stock_quantity", "sale_price", "category"])

def find_product_by_barcode(df, code):
    if code == "" or df.empty: return None
    clean_code = str(code).strip()
    result = df[df['barcode'] == clean_code]
    return result.iloc[0] if not result.empty else None

# --- COMPONENT QUÉT MÃ ---
def auto_scanner_component():
    scanner_html = f"""
    <div id="reader" style="width: 100%;"></div>
    <script src="https://unpkg.com/html5-qrcode"></script>
    <script>
        const html5QrCode = new Html5Qrcode("reader");
        const qrCodeSuccessCallback = (decodedText, decodedResult) => {{
            const audio = new Audio('https://www.soundjay.com/button/beep-07.mp3');
            audio.play();
            const url = new URL(window.parent.location.href);
            url.searchParams.set('barcode', decodedText);
            url.searchParams.set('t', Date.now());
            window.parent.location.href = url.href;
            html5QrCode.stop().catch(err => console.error(err));
        }};
        const config = {{ fps: 20, qrbox: {{ width: 250, height: 250 }}, aspectRatio: 1.0 }};
        html5QrCode.start({{ facingMode: "environment" }}, config, qrCodeSuccessCallback);
    </script>
    """
    return components.html(scanner_html, height=350)

# Xử lý tham số từ URL khi quét mã xong
query_params = st.query_params
if "barcode" in query_params:
    st.session_state.last_scanned_code = query_params["barcode"]
    st.query_params.clear()

# --- MENU CHÍNH ---
with st.sidebar:
    st.title("❄️ Thành Viễn ERP")
    menu = st.sidebar.radio("Chức năng", ["🛒 Bán Hàng", "📦 Kho Hàng", "📊 Báo Cáo"])

# Lấy dữ liệu mới nhất từ Supabase
df_products = get_product_data()

# --- 1. PHÂN HỆ BÁN HÀNG ---
if menu == "🛒 Bán Hàng":
    st.markdown('<p class="main-header">🛒 Hệ Thống Bán Hàng & Dịch Vụ</p>', unsafe_allow_html=True)
    
    col_form, col_view = st.columns([1, 1.2])
    
    with col_form:
        with st.container(border=True):
            st.subheader("Quét hoặc Chọn Sản Phẩm")
            
            if st.toggle("📷 Mở Camera Quét Mã"):
                auto_scanner_component()
            
            current_code = st.text_input("Mã vạch nhận diện:", value=st.session_state.last_scanned_code)
            product = find_product_by_barcode(df_products, current_code)
            
            if product is not None:
                st.markdown(f'<div class="scan-status">✅ {product["name"]} - Tồn: {product["stock_quantity"]}</div>', unsafe_allow_html=True)

            with st.form("sale_form", clear_on_submit=True):
                cust = st.text_input("Tên khách hàng", "Khách lẻ")
                
                # Danh sách để chọn tay nếu không quét
                product_list = df_products['name'].tolist() if not df_products.empty else []
                default_idx = product_list.index(product['name']) if product is not None else 0
                
                selected_name = st.selectbox("Sản phẩm", product_list, index=default_idx)
                
                # Lấy thông tin chi tiết item đang chọn trong form
                item_info = df_products[df_products['name'] == selected_name].iloc[0]
                
                c1, c2 = st.columns(2)
                qty = c1.number_input("Số lượng", min_value=1, value=1)
                price = c2.number_input("Giá bán (VNĐ)", value=int(item_info['sale_price']), step=1000)
                
                if st.form_submit_button("XÁC NHẬN XUẤT ĐƠN", use_container_width=True, type="primary"):
                    if item_info['category'] != "Dịch Vụ" and item_info['stock_quantity'] < qty:
                        st.error("Kho không đủ hàng!")
                    else:
                        # 1. Lưu đơn hàng vào Supabase
                        order_payload = {
                            "customer_name": cust,
                            "product_id": str(item_info['id']),
                            "quantity": qty,
                            "price": price,
                            "total_amount": qty * price,
                            "order_date": datetime.now().isoformat()
                        }
                        insert_order(order_payload)
                        
                        # 2. Cập nhật tồn kho (Nếu không phải dịch vụ)
                        if item_info['category'] != "Dịch Vụ":
                            new_stock = item_info['stock_quantity'] - qty
                            supabase.table("products").update({"stock_quantity": new_stock}).eq("id", item_info['id']).execute()
                        
                        st.session_state.last_scanned_code = ""
                        st.success("Đã ghi nhận giao dịch!")
                        st.rerun()

    with col_view:
        st.subheader("Đơn hàng gần đây")
        orders_res = supabase.table("orders").select("*, products(name)").order("order_date", desc=True).limit(10).execute()
        if orders_res.data:
            view_df = pd.DataFrame(orders_res.data)
            # Làm đẹp tên sản phẩm từ quan hệ join
            view_df['Sản phẩm'] = view_df['products'].apply(lambda x: x['name'] if x else "N/A")
            st.dataframe(view_df[['order_date', 'customer_name', 'Sản phẩm', 'quantity', 'total_amount']], use_container_width=True)

# --- 2. PHÂN HỆ KHO HÀNG ---
elif menu == "📦 Kho Hàng":
    st.markdown('<p class="main-header">📦 Quản Lý Kho & Nhập Hàng</p>', unsafe_allow_html=True)
    
    t1, t2 = st.tabs(["📋 Danh Mục Tồn Kho", "📥 Nhập Kho Nhanh"])
    
    with t1:
        st.dataframe(df_products, use_container_width=True, hide_index=True)
        
    with t2:
        st.write("Quét mã sản phẩm để nhập hàng vào kho")
        if st.toggle("Bật Camera Nhập Kho"):
            auto_scanner_component()
        
        in_code = st.text_input("Mã vạch nhập:", value=st.session_state.last_scanned_code, key="in_code")
        p_in = find_product_by_barcode(df_products, in_code)
        
        if p_in is not None:
            st.success(f"Nhập hàng cho: {p_in['name']}")
            with st.form("import_form"):
                add_qty = st.number_input("Số lượng nhập thêm", min_value=1)
                if st.form_submit_button("Xác nhận nhập"):
                    new_qty = p_in['stock_quantity'] + add_qty
                    supabase.table("products").update({"stock_quantity": new_qty}).eq("id", p_in['id']).execute()
                    st.session_state.last_scanned_code = ""
                    st.success("Đã cập nhật tồn kho!")
                    st.rerun()

# --- 3. PHÂN HỆ BÁO CÁO ---
elif menu == "📊 Báo Cáo":
    st.markdown('<p class="main-header">📊 Báo Cáo Kinh Doanh</p>', unsafe_allow_html=True)
    
    all_orders = supabase.table("orders").select("*").execute()
    if all_orders.data:
        df_all = pd.DataFrame(all_orders.data)
        
        c1, c2, c3 = st.columns(3)
        c1.metric("Doanh Thu Tổng", f"{df_all['total_amount'].sum():,.0f}đ")
        c2.metric("Số Đơn Hàng", len(df_all))
        c3.metric("Số Lượng Bán", int(df_all['quantity'].sum()))
        
        # Biểu đồ
        st.subheader("Diễn biến doanh thu")
        df_all['order_date'] = pd.to_datetime(df_all['order_date'])
        daily_rev = df_all.groupby(df_all['order_date'].dt.date)['total_amount'].sum().reset_index()
        fig = px.line(daily_rev, x='order_date', y='total_amount', title="Doanh thu theo ngày")
        st.plotly_chart(fig, use_container_width=True)
