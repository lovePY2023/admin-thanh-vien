import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pytz

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# Tối ưu giao diện rộng toàn màn hình
st.set_page_config(page_title="Thành Viễn Admin", layout="wide")

# --- DANH MỤC ---
DANH_MUC_KHU_VUC = ["Gò Vấp", "Quận 12", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Hóc Môn", "Khác"]
DANH_MUC_CONG_VIEC = ["Vệ sinh máy lạnh", "Bơm Gas", "Sửa máy không lạnh", "Sửa máy chảy nước", "Tháo lắp máy", "Sửa Board", "Khác..."]
DANH_MUC_CHOT = ["Chưa Gọi", "Từ Chối", "Đã Chốt"]

# --- CSS GIAO DIỆN TỐI ƯU (CHỮ NHỎ GỌN) ---
st.markdown("""
    <style>
    .header-style { font-size:18px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 10px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left:5px; }
    .tomorrow-label { color: white; background-color: #ffa500; padding: 2px 6px; border-radius: 4px; font-size: 11px; margin-left:5px; }
    
    /* Thu nhỏ chữ trong thẻ */
    .job-card-title { font-size: 15px; font-weight: bold; margin-bottom: 2px; color: #111; }
    .job-card-text { font-size: 13px; margin-bottom: 2px; line-height: 1.3; }
    
    .note-box { background-color: #fffde7; padding: 6px; border-radius: 4px; font-size: 12px; border-left: 4px solid #fbc02d; margin: 5px 0; color: #333; }
    .chot-box { background-color: #e8f5e9; padding: 6px; border-radius: 4px; font-size: 12px; border-left: 4px solid #4caf50; margin: 5px 0; color: #2e7d32; font-weight: bold; }
    
    /* Thu hẹp khoảng cách mặc định của Streamlit */
    .stVerticalBlock { gap: 0.5rem; }
    div[data-testid="stExpander"] { margin-bottom: 1rem; }
    </style>
    """, unsafe_allow_html=True)

# --- THỜI GIAN ---
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now_vn = datetime.now(tz)
today = now_vn.date()
tomorrow = today + timedelta(days=1)
start_week = today - timedelta(days=today.weekday())
this_week = [start_week + timedelta(days=i) for i in range(7)]
next_week = [start_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Điện lạnh Thành Viễn")

# --- FORM NHẬP LIỆU ---
with st.expander("➕ THÊM CA MÁY MỚI", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
        with c1:
            ngay = st.date_input("Ngày hẹn", value=today)
            ten_kh = st.text_input("Tên Khách hàng")
        with c2:
            sdt = st.text_input("Số điện thoại")
            khu_vuc = st.selectbox("Khu vực", DANH_MUC_KHU_VUC)
        with c3:
            dia_chi = st.text_input("Địa chỉ chi tiết")
            cv_chon = st.selectbox("Loại công việc", DANH_MUC_CONG_VIEC)
        ghi_chu_dau = st.text_area("Yêu cầu ban đầu", height=70)
        if st.form_submit_button("LƯU HỆ THỐNG"):
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": f"{cv_chon} | {ghi_chu_dau}",
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý", "ChotViec": "Chưa Gọi"
                }).execute()
                st.rerun()

# --- GRID HIỂN THỊ (4 CỘT TRÊN PC) ---
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
            # Sửa đổi quan trọng: Chia làm 4 cột cho PC
            grid_cols = st.columns(4) 
            for idx, job in enumerate(jobs):
                # Chia việc vào 4 cột xoay vòng
                with grid_cols[idx % 4]:
                    stt = job.get('TrangThai', 'Chờ xử lý')
                    chot_hien_tai = job.get('ChotViec', 'Chưa Gọi') or "Chưa Gọi"
                    
                    with st.container(border=True):
                        st.markdown(f"<div class='job-card-title'>{job['TenKH']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='job-card-text'>📍 <b>{job['KhuVuc']}</b>: {job['DiaChi']}</div>", unsafe_allow_html=True)
                        
                        if chot_hien_tai == "Đã Chốt":
                            st.markdown(f"<div class='chot-box'>✅ ĐÃ CHỐT LỊCH</div>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='job-card-text'>🛠️ {job.get('CongViec', 'N/A')}</div>", unsafe_allow_html=True)
                        
                        if job.get("GhiChuThem"):
                            st.markdown(f"<div class='note-box'>📝 {job['GhiChuThem']}</div>", unsafe_allow_html=True)
                        
                        st.divider()

                        # NÚT GỌI (Nhỏ gọn)
                        st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none; display:block; text-align:center; background:#e3f2fd; color:#1e88e5; padding:6px; border-radius:5px; font-weight:bold; font-size:12px; border:1px solid #bbdefb; margin-bottom:8px;">📞 GỌI: {job["SoDT"]}</a>', unsafe_allow_html=True)
                        
                        # Ô CHỌN TRẠNG THÁI (Thu nhỏ label)
                        idx_chot = DANH_MUC_CHOT.index(chot_hien_tai) if chot_hien_tai in DANH_MUC_CHOT else 0
                        moi_chot = st.selectbox("CSKH:", DANH_MUC_CHOT, index=idx_chot, key=f"sel_{job['id']}", label_visibility="collapsed")
                        
                        if moi_chot != chot_hien_tai:
                            up_data = {"ChotViec": moi_chot}
                            if moi_chot == "Từ Chối": up_data["TrangThai"] = "Hoàn thành"
                            supabase.table("LichLamViec").update(up_data).eq("id", job['id']).execute()
                            st.rerun()

                        # GHI CHÚ & HOÀN THÀNH
                        if stt != "Hoàn thành":
                            ghi_chu_input = st.text_input("Ghi chú:", key=f"nt_{job['id']}", value=job.get("GhiChuThem", ""), placeholder="Vật tư...")
                            
                            b1, b2 = st.columns(2)
                            if b1.button(f"💾 LƯU", key=f"sv_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"GhiChuThem": ghi_chu_input}).eq("id", job['id']).execute()
                                st.rerun()
                            if b2.button(f"✅ XONG", key=f"dn_{job['id']}", use_container_width=True, type="primary"):
                                t_now = datetime.now(tz).strftime("%H:%M - %d/%m/%Y")
                                supabase.table("LichLamViec").update({
                                    "TrangThai": "Hoàn thành", "GhiChuThem": ghi_chu_input, "ThoiGianXong": t_now
                                }).eq("id", job['id']).execute()
                                st.rerun()
                        else:
                            if chot_hien_tai == "Từ Chối": st.error("Từ chối")
                            else: st.success(f"Xong: {job.get('ThoiGianXong', 'N/A')}")

                        if st.button(f"🗑️ Xóa", key=f"dl_{job['id']}", use_container_width=True):
                            supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                            st.rerun()

st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)
st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
