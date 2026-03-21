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
DANH_MUC_CHOT = ["Chưa Gọi", "Từ Chối", "Đã Chốt"]

# --- CSS TỐI ƯU CÂN ĐỐI ---
st.markdown("""
    <style>
    .header-style { font-size:18px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-top: 20px; margin-bottom: 10px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
    .tomorrow-label { color: white; background-color: #ffa500; padding: 2px 6px; border-radius: 4px; font-size: 11px; }
    
    .customer-name { font-size: 16px; font-weight: 800; color: #D32F2F; margin-bottom: 2px; }
    .address-text { font-size: 13px; color: #444; line-height: 1.2; margin-bottom: 4px; }
    
    .note-box { background-color: #fffde7; padding: 8px; border-radius: 4px; font-size: 12px; border-left: 4px solid #fbc02d; margin-top: 5px; }
    .chot-box { background-color: #e8f5e9; padding: 5px; border-radius: 4px; font-size: 12px; border: 1px solid #4caf50; color: #2e7d32; font-weight: bold; text-align: center; margin-bottom: 5px; }
    
    .stSelectbox label, .stTextInput label { display: none; } 
    .stButton>button { height: 32px; font-size: 12px !important; }
    hr { margin: 10px 0 !important; }
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

# --- FORM NHẬP ---
with st.expander("➕ THÊM CA MỚI", expanded=False):
    with st.form("f_nhap", clear_on_submit=True):
        r1 = st.columns([2, 2, 2, 3, 2])
        ngay = r1[0].date_input("Ngày", value=today)
        ten_kh = r1[1].text_input("Tên Khách")
        sdt = r1[2].text_input("SĐT")
        dia_chi = r1[3].text_input("Địa chỉ")
        khu_vuc = r1[4].selectbox("Quận", DANH_MUC_KHU_VUC)
        
        r2 = st.columns([3, 7])
        cv_chon = r2[0].selectbox("Việc", DANH_MUC_CONG_VIEC)
        ghi_chu_dau = r2[1].text_input("Ghi chú ban đầu...")
        
        if st.form_submit_button("LƯU HỆ THỐNG", use_container_width=True):
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": f"{cv_chon} | {ghi_chu_dau}",
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý", "ChotViec": "Chưa Gọi"
                }).execute()
                st.rerun()

# --- HÀM HIỂN THỊ GRID ---
def render_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        nhan = ""
        if d == today: nhan = f'<span class="today-label">HÔM NAY</span>'
        elif d == tomorrow: nhan = f'<span class="tomorrow-label">NGÀY MAI</span>'
        
        st.markdown(f"#### {days_vn[i]} ({d.strftime('%d/%m')}) {nhan}", unsafe_allow_html=True)
        
        if not jobs:
            st.caption("Trống lịch")
        else:
            grid_cols = st.columns(4) 
            for idx, job in enumerate(jobs):
                with grid_cols[idx % 4]:
                    stt = job.get('TrangThai', 'Chờ xử lý')
                    chot = job.get('ChotViec', 'Chưa Gọi') or "Chưa Gọi"
                    
                    with st.container(border=True):
                        st.markdown(f"<div class='customer-name'>{job['TenKH']}</div>", unsafe_allow_html=True)
                        st.markdown(f"<div class='address-text'>📍 {job['KhuVuc']} - {job['DiaChi']}</div>", unsafe_allow_html=True)
                        
                        if chot == "Đã Chốt":
                            st.markdown(f"<div class='chot-box'>✅ ĐÃ CHỐT</div>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='address-text'>🛠️ {job.get('CongViec', 'N/A')}</div>", unsafe_allow_html=True)
                        
                        if job.get("GhiChuThem"):
                            st.markdown(f"<div class='note-box'>📝 {job['GhiChuThem']}</div>", unsafe_allow_html=True)
                        
                        st.divider()

                        # Nút gọi và trạng thái
                        c_call, c_status = st.columns([1, 1])
                        c_call.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none; display:block; text-align:center; background:#1e88e5; color:white; padding:6px; border-radius:5px; font-weight:bold; font-size:12px;">📞 Gọi</a>', unsafe_allow_html=True)
                        
                        idx_chot = DANH_MUC_CHOT.index(chot) if chot in DANH_MUC_CHOT else 0
                        moi_chot = c_status.selectbox("S", DANH_MUC_CHOT, index=idx_chot, key=f"s_{job['id']}")
                        
                        if moi_chot != chot:
                            up = {"ChotViec": moi_chot}
                            if moi_chot == "Từ Chối": up["TrangThai"] = "Hoàn thành"
                            supabase.table("LichLamViec").update(up).eq("id", job['id']).execute()
                            st.rerun()

                        # Thao tác
                        if stt != "Hoàn thành":
                            note_val = st.text_input("Note:", key=f"in_{job['id']}", value=job.get("GhiChuThem", ""), placeholder="Ghi chú...")
                            
                            b1, b2, b3 = st.columns([1, 2.5, 1])
                            if b1.button("💾", key=f"v_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"GhiChuThem": note_val}).eq("id", job['id']).execute()
                                st.rerun()
                            if b2.button("XONG", key=f"d_{job['id']}", use_container_width=True, type="primary"):
                                t_now = datetime.now(tz).strftime("%H:%M - %d/%m")
                                supabase.table("LichLamViec").update({"TrangThai": "Hoàn thành", "GhiChuThem": note_val, "ThoiGianXong": t_now}).eq("id", job['id']).execute()
                                st.rerun()
                            if b3.button("🗑️", key=f"l_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                st.rerun()
                        else:
                            st.success(f"Xong: {job.get('ThoiGianXong', 'N/A')}")
                            if st.button("Xóa ca", key=f"del_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                st.rerun()

# --- HIỂN THỊ ---
st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)

st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
