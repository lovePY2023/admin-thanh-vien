import streamlit as st
from supabase import create_client
from datetime import datetime, timedelta
import pytz

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

# --- CSS GIAO DIỆN ---
st.markdown("""
    <style>
    .header-style { font-size:20px; font-weight:bold; color: #1E88E5; border-bottom: 2px solid #1E88E5; margin-bottom: 15px; }
    .today-label { color: white; background-color: #ff4b4b; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
    .job-title { font-size: 17px; font-weight: bold; border-bottom: 1px solid #eee; padding-bottom: 5px; }
    .status-badge { font-size: 11px; padding: 2px 5px; border-radius: 4px; background-color: #f0f2f6; color: #555; font-weight: normal; }
    .note-box { background-color: #fff9c4; padding: 5px; border-radius: 5px; font-size: 13px; border-left: 3px solid #fbc02d; margin-top: 5px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. XỬ LÝ THỜI GIAN ---
tz = pytz.timezone('Asia/Ho_Chi_Minh')
now_vn = datetime.now(tz)
today = now_vn.date()
tomorrow = today + timedelta(days=1)
start_week = today - timedelta(days=today.weekday())
this_week = [start_week + timedelta(days=i) for i in range(7)]
next_week = [start_week + timedelta(days=i+7) for i in range(7)]
days_vn = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ Nhật"]

# --- 3. LẤY DỮ LIỆU ---
res = supabase.table("LichLamViec").select("*").execute()
all_data = res.data

st.title("❄️ Điều hành Thành Viễn")

# --- PHẦN FORM NHẬP ---
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
        ghi_chu = st.text_area("Yêu cầu/Tình trạng ban đầu")
        if st.form_submit_button("LƯU VÀO HỆ THỐNG"):
            if ten_kh and sdt:
                supabase.table("LichLamViec").insert({
                    "TenKH": ten_kh, "SoDT": sdt, "DiaChi": dia_chi,
                    "KhuVuc": khu_vuc, "CongViec": f"{cv_chon} | {ghi_chu}",
                    "NgayHen": str(ngay), "TrangThai": "Chờ xử lý",
                    "TrangThaiCSKH": "Chưa gọi"
                }).execute()
                st.rerun()

# ==========================================
# HÀM HIỂN THỊ GRID
# ==========================================
def render_full_grid(days_list):
    for i, d in enumerate(days_list):
        jobs = [j for j in all_data if j.get('NgayHen') == str(d)]
        nhan = f' <span class="today-label">HÔM NAY</span>' if d == today else ""
        st.markdown(f"#### {days_vn[i]} ({d.strftime('%d/%m')}){nhan}", unsafe_allow_html=True)
        
        if not jobs:
            st.caption("Trống lịch")
        else:
            cols = st.columns(2)
            for idx, job in enumerate(jobs):
                with cols[idx % 2]:
                    stt = job.get('TrangThai', 'Chờ xử lý')
                    cskh = job.get('TrangThaiCSKH', 'Chưa gọi')
                    
                    with st.container(border=True):
                        st.markdown(f"<div class='job-title'>{job['TenKH']} <span class='status-badge'>{cskh}</span></div>", unsafe_allow_html=True)
                        st.markdown(f"📍 **{job['KhuVuc']}**: {job['DiaChi']}")
                        st.markdown(f"🛠️ **Việc**: {job.get('CongViec')}")
                        
                        # Hiển thị Ghi chú thêm nếu đã có dữ liệu
                        if job.get("GhiChuThem"):
                            st.markdown(f"<div class='note-box'>📝 <b>Ghi chú:</b> {job['GhiChuThem']}</div>", unsafe_allow_html=True)
                        
                        st.divider()

                        # 1. NÚT GỌI (Luôn hiện trên cùng)
                        st.markdown(f'<a href="tel:{job["SoDT"]}" style="text-decoration:none; display:block; text-align:center; background:#e3f2fd; color:#1e88e5; padding:8px; border-radius:5px; font-weight:bold; border:1px solid #bbdefb; margin-bottom:10px;">📞 GỌI KHÁCH: {job["SoDT"]}</a>', unsafe_allow_html=True)
                        
                        # 2. XỬ LÝ CSKH (Chưa gọi)
                        if cskh == "Chưa gọi":
                            col_cskh1, col_cskh2 = st.columns(2)
                            if col_cskh1.button(f"✅ KHÁCH CHỐT", key=f"chot_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"TrangThaiCSKH": "Khách Chốt"}).eq("id", job['id']).execute()
                                st.rerun()
                            if col_cskh2.button(f"❌ KHÁCH HỦY", key=f"huy_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"TrangThaiCSKH": "Khách Hủy", "TrangThai": "Hoàn thành"}).eq("id", job['id']).execute()
                                st.rerun()

                        # 3. XỬ LÝ THỢ (Chỉ khi khách đã Chốt và chưa xong)
                        if cskh == "Khách Chốt" and stt != "Hoàn thành":
                            # Ô nhập ghi chú đa năng (CSKH hoặc Thợ đều gõ được)
                            ghi_chu_input = st.text_input("Ghi chú thêm (Vật tư/Dặn dò):", key=f"note_{job['id']}", value=job.get("GhiChuThem", ""))
                            
                            col_action1, col_action2 = st.columns(2)
                            if col_action1.button(f"💾 LƯU GHI CHÚ", key=f"save_{job['id']}", use_container_width=True):
                                supabase.table("LichLamViec").update({"GhiChuThem": ghi_chu_input}).eq("id", job['id']).execute()
                                st.rerun()
                                
                            if col_action2.button(f"✅ XONG CA", key=f"done_{job['id']}", use_container_width=True, type="primary"):
                                time_now = datetime.now(tz).strftime("%H:%M - %d/%m/%Y")
                                supabase.table("LichLamViec").update({
                                    "TrangThai": "Hoàn thành",
                                    "GhiChuThem": ghi_chu_input,
                                    "ThoiGianXong": time_now
                                }).eq("id", job['id']).execute()
                                st.rerun()

                        # 4. HIỂN THỊ KẾT QUẢ CUỐI CÙNG
                        if stt == "Hoàn thành":
                            if cskh == "Khách Hủy":
                                st.error("Lịch đã Hủy")
                            else:
                                st.success(f"Hoàn thành lúc: {job.get('ThoiGianXong', 'N/A')}")

                        # 5. NÚT XÓA (Dưới cùng)
                        if st.button(f"🗑️ Xóa ca", key=f"del_{job['id']}", use_container_width=True, type="secondary"):
                            supabase.table("LichLamViec").delete().eq("id", job['id']).execute()
                            st.rerun()

# --- HIỂN THỊ ---
st.markdown('<p class="header-style">🗓️ LỊCH TRÌNH TUẦN NÀY</p>', unsafe_allow_html=True)
render_full_grid(this_week)
st.markdown('<p class="header-style">⏭️ KẾ HOẠCH TUẦN TIẾP THEO</p>', unsafe_allow_html=True)
render_full_grid(next_week)
