import streamlit as st
from supabase import create_client

# Kết nối
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn Mobile", layout="wide")

# --- 1. Ô NHẬP MÃ NHÂN VIÊN (Gọn nhẹ ở góc trên) ---
col_head1, col_head2 = st.columns([1, 2])
with col_head1:
    ma_tho = st.text_input("Mã Thợ:", placeholder="VD: TV01", type="password")

if not ma_tho:
    st.info("💡 Vui lòng nhập Mã Thợ để làm việc.")
    st.stop()

# --- 2. CHỈ SỐ TÓM TẮT NẰM NGANG (Dùng 3 cột nhỏ) ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

cho = len([t for t in data if t.get('TrangThai') == "Chờ xử lý"])
dang = len([t for t in data if t.get('TrangThai') == "Đang làm"])
xong = len([t for t in data if t.get('TrangThai') == "Hoàn thành"])

# Mẹo: Dùng st.columns để ép các chỉ số nằm ngang trên mobile
c1, c2, c3 = st.columns(3)
c1.metric("🔴 Chờ", cho)
c2.metric("🟡 Làm", dang)
c3.metric("🟢 Xong", xong)

st.divider()

# --- 3. TAB CHÍNH ---
t1, t2 = st.tabs(["➕ NHẬP VIỆC", "📋 DANH SÁCH"])

with t1:
    with st.form("f_nhap", clear_on_submit=True):
        nd = st.text_area("Nội dung công việc & Địa chỉ")
        if st.form_submit_button("LƯU HỆ THỐNG"):
            supabase.table("LichLamViec").insert({
                "Viec": nd, 
                "TrangThai": "Chờ xử lý",
                "NguoiThucHien": ma_tho
            }).execute()
            st.success("Đã ghi sổ!")
            st.rerun()

with t2:
    # Sắp xếp việc mới nhất lên đầu
    for task in sorted(data, key=lambda x: x['id'], reverse=True):
        stt = task.get('TrangThai', 'Chờ xử lý')
        icon = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
        
        # Hiển thị tóm tắt ngắn gọn
        with st.container(border=True):
            col_info, col_btn = st.columns([3, 1])
            with col_info:
                st.markdown(f"**{icon} {task['Viec'][:50]}...**")
            
            with st.expander("Xem chi tiết & Cập nhật"):
                st.write(f"📝 {task['Viec']}")
                st.caption(f"Thợ: {task.get('NguoiThucHien')} | ID: #{task['id']}")
                
                # Nút xử lý nhanh
                if stt == "Chờ xử lý":
                    if st.button(f"🚀 Nhận việc", key=f"rec_{task['id']}"):
                        supabase.table("LichLamViec").update({"TrangThai": "Đang làm"}).eq("id", task['id']).execute()
                        st.rerun()
                elif stt == "Đang làm":
                    vt = st.text_input("Vật tư/Ghi chú:", key=f"note_{task['id']}")
                    if st.button(f"✔️ Xong", key=f"done_{task['id']}"):
                        supabase.table("LichLamViec").update({
                            "TrangThai": "Hoàn thành",
                            "VatTuSuDung": vt
                        }).eq("id", task['id']).execute()
                        st.rerun()
