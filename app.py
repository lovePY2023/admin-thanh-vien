import streamlit as st
from supabase import create_client

# 1. Kết nối Supabase (Lấy từ Secrets)
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Cấu hình trang
st.set_page_config(page_title="Thành Viễn Admin", layout="wide")

# --- 2. CSS TỐI ƯU MOBILE: ÉP 3 CỘT NẰM NGANG ---
st.markdown("""
    <style>
    /* Ép các cột chia đều 33% và nằm ngang trên mọi thiết bị */
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
        min-width: 33% !important;
        text-align: center;
    }
    /* Chỉnh cỡ chữ số tóm tắt nhỏ lại để không bị tràn */
    [data-testid="stMetricValue"] {
        font-size: 24px !important;
    }
    /* Khoảng cách giữa các phần */
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("❄️ Điện lạnh Thành Viễn")

# --- 3. LẤY DỮ LIỆU THỜI GIAN THỰC ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

# Tính toán chỉ số
cho = len([t for t in data if t.get('TrangThai') == "Chờ xử lý"])
dang = len([t for t in data if t.get('TrangThai') == "Đang làm"])
xong = len([t for t in data if t.get('TrangThai') == "Hoàn thành"])

# --- 4. HIỂN THỊ 3 CỘT TÓM TẮT (NẰM NGANG) ---
c1, c2, c3 = st.columns(3)
c1.metric("🔴 Chờ", cho)
c2.metric("🟡 Làm", dang)
c3.metric("✅ Xong", xong)

st.divider()

# --- 5. GIAO DIỆN CHÍNH ---
tab1, tab2 = st.tabs(["➕ NHẬP VIỆC", "📋 DANH SÁCH"])

with tab1:
    with st.form("nhap_form", clear_on_submit=True):
        nd = st.text_area("Nội dung & Địa chỉ khách hàng", placeholder="VD: Anh Nam - 123 Quang Trung, Gò Vấp - Sửa máy giặt...")
        if st.form_submit_button("LƯU HỆ THỐNG"):
            if nd:
                supabase.table("LichLamViec").insert({
                    "Viec": nd, 
                    "TrangThai": "Chờ xử lý"
                }).execute()
                st.success("Đã ghi sổ thành công!")
                st.rerun()
            else:
                st.error("Vui lòng nhập nội dung!")

with tab2:
    # Sắp xếp: ID lớn nhất (mới nhất) hiện lên đầu
    sorted_data = sorted(data, key=lambda x: x['id'], reverse=True)
