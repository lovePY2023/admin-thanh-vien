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

# --- CSS TỐI ƯU: GỌI NHANH & CHỮ TO ---
st.markdown("""
    <style>
    .header-style { font-size:20px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-top: 20px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 6px; border-radius: 4px; font-size: 13px; }
    
    /* Tên và Nút Gọi nhanh */
    .title-row { display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px; flex-wrap: wrap; gap: 10px; }
    .customer-name { font-size: 18px; font-weight: 800; color: #000000; }
    .call-link { 
        text-decoration: none !important; 
        background-color: #e3f2fd; 
        color: #1e88e5 !important; 
        padding: 5px 12px; 
        border-radius: 20px; 
        font-weight: bold; 
        font-size: 15px;
        border: 1px solid #bbdefb;
    }
    
    .address-text { font-size: 15px; color: #333; line-height: 1.4; margin-bottom: 5px; }
    
    /* Khung trạng thái */
    .note-box { background-color: #fffde7; padding: 10px; border-radius: 5px; font-size: 14px; border-left: 5px solid #fbc02d; margin: 8px 0; color: #333; }
    .chot-box { background-color: #e8f5e9; padding: 6px; border-radius: 5px; font-size: 13px; border: 1px solid #4caf50; color: #2e7d32; font-weight: bold; text-align: center; }
    
    /* Custom nút Hoàn Thành xanh lá */
    div.stButton > button[kind="primary"] {
        background-color: #28a745 !important;
        color: white !important;
        border: none !important;
    }
    
    .stSelectbox label, .stTextInput label { display: none; }
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
        c1, c2, c3 = st.columns([1, 1, 1])
        ngay = c1.date_input("Ngày hẹn", value=today)
        ten_kh = c1.text_input("Tên Khách")
        sdt = c2.text_input("Số điện thoại")
        khu_vuc = c2.selectbox("Khu vực", DANH_MUC_KHU_VUC)
        dia_chi = c3.text_input("Địa chỉ chi tiết")
        cv_chon = c3.selectbox("Công việc", DANH_MUC_CONG_VIEC)
        ghi_chu_dau = st.text_area("Yêu cầu khách hàng", height=60)
        if st.form_submit_button("LƯU HỆ THỐNG", use_container_width=True):
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": f"{cv_chon} | {ghi_chu_dau}",
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý", "ChotViec": "Chưa Gọi"
                }).execute()
                st.rerun()

# --- HÀM HIỂN THỊ ---
def render_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        nhan = f' <span class="today-label">HÔM NAY</span>' if d == today else ""
        st.markdown(f"#### {days_vn[i]} ({d.strftime('%d/%m')}){nhan}", unsafe_allow_html=True)
        
        if not jobs:
            st.caption("Trống lịch")
        else:
            grid_cols = st.columns(4) 
            for idx, job in enumerate(jobs):
                with grid_cols[idx % 4]:
                    stt = job.get('TrangThai', 'Chờ xử lý')
                    chot = job.get('ChotViec', 'Chưa Gọi') or "Chưa Gọi"
                    
                    with st.container(border=True):
                        # --- DÒNG TIÊU ĐỀ: TÊN & GỌI NHANH ---
                        st.markdown(f"""
                            <div class="title-row">
                                <span class="customer-name">{job['TenKH']}</span>
                                <a href="tel:{job['SoDT']}" class="call-link">📞 {job['SoDT']}</a>
                            </div>
                        """, unsafe_allow_html=True)

                        # --- THÔNG TIN ĐỊA CHỈ & VIỆC ---
                        st.markdown(f"<div class='address-text'>📍 {job['KhuVuc']} - {job['DiaChi']}</div>", unsafe_allow_html=True)
                        
                        if chot == "Đã Chốt":
                            st.markdown(f"<div class='chot-box'>✅ ĐÃ CHỐT LỊCH</div>", unsafe_allow_html=True)
                        
                        st.markdown(f"<div class='address-text'>🛠️ {job.get('CongViec', 'N/A')}</div>", unsafe_allow_html=True)
                        
                        if job.get("GhiChuThem"):
                            st.markdown(f"<div class='note-box'>📝 {job['GhiChuThem']}</div>", unsafe_allow_html=True)

                        # --- PHẦN THAO TÁC (KHÔNG CẦN NÚT GỌI NỮA) ---
                        if stt != "Hoàn thành":
                            with st.popover("⚙️ Cập nhật / Xong", use_container_width=True):
                                # Trạng thái CSKH
                                st.write("Trạng thái chốt việc:")
                                idx_ch = DANH_MUC_CHOT.index(chot) if chot in DANH_MUC_CHOT else 0
                                moi_ch = st.selectbox("S", DANH_MUC_CHOT, index=idx_ch, key=f"s_{job['id']}")
                                if moi_ch != chot:
                                    up = {"ChotViec": moi_ch}
                                    if moi_ch == "Từ Chối": up["TrangThai"] = "Hoàn thành"
                                    supabase.table("LichLamViec").update(up).eq("id", job['id']).execute()
                                    st.rerun()

                                # Ghi chú & Hoàn thành
                                note_val = st.text_input("Ghi chú thêm:", key=f"in_{job['id']}", value=job.get("GhiChuThem", ""))
                                
                                if st.button("💾 LƯU GHI CHÚ", key=f"v_{job['id']}", use_container_width=True):
                                    supabase.table("LichLamViec").update({"GhiChuThem": note_val}).eq("id", job['id']).execute()
                                    st.rerun()
                                    
                                if st.button("✅ HOÀN THÀNH", key=f"d_{job['id']}", use_container_width=True, type="primary"):
                                    t_now = datetime.now(tz).strftime("%H:%M - %d/%m")
                                    supabase.table("LichLamViec").update({"TrangThai": "Hoàn thành", "GhiChuThem": note_val, "ThoiGianXong": t_now}).eq("id", job['id']).execute()
                                    st.rerun()
                                    
                                if st.button("🗑️ Xóa ca máy", key=f"l_{job['id']}", use_container_width=True):
                                    supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                    st.rerun()
                        else:
                            st.success(f"Xong: {job.get('ThoiGianXong', 'N/A')}")
                            if st.button("Xóa ca", key=f"del_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                                st.rerun()

st.markdown('<p class="header-style">🗓️ TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)

st.markdown('<p class="header-style">⏭️ TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
