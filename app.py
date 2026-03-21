import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Lịch Thành Viễn", layout="wide")

# CSS để giao diện gọn gàng trên mobile
st.markdown("""
    <style>
    .stMetric { background-color: #f0f2f6; padding: 5px; border-radius: 5px; }
    [data-testid="column"] { width: 100% !important; } /* Trên mobile ưu tiên dọc cho dễ đọc lịch */
    </style>
    """, unsafe_allow_html=True)

st.title("📅 Lịch Công Việc Thành Viễn")

# --- 2. HÀM TÍNH TOÁN NGÀY TRONG TUẦN ---
today = datetime.now().date()
start_of_week = today - timedelta(days=today.weekday()) # Thứ 2 tuần này

def get_days_of_week(start_date):
    return [start_date + timedelta(days=i) for i in range(7)]

this_week = get_days_of_week(start_of_week)
next_week = get_days_of_week(start_of_week + timedelta(days=7))

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

# --- 4. GIAO DIỆN TAB ---
tab_nhap, tab_tuan_nay, tab_tuan_toi = st.tabs(["➕ NHẬP LỊCH", "🗓️ TUẦN NÀY", "⏭️ TUẦN TIẾP THEO"])

with tab_nhap:
    with st.form("nhap_lich", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            ngay = st.date_input("Ngày hẹn", value=today)
        with col2:
            stt = st.selectbox("Trạng thái", ["Chờ xử lý", "Đang làm", "Hoàn thành"])
        
        nd = st.text_area("Chi tiết (Tên khách, SĐT, Địa chỉ, Nội dung máy...)")
        
        if st.form_submit_button("LƯU VÀO LỊCH"):
            if nd:
                supabase.table("LichLamViec").insert({
                    "Viec": nd,
                    "NgayHen": str(ngay),
                    "TrangThai": stt
                }).execute()
                st.success(f"Đã thêm lịch cho ngày {ngay}")
                st.rerun()

def hiển_thị_lịch(danh_sách_ngày):
    days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]
    for i, d in enumerate(danh_sách_ngày):
        # Lọc công việc của ngày này
        jobs = [j for j in data if j.get('NgayHen') == str(d)]
        
        # Hiển thị tiêu đề ngày
        bg_today = "💡" if d == today else ""
        with st.expander(f"{bg_today} {days_vn[i]} ({d.strftime('%d/%m')}) - {len(jobs)} việc"):
            if not jobs:
                st.caption("Chưa có lịch")
            for j in jobs:
                stt = j.get('TrangThai', 'Chờ xử lý')
                icon = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
                st.markdown(f"**{icon}** {j['Viec']}")
                st.divider()

with tab_tuan_nay:
    hiển_thị_lịch(this_week)

with tab_tuan_toi:
    hiển_thị_lịch(next_week)
