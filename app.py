import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pytz

# ==========================================
# ⚙️ CÀI ĐẶT DANH MỤC
# ==========================================
DANH_MUC_KHU_VUC = ["Gò Vấp", "Quận 12", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Hóc Môn", "Khác"]
DANH_MUC_CONG_VIEC = ["Vệ sinh máy lạnh", "Bơm Gas", "Sửa máy không lạnh", "Sửa máy chảy nước", "Tháo lắp máy", "Sửa Board", "Khác..."]

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn Admin", layout="wide")

# --- CSS GIAO DIỆN CHUYÊN NGHIỆP ---
st.markdown("""
    <style>
    .header-style { font-size:20px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 15px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .status-badge { font-size: 11px; padding: 2px 6px; border-radius: 10px; background-color: #f0f2f6; color: #555; border: 1px solid #ddd; }
    .note-box { background-color: #fffde7; padding: 10px; border-radius: 5px; font-size: 14px; border-left: 5px solid #fbc02d; margin: 10px 0; color: #333; }
    .job-card-chot { border-left: 8px solid #4caf50 !important; } /* Màu xanh khi khách chốt */
    .job-card-huy { opacity: 0.6; background-color: #fafafa !important; } /* Làm mờ khi hủy */
    </style>
    """, unsafe_allow_html=True)

# --- 2. XỬ LÝ THỜI GIAN VIỆT NAM ---
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now_vn = datetime.now(tz)
today = now_vn.date()
start_week = today - timedelta(days=today.weekday())
this_week = [start_week + timedelta(days=i) for i in range(7)]
next_week = [start_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Điều hành Thành Viễn")

# --- PHẦN FORM NHẬP LIỆU ---
with st.expander("➕ THÊM CA MÁY MỚI", expanded=False):
    with st.form("f_nhap", clear_
