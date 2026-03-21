import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Lịch Thành Viễn", layout="wide")

# CSS Tối ưu: Làm các khối tiêu đề nổi bật hơn để dễ nhìn khi cuộn
st.markdown("""
    <style>
    .header-style {
        font-size:24px; font-weight:bold; color: #1E88E5; 
        padding-top: 20px; padding-bottom: 10px;
        border-bottom: 2px solid #1E88E5; margin-bottom: 15px;
    }
    .stExpander { border: 1px solid #ddd; border-radius: 8px; margin-bottom: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. HÀM TÍNH TOÁN THỜI GIAN ---
today = datetime.now().date()
# Tìm Thứ 2 của tuần này
start_of_this_week = today - timedelta(days=today.weekday())
# Tìm Thứ 2 của tuần tới
start_of_next_week = start_of_this_week + timedelta(days=7)

def get_days_of_week(start_date):
    return [start_date + timedelta(days=i) for i in range(7)]

this_week = get_days_of_week(start_of_this_week)
next_week = get_days_of_week(start_of_next_week)
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

# =========================================================
# PHẦN 1: NHẬP LỊCH (Nằm trên cùng)
# =========================================================
st.markdown('<p class="header-style">➕ NHẬP LỊCH MỚI</p>', unsafe_allow_html=True)
with st.expander("Bấm vào đây để thêm ca máy mới", expanded=False):
    with st.form("nhap_lich", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ngay_hen = st.date_input("Ngày hẹn", value=today)
        with c2:
            trang_thai = st.selectbox("Trạng thái", ["Chờ xử lý", "Đang làm", "Hoàn thành"])
        
        nội_dung = st.text_area("Chi tiết công việc (Khách, SĐT, Lỗi máy...)")
        
        if st.form_submit_button("LƯU VÀO HỆ THỐNG"):
            if nội_dung:
                supabase.table("LichLamViec").insert({
                    "Viec": nội_dung,
                    "NgayHen": str(ngay_hen
