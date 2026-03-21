import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn POS", layout="wide")

# --- CSS GIAO DIỆN ẤN TƯỢNG ---
st.markdown("""
    <style>
    .header-style {
        font-size:22px; font-weight:bold; color: #1E88E5; 
        padding: 10px 0; border-bottom: 2px solid #1E88E5; margin-bottom: 15px;
    }
    .today-label { color: #ffffff; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 14px; margin-left: 10px; }
    .tomorrow-label { color: #ffffff; background-color: #ffa500; padding: 2px 8px; border-radius: 4px; font-size: 14px; margin-left: 10px; }
    .job-card { border-radius: 10px; border: 1px solid #eee; padding: 10px; margin-bottom: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. XỬ LÝ THỜI GIAN ---
today = datetime.now().date()
tomorrow = today + timedelta(days=1)
start_this_week = today - timedelta(days=today.weekday())
this_week = [start_this_week + timedelta(days=i) for i in range(7)]
next_week = [start_this_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Điện lạnh Thành Viễn")

# ==========================================
# PHẦN 1: FORM NHẬP LIỆU (Dùng cột CongViec)
# ==========================================
st.markdown('<p class="header-style">➕ THÊM CA MÁY MỚI</p>', unsafe_allow_html=True)
with st.expander("Chạm để mở Form nhập liệu", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ngay = st.date_input("Ngày hẹn", value=today)
            ten_kh = st.text_input("Tên Khách hàng")
            sdt = st.text_input("Số điện thoại")
        with c2:
            khu_vuc = st.selectbox("Khu vực", ["Gò Vấp", "Quận 12", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Hóc Môn", "Khác"])
            dia_chi = st.text_input("Địa chỉ chi tiết")
            
        # Tách riêng danh mục Công việc
        st.write("---")
        danhmuc_cv = ["Vệ sinh máy lạnh", "Bơm Gas R32/R410A", "Sửa máy không lạnh", "Sửa máy chảy nước", "Tháo lắp máy", "Sửa Board mạch", "Khác..."]
        cv_chon = st.selectbox("Danh mục công việc", danhmuc_cv)
        ghi_chu_them = st.text_area("Ghi chú chi tiết lỗi (nếu có)")
        
        if st.form_submit_button("LƯU VÀO HỆ THỐNG"):
            # Gộp danh mục và ghi chú vào cột CongViec
            noidung_cv = f"{cv_chon} | {ghi_chu_them}" if ghi_chu_them else cv_chon
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": noidung_cv,
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý"
                }).execute()
                st.success("Đã ghi sổ thành công!")
                st.rerun()

# ==========================================
# HÀM HIỂN THỊ DẠNG GRID
# ==========================================
def render_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        
        # Tạo nhãn đẹp cho Hôm nay/Ngày mai
        nhan = ""
        if d == today:
            nhan = '<span class="today-label">HÔM NAY</span>'
        elif d == tomorrow:
            nhan = '<span class="tomorrow-label">NGÀY MAI</span>'
        
        st.markdown(f"#### {days_vn[i]} ({d.strftime('%d/%m')}) {nhan}", unsafe_allow_html=True)
        
        if not jobs:
            st.caption("Trống lịch")
        else:
            cols = st.columns(2) # Grid 2 cột cho mobile
            for idx, job in enumerate(jobs):
                with cols[idx % 2]:
                    stt = job.get('TrangThai', 'Chờ xử lý')
                    icon = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
                    
                    with st.container(border=True):
                        st.markdown(f"**{icon} {job['TenKH']}**")
                        st.markdown(f"📍 {job['KhuVuc']}")
                        
                        with st.expander("Xem chi tiết"):
                            st.write(f"📞 SĐT: {job['SoDT']}")
                            st.write(f"🏠 ĐC: {job['DiaChi']}")
                            st.write(f"🛠️ Việc: {job.get('CongViec', 'Chưa ghi chú')}")
                            
                            st.divider()
                            # Nút bấm cập nhật
                            if stt == "Chờ xử lý":
                                if st.button(f"🚀 Nhận", key=f"nh_{job['id']}"):
                                    supabase.table("LichLamViec").update({"TrangThai":"Đang làm"}).eq("id", job['id']).execute()
                                    st.rerun()
                            elif stt == "Đang làm":
                                if st.button(f"✅ Xong", key=f"xo_{job['id']}"):
                                    supabase.table("LichLamViec").update({"TrangThai":"Hoàn thành"}).eq("id", job['id']).execute()
                                    st.rerun()
                            
                            # Nút gọi điện
                            st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none;"><button style="width:100%; border-radius:5px; border:1px solid #ddd; padding:5px; background-color:#e1f5fe;">📞 Gọi cho khách</button></a>', unsafe_allow_html=True)
                            
                            if st.button(f"🗑️ Xóa", key=f"del_{job['id']}"):
                                supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                st.rerun()

# ==========================================
# HIỂN THỊ CUỘN
# ==========================================
st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)

st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
