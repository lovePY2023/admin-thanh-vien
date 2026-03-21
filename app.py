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

# --- CSS GIAO DIỆN CẬP NHẬT ---
st.markdown("""
    <style>
    .header-style { font-size:20px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 15px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left:10px; }
    .tomorrow-label { color: white; background-color: #ffa500; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-left:10px; }
    
    /* Khung ghi chú màu vàng */
    .note-box { background-color: #fffde7; padding: 10px; border-radius: 5px; font-size: 14px; border-left: 5px solid #fbc02d; margin: 10px 0; color: #333; }
    
    /* Khung thông báo Đã Chốt màu xanh lá */
    .chot-box { background-color: #e8f5e9; padding: 10px; border-radius: 5px; font-size: 14px; border-left: 5px solid #4caf50; margin: 10px 0; color: #2e7d32; font-weight: bold; }
    
    /* Tùy chỉnh nút bấm để không bị thô */
    .stButton>button { border-radius: 5px; }
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
                    chot_hien_tai = job.get('ChotViec', 'Chưa Gọi')
                    if not chot_hien_tai: chot_hien_tai = "Chưa Gọi"
                    
                    with st.container(border=True):
                        st.markdown(f"### {job['TenKH']}")
                        st.markdown(f"📍 **{job['KhuVuc']}**: {job['DiaChi']}")
                        
                        # HIỆN DÒNG MÀU XANH KHI ĐÃ CHỐT
                        if chot_hien_tai == "Đã Chốt":
                            st.markdown(f"<div class='chot-box'>✅ ĐÃ CHỐT LỊCH THÀNH CÔNG</div>", unsafe_allow_html=True)
                        
                        st.markdown(f"🛠️ **Việc**: {job.get('CongViec', 'N/A')}")
                        
                        if job.get("GhiChuThem"):
                            st.markdown(f"<div class='note-box'>📝 Ghi chú: {job['GhiChuThem']}</div>", unsafe_allow_html=True)
                        
                        st.divider()

                        # 1. NÚT GỌI
                        st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none; display:block; text-align:center; background:#e3f2fd; color:#1e88e5; padding:10px; border-radius:8px; font-weight:bold; border:1px solid #bbdefb; margin-bottom:12px;">📞 GỌI: {job["SoDT"]}</a>', unsafe_allow_html=True)
                        
                        # 2. Ô CHỌN TRẠNG THÁI CSKH
                        index_chot = DANH_MUC_CHOT.index(chot_hien_tai) if chot_hien_tai in DANH_MUC_CHOT else 0
                        moi_chot = st.selectbox("Cập nhật trạng thái:", DANH_MUC_CHOT, index=index_chot, key=f"sel_{job['id']}")
                        
                        if moi_chot != chot_hien_tai:
                            update_data = {"ChotViec": moi_chot}
                            if moi_chot == "Từ Chối": update_data["TrangThai"] = "Hoàn thành"
                            supabase.table("LichLamViec").update(update_data).eq("id", job['id']).execute()
                            st.rerun()

                        # 3. GHI CHÚ & HOÀN THÀNH
                        if stt != "Hoàn thành":
                            ghi_chu_input = st.text_input("Ghi chú/Vật tư:", key=f"nt_{job['id']}", value=job.get("GhiChuThem", ""))
                            
                            b1, b2 = st.columns(2)
                            if b1.button(f"💾 LƯU", key=f"sv_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"GhiChuThem": ghi_chu_input}).eq("id", job['id']).execute()
                                st.rerun()
                            # Nút Hoàn thành đổi sang màu Primary (Xanh dương) thay vì Đỏ
                            if b2.button(f"✅ HOÀN THÀNH", key=f"dn_{job['id']}", use_container_width=True, type="primary"):
                                t_now = datetime.now(tz).strftime("%H:%M - %d/%m/%Y")
                                supabase.table("LichLamViec").update({
                                    "TrangThai": "Hoàn thành", "GhiChuThem": ghi_chu_input, "ThoiGianXong": t_now
                                }).eq("id", job['id']).execute()
                                st.rerun()
                        else:
                            if chot_hien_tai == "Từ Chối": st.error("Khách đã từ chối")
                            else: st.success(f"✅ Xong lúc: {job.get('ThoiGianXong', 'N/A')}")

                        if st.button(f"🗑️ Xóa", key=f"dl_{job['id']}", use_container_width=True):
                            supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                            st.rerun()

st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_grid(this_week)
st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_grid(next_week)
