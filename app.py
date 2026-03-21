import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn POS", layout="wide")

# --- CSS TẠO GIAO DIỆN GRID & CARD ---
st.markdown("""
    <style>
    .header-style {
        font-size:22px; font-weight:bold; color: #1E88E5; 
        padding: 10px 0; border-bottom: 2px solid #1E88E5; margin-bottom: 15px;
    }
    .job-card {
        border: 1px solid #e6e9ef; padding: 12px; border-radius: 10px;
        background-color: #ffffff; margin-bottom: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
    .status-cho { color: #f44336; font-weight: bold; }
    .status-dang { color: #ff9800; font-weight: bold; }
    .status-xong { color: #4caf50; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. XỬ LÝ THỜI GIAN ---
today = datetime.now().date()
start_this_week = today - timedelta(days=today.weekday())
this_week = [start_this_week + timedelta(days=i) for i in range(7)]
next_week = [start_this_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Hệ thống Thành Viễn")

# ==========================================
# PHẦN 1: FORM NHẬP LIỆU CHI TIẾT
# ==========================================
st.markdown('<p class="header-style">➕ NHẬP CA MÁY MỚI</p>', unsafe_allow_html=True)
with st.expander("Chạm để mở Form nhập liệu", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ngay = st.date_input("Ngày hẹn", value=today)
            ten_kh = st.text_input("Tên Khách hàng")
            sdt = st.text_input("Số điện thoại")
        with c2:
            khu_vuc = st.selectbox("Khu vực", ["Gò Vấp", "Quận 12", "Bình Thạnh", "Tân Bình", "Khác"])
            dia_chi = st.text_input("Địa chỉ chi tiết")
        
        ghi_chu = st.text_area("Tình trạng máy & Ghi chú")
        
        if st.form_submit_button("LƯU LỊCH"):
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "Viec": ghi_chu,
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý"
                }).execute()
                st.success("Đã lưu ca máy thành công!")
                st.rerun()

# ==========================================
# HÀM HIỂN THỊ DẠNG GRID
# ==========================================
def render_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        is_today = "💡 " if d == today else ""
        st.subheader(f"{is_today}{days_vn[i]} ({d.strftime('%d/%m')})")
        
        if not jobs:
            st.caption("Trống lịch")
        else:
            # Tạo Grid 2 cột trên mobile
            cols = st.columns(2)
            for idx, job in enumerate(jobs):
                with cols[idx % 2]:
                    stt = job.get('TrangThai', 'Chờ xử lý')
                    color_class = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
                    
                    with st.container(border=True):
                        st.markdown(f"**{color_class} {job['TenKH']}**")
                        st.markdown(f"📞 {job['SoDT']}")
                        st.markdown(f"📍 {job['KhuVuc']} - {job['DiaChi']}")
                        
                        with st.expander("Chi tiết & Cập nhật"):
                            st.write(f"📝 {job['Viec']}")
                            # Nút bấm cập nhật
                            if stt == "Chờ xử lý":
                                if st.button(f"🚀 Nhận", key=f"nhan_{job['id']}"):
                                    supabase.table("LichLamViec").update({"TrangThai":"Đang làm"}).eq("id", job['id']).execute()
                                    st.rerun()
                            elif stt == "Đang làm":
                                if st.button(f"✅ Xong", key=f"xong_{job['id']}"):
                                    supabase.table("LichLamViec").update({"TrangThai":"Hoàn thành"}).eq("id", job['id']).execute()
                                    st.rerun()
                            if st.button(f"🗑️ Xóa", key=f"del_{job['id']}"):
                                supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                st.rerun()

# ==========================================
# HIỂN THỊ CUỘN
# ==========================================
st.markdown('<p class="header-style">🗓️ TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)

st.markdown('<p class="header-style">⏭️ TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
