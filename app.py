import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

# ==========================================
# ⚙️ VÙNG CÀI ĐẶT DANH MỤC (SỬA Ở ĐÂY)
# ==========================================
DANH_MUC_KHU_VUC = ["Gò Vấp", "Quận 12", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Hóc Môn", "Củ Chi", "Khác"]

DANH_MUC_CONG_VIEC = [
    "Vệ sinh máy lạnh", 
    "Bơm Gas R32/R410A", 
    "Sửa máy không lạnh", 
    "Sửa máy chảy nước", 
    "Tháo lắp máy lạnh", 
    "Sửa Board mạch", 
    "Sửa Tủ lạnh/Máy giặt",
    "Khác (Ghi chú chi tiết)"
]
# ==========================================

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn Quản Lý", layout="wide")

# (Phần CSS và Xử lý thời gian giữ nguyên...)
st.markdown("""
    <style>
    .header-style { font-size:22px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 15px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 14px; margin-left: 10px; }
    .tomorrow-label { color: white; background-color: #ffa500; padding: 2px 8px; border-radius: 4px; font-size: 14px; margin-left: 10px; }
    </style>
    """, unsafe_allow_html=True)

today = datetime.now().date()
tomorrow = today + timedelta(days=1)
start_this_week = today - timedelta(days=today.weekday())
this_week = [start_this_week + timedelta(days=i) for i in range(7)]
next_week = [start_this_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Điện lạnh Thành Viễn")

# --- PHẦN FORM NHẬP ---
st.markdown('<p class="header-style">➕ THÊM CA MÁY MỚI</p>', unsafe_allow_html=True)
with st.expander("Chạm để mở Form nhập liệu", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ngay = st.date_input("Ngày hẹn", value=today)
            ten_kh = st.text_input("Tên Khách hàng")
            sdt = st.text_input("Số điện thoại")
        with c2:
            # SỬ DỤNG DANH MỤC TỪ VÙNG CÀI ĐẶT
            khu_vuc = st.selectbox("Khu vực", DANH_MUC_KHU_VUC)
            dia_chi = st.text_input("Địa chỉ chi tiết")
            cv_chon = st.selectbox("Loại công việc", DANH_MUC_CONG_VIEC)
            
        ghi_chu_them = st.text_area("Ghi chú chi tiết (nếu có)")
        
        if st.form_submit_button("LƯU LỊCH"):
            noidung_cv = f"{cv_chon} | {ghi_chu_them}" if ghi_chu_them else cv_chon
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": noidung_cv,
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý"
                }).execute()
                st.success("Đã ghi sổ thành công!")
                st.rerun()

# --- HÀM RENDER GRID (Giữ nguyên như bản trước) ---
def render_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        nhan = ""
        if d == today: nhan = '<span class="today-label">HÔM NAY</span>'
        elif d == tomorrow: nhan = '<span class="tomorrow-label">NGÀY MAI</span>'
        st.markdown(f"#### {days_vn[i]} ({d.strftime('%d/%m')}) {nhan}", unsafe_allow_html=True)
        
        if not jobs:
            st.caption("Trống lịch")
        else:
            cols = st.columns(2)
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
                            st.write(f"🛠️ Việc: {job.get('CongViec')}")
                            st.divider()
                            # Các nút Nhận/Xong/Gọi/Xóa giữ nguyên...
                            if stt == "Chờ xử lý" and st.button(f"🚀 Nhận", key=f"nh_{job['id']}"):
                                supabase.table("LichLamViec").update({"TrangThai":"Đang làm"}).eq("id", job['id']).execute()
                                st.rerun()
                            elif stt == "Đang làm" and st.button(f"✅ Xong", key=f"xo_{job['id']}"):
                                supabase.table("LichLamViec").update({"TrangThai":"Hoàn thành"}).eq("id", job['id']).execute()
                                st.rerun()
                            st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none;"><button style="width:100%; border-radius:5px; border:1px solid #ddd; padding:5px; background-color:#e1f5fe;">📞 Gọi cho khách</button></a>', unsafe_allow_html=True)
                            if st.button(f"🗑️ Xóa", key=f"del_{job['id']}"):
                                supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                st.rerun()

st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)
st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
