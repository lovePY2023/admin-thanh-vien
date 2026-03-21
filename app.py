import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta

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

# --- CSS TỐI ƯU THẺ CÔNG VIỆC (HIỂN THỊ HẾT) ---
st.markdown("""
    <style>
    .header-style {
        font-size:20px; font-weight:bold; color: #1E88E5; 
        padding: 10px 0; border-bottom: 2px solid #1E88E5; margin-bottom: 10px;
    }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }
    .tomorrow-label { color: white; background-color: #ffa500; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left: 10px; }
    
    /* Làm cho text trong container rõ ràng hơn */
    .job-info { font-size: 14px; line-height: 1.4; margin-bottom: 8px; }
    .job-title { font-size: 16px; font-weight: bold; margin-bottom: 5px; border-bottom: 1px dashed #ddd; padding-bottom: 3px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. XỬ LÝ THỜI GIAN ---
today = datetime.now().date()
tomorrow = today + timedelta(days=1)
start_week = today - timedelta(days=today.weekday())
this_week = [start_week + timedelta(days=i) for i in range(7)]
next_week = [start_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Điện lạnh Thành Viễn")

# ==========================================
# PHẦN 1: FORM NHẬP LIỆU (Giữ nguyên)
# ==========================================
with st.expander("➕ THÊM CA MÁY MỚI", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        c1, c2 = st.columns(2)
        with c1:
            ngay = st.date_input("Ngày hẹn", value=today)
            ten_kh = st.text_input("Tên Khách hàng")
            sdt = st.text_input("Số điện thoại")
        with c2:
            khu_vuc = st.selectbox("Khu vực", DANH_MUC_KHU_VUC)
            dia_chi = st.text_input("Địa chỉ chi tiết")
            cv_chon = st.selectbox("Loại công việc", DANH_MUC_CONG_VIEC)
        ghi_chu = st.text_area("Ghi chú chi tiết")
        if st.form_submit_button("LƯU HỆ THỐNG"):
            if ten_kh and sdt:
                noidung_full = f"{cv_chon} | {ghi_chu}" if ghi_chu else cv_chon
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": noidung_full,
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý"
                }).execute()
                st.rerun()

# ==========================================
# HÀM HIỂN THỊ GRID KHÔNG CẦN BẤM XEM CHI TIẾT
# ==========================================
def render_full_grid(days_list):
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
                    color = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
                    
                    # TẤT CẢ THÔNG TIN HIỆN TRÊN THẺ
                    with st.container(border=True):
                        st.markdown(f"<div class='job-title'>{color} {job['TenKH']}</div>", unsafe_allow_html=True)
                        st.markdown(f"📍 **{job['KhuVuc']}**: {job['DiaChi']}")
                        st.markdown(f"🛠️ **Việc**: {job.get('CongViec', 'Chưa có nội dung')}")
                        st.markdown(f"📞 **SĐT**: {job['SoDT']}")
                        
                        st.write("") # Tạo khoảng cách nhỏ
                        
                        # CÁC NÚT BẤM THAO TÁC (DÀN HÀNG NGANG)
                        btn_c1, btn_c2 = st.columns(2)
                        
                        if stt == "Chờ xử lý":
                            if btn_c1.button(f"🚀 Nhận", key=f"nh_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"TrangThai":"Đang làm"}).eq("id", job['id']).execute()
                                st.rerun()
                        elif stt == "Đang làm":
                            if btn_c1.button(f"✅ Xong", key=f"xo_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"TrangThai":"Hoàn thành"}).eq("id", job['id']).execute()
                                st.rerun()
                        
                        # Nút gọi điện (Luôn hiện)
                        st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none;"><button style="width:100%; border:1px solid #ddd; padding:6px; border-radius:5px; background-color:#e3f2fd; cursor:pointer;">📞 Gọi Khách</button></a>', unsafe_allow_html=True)
                        
                        # Nút xóa (Để nhỏ ở dưới)
                        if btn_c2.button(f"🗑️ Xóa", key=f"del_{job['id']}", use_container_width=True):
                            supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                            st.rerun()

# --- HIỂN THỊ ---
st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_full_grid(this_week)

st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_full_grid(next_week)
