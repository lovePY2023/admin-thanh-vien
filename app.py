import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Lịch Thành Viễn", layout="wide")

# --- CSS TỐI ƯU GIAO DIỆN CUỘN ---
st.markdown("""
    <style>
    .header-style {
        font-size:22px; font-weight:bold; color: #1E88E5; 
        padding: 10px 0; border-bottom: 2px solid #1E88E5;
        margin-top: 20px;
    }
    .stExpander { border: 1px solid #e6e9ef; border-radius: 8px; }
    .status-tag { padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. XỬ LÝ THỜI GIAN ---
today = datetime.now().date()
# Tìm Thứ 2 tuần này
start_this_week = today - timedelta(days=today.weekday())
# Tìm Thứ 2 tuần tới
start_next_week = start_this_week + timedelta(days=7)

def get_days(start):
    return [start + timedelta(days=i) for i in range(7)]

this_week = get_days(start_this_week)
next_week = get_days(start_next_week)
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

st.title("❄️ Điện lạnh Thành Viễn")

# ==========================================
# PHẦN 1: NHẬP LỊCH MỚI (Thu gọn để dễ cuộn)
# ==========================================
st.markdown('<p class="header-style">➕ NHẬP LỊCH MỚI</p>', unsafe_allow_html=True)
with st.expander("Chạm để mở form nhập liệu", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ngay_hen = st.date_input("Ngày hẹn", value=today)
        with c2:
            trang_thai = st.selectbox("Trạng thái", ["Chờ xử lý", "Đang làm", "Hoàn thành"])
        
        nội_dung = st.text_area("Nội dung (Tên khách, SĐT, Địa chỉ, Lỗi máy...)")
        
        if st.form_submit_button("LƯU HỆ THỐNG"):
            if nội_dung:
                # SỬA LỖI NGOẶC TẠI ĐÂY
                supabase.table("LichLamViec").insert({
                    "Viec": nội_dung,
                    "NgayHen": str(ngay_hen),
                    "TrangThai": trang_thai
                }).execute()
                st.success("Đã lưu lịch thành công!")
                st.rerun()
            else:
                st.error("Vui lòng nhập nội dung công việc!")

# ==========================================
# PHẦN 2: LỊCH TUẦN NÀY
# ==========================================
st.markdown('<p class="header-style">🗓️ LỊCH TUẦN NÀY</p>', unsafe_allow_html=True)

for i, d in enumerate(this_week):
    # Lọc việc theo ngày
    jobs = [j for j in data if j.get('NgayHen') == str(d)]
    
    # Đánh dấu ngày hôm nay
    is_today = "💡 " if d == today else ""
    tieu_de = f"{is_today}{days_vn[i]} ({d.strftime('%d/%m')}) - {len(jobs)} việc"
    
    with st.expander(tieu_de, expanded=(d == today)):
        if not jobs:
            st.caption("Chưa có ca máy nào.")
        for job in jobs:
            stt = job.get('TrangThai', 'Chờ xử lý')
            icon = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
            st.markdown(f"**{icon}** {job['Viec']}")
            
            # Nút cập nhật nhanh trạng thái
            c_btn1, c_btn2 = st.columns(2)
            if stt == "Chờ xử lý":
                if c_btn1.button(f"Nhận việc #{job['id']}", key=f"nhan_{job['id']}"):
                    supabase.table("LichLamViec").update({"TrangThai": "Đang làm"}).eq("id", job['id']).execute()
                    st.rerun()
            elif stt == "Đang làm":
                if c_btn1.button(f"Xong #{job['id']}", key=f"xong_{job['id']}"):
                    supabase.table("LichLamViec").update({"TrangThai": "Hoàn thành"}).eq("id", job['id']).execute()
                    st.rerun()
            st.divider()

# ==========================================
# PHẦN 3: TUẦN TIẾP THEO
# ==========================================
st.markdown('<p class="header-style">⏭️ TUẦN TIẾP THEO</p>', unsafe_allow_html=True)

for i, d in enumerate(next_week):
    jobs = [j for j in data if j.get('NgayHen') == str(d)]
    tieu_de = f"{days_vn[i]} ({d.strftime('%d/%m')}) - {len(jobs)} việc"
    
    with st.expander(tieu_de):
        if not jobs:
            st.caption("Trống lịch")
        for job in jobs:
            stt = job.get('TrangThai', 'Chờ xử lý')
            icon = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
            st.markdown(f"**{icon}** {job['Viec']}")
            st.divider()
