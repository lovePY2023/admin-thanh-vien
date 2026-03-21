import streamlit as st
from supabase import create_client

# Kết nối
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

st.set_page_config(page_title="Thành Viễn Admin", layout="centered")

# --- PHẦN 1: ĐỊNH DANH ---
st.sidebar.title("🔑 Đăng nhập")
ma_tho = st.sidebar.text_input("Nhập Mã Thợ (VD: TV01)", type="password")

if not ma_tho:
    st.info("Vui lòng nhập Mã Thợ ở thanh bên trái để bắt đầu.")
    st.stop()

st.title(f"🛠️ Hệ thống Thành Viễn - Thợ: {ma_tho}")

# --- PHẦN 2: TÓM TẮT CHỈ SỐ ---
res = supabase.table("LichLamViec").select("*").execute()
data = res.data

cho = len([t for t in data if t.get('TrangThai') == "Chờ xử lý"])
dang = len([t for t in data if t.get('TrangThai') == "Đang làm"])
xong = len([t for t in data if t.get('TrangThai') == "Hoàn thành"])

c1, c2, c3 = st.columns(3)
c1.metric("🔴 Chờ", cho)
c2.metric("🟡 Làm", dang)
c3.metric("🟢 Xong", xong)

# --- PHẦN 3: GIAO DIỆN TAB ---
t1, t2 = st.tabs(["➕ Nhập việc mới", "📋 Danh sách việc"])

with t1:
    with st.form("f_nhap"):
        nd = st.text_area("Nội dung (Khách hàng, địa chỉ, tình trạng máy...)")
        if st.form_submit_button("Gửi dữ liệu"):
            supabase.table("LichLamViec").insert({
                "Viec": nd, 
                "TrangThai": "Chờ xử lý",
                "NguoiThucHien": ma_tho
            }).execute()
            st.success("Đã thêm việc thành công!")
            st.rerun()

with t2:
    for task in data:
        stt = task.get('TrangThai', 'Chờ xử lý')
        bg_color = "🔴" if stt == "Chờ xử lý" else "🟡" if stt == "Đang làm" else "✅"
        
        with st.expander(f"{bg_color} {task['Viec'][:40]}..."):
            st.write(f"**Chi tiết:** {task['Viec']}")
            st.write(f"**Người làm:** {task.get('NguoiThucHien')}")
            
            # Nút bấm cập nhật trạng thái
            if stt == "Chờ xử lý":
                if st.button(f"🚀 Bắt đầu làm #{task['id']}"):
                    supabase.table("LichLamViec").update({"TrangThai": "Đang làm"}).eq("id", task['id']).execute()
                    st.rerun()
            elif stt == "Đang làm":
                vt = st.text_input(f"Vật tư đã dùng cho ca #{task['id']}", placeholder="VD: 1kg gas, 2 tụ...")
                if st.button(f"✔️ Hoàn thành #{task['id']}"):
                    supabase.table("LichLamViec").update({
                        "TrangThai": "Hoàn thành",
                        "VatTuSuDung": vt
                    }).eq("id", task['id']).execute()
                    st.rerun()
