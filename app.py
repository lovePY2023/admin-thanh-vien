import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pytz

# 1. Kết nối Supabase
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn Admin", layout="wide")

# --- DANH MỤC ---
DANH_MUC_KHU_VUC = ["Gò Vấp", "Quận 12", "Bình Thạnh", "Phú Nhuận", "Tân Bình", "Hóc Môn", "Khác"]
DANH_MUC_CONG_VIEC = ["Vệ sinh máy lạnh", "Bơm Gas", "Sửa máy không lạnh", "Sửa máy chảy nước", "Tháo lắp máy", "Sửa Board", "Khác..."]

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .header-style { font-size:20px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 15px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left:10px; }
    .tomorrow-label { color: white; background-color: #ffa500; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left:10px; }
    .status-badge { font-size: 11px; padding: 2px 6px; border-radius: 10px; background-color: #f0f2f6; color: #555; border: 1px solid #ddd; }
    .note-box { background-color: #fffde7; padding: 10px; border-radius: 5px; font-size: 14px; border-left: 5px solid #fbc02d; margin: 10px 0; color: #333; }
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

st.title("❄️ Điều hành Thành Viễn")

# --- FORM NHẬP LIỆU ---
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
        ghi_chu_dau = st.text_area("Yêu cầu ban đầu")
        if st.form_submit_button("LƯU HỆ THỐNG"):
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": f"{cv_chon} | {ghi_chu_dau}",
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý", "ChotViec": "Chưa Gọi"
                }).execute()
                st.rerun()

# --- GRID HIỂN THỊ ---
def render_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        # Xử lý nhãn Ngày Mai
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
                    chot = job.get('ChotViec', 'Chưa Gọi')
                    
                    with st.container(border=True):
                        st.markdown(f"**{job['TenKH']}** <span class='status-badge'>{chot}</span>", unsafe_allow_html=True)
                        st.markdown(f"📍 **{job['KhuVuc']}**: {job['DiaChi']}")
                        st.markdown(f"🛠️ **Việc**: {job.get('CongViec', 'N/A')}")
                        
                        # HIỂN THỊ GHI CHÚ THÊM TRÊN GRID
                        ghi_chu_hien_tai = job.get("GhiChuThem", "")
                        if ghi_chu_hien_tai:
                            st.markdown(f"<div class='note-box'>📝 {ghi_chu_hien_tai}</div>", unsafe_allow_html=True)
                        
                        st.divider()

                        # NÚT GỌI
                        st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none; display:block; text-align:center; background:#e3f2fd; color:#1e88e5; padding:10px; border-radius:8px; font-weight:bold; border:1px solid #bbdefb; margin-bottom:12px;">📞 GỌI: {job["SoDT"]}</a>', unsafe_allow_html=True)
                        
                        # LOGIC CHỌN DANH MỤC: CHƯA GỌI / TỪ CHỐI / ĐÃ CHỐT
                        if chot == "Chưa Gọi":
                            c1, c2 = st.columns(2)
                            if c1.button(f"✅ ĐÃ CHỐT", key=f"ch_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"ChotViec": "Đã Chốt"}).eq("id", job['id']).execute()
                                st.rerun()
                            if c2.button(f"❌ TỪ CHỐI", key=f"hu_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"ChotViec": "Từ Chối", "TrangThai": "Hoàn thành"}).eq("id", job['id']).execute()
                                st.rerun()

                        # NÚT GHI CHÚ VÀ HOÀN THÀNH (Hiện khi đã chốt)
                        if chot == "Đã Chốt" and stt != "Hoàn thành":
                            ghi_chu_input = st.text_input("Nhập ghi chú/vật tư:", key=f"nt_{job['id']}", value=ghi_chu_hien_tai)
                            
                            b1, b2 = st.columns(2)
                            if b1.button(f"💾 LƯU", key=f"sv_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"GhiChuThem": ghi_chu_input}).eq("id", job['id']).execute()
                                st.rerun()
                            if b2.button(f"✅ HOÀN THÀNH", key=f"dn_{job['id']}", use_container_width=True, type="primary"):
                                t_now = datetime.now(tz).strftime("%H:%M - %d/%m/%Y")
                                supabase.table("LichLamViec").update({
                                    "TrangThai": "Hoàn thành", "GhiChuThem": ghi_chu_input, "ThoiGianXong": t_now
                                }).eq("id", job['id']).execute()
                                st.rerun()

                        # TRẠNG THÁI CUỐI
                        if stt == "Hoàn thành":
                            if chot == "Từ Chối": st.error("Khách đã từ chối")
                            else: st.success(f"✅ Xong lúc: {job.get('ThoiGianXong', 'N/A')}")

                        if st.button(f"🗑️ Xóa ca", key=f"dl_{job['id']}", use_container_width=True):
                            supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                            st.rerun()

st.markdown('<p class="header-style">🗓️ TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)
st.markdown('<p class="header-style">⏭️ TUẦN TỚI</p>', unsafe_allow_html=True)
render_grid(next_week)
