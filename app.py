import streamlit as st
from supabase import create_client

# Kết nối
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn Admin", layout="wide")

# --- MẸO CSS: ÉP CỘT NẰM NGANG TRÊN MOBILE ---
st.markdown("""
    <style>
    [data-testid="column"] {
        width: 33% !important;
        flex: 1 1 33% !important;
        min-width: 33% !important;
        text-align: center;
    }
    /* Chỉnh cỡ chữ số nhỏ lại một chút để vừa màn hình điện thoại */
    [data-testid="stMetricValue"] {
        font-size: 25px !important;
    }
    </style>
    """, unsafe_allow_status=True)

st.title("❄️ Điện lạnh Thành Viễn")

# --- LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

cho = len([t for t in data if t.get('TrangThai') == "Chờ xử lý"])
dang = len([t for t in data if t.get('TrangThai') == "Đang làm"])
xong = len([t for t in data if t.get('TrangThai') == "Hoàn thành"])

# --- HIỂN THỊ 3 CỘT (Đã ép ngang bằng CSS ở trên) ---
c1, c2, c3 = st.columns(3)
c1.metric("🔴 Chờ", cho)
c2.metric("🟡 Làm", dang)
c3.metric("✅ Xong", xong)

st.divider()

# --- DANH SÁCH VIỆC ---
# (Phần Tab và Danh sách giữ nguyên như cũ hoặc lược bớt theo ý bạn)
tab1, tab2 = st.tabs(["➕ NHẬP VIỆC", "📋 DANH SÁCH"])

with tab1:
    with st.form("nhap_form", clear_on_submit=True):
        nd = st.text_area("Nội dung & Địa chỉ khách")
        if st.form_submit_button("LƯU HỆ THỐNG"):
            supabase.table("LichLamViec").insert({"Viec": nd, "TrangThai": "Chờ xử lý"}).execute()
            st.rerun()

with tab2:
    for task in sorted(data, key=lambda x: x['id'], reverse=True):
        stt = task.get('TrangThai', 'Chờ xử lý')
        icon = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
        
        with st.expander(f"{icon} {task['Viec'][:35]}..."):
            st.write(task['Viec'])
            # Nút cập nhật trạng thái nhanh ở đây...
