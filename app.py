import streamlit as st
from supabase import create_client

# 1. Kết nối Supabase (GỌI TÊN BIẾN từ Secrets - ĐÚNG CÁCH)
# Lưu ý: "SUPABASE_URL" và "SUPABASE_KEY" là tên bạn đặt trong mục Settings -> Secrets trên web
url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]
supabase = create_client(url, key)

# ... (các phần bên dưới giữ nguyên)

# Cấu hình trang tối ưu cho di động
st.set_page_config(page_title="Thành Viễn Admin", layout="centered")

st.title("❄️ Điện lạnh Thành Viễn")

# 2. Tạo Menu dạng TAB (Mobile First)
tab1, tab2 = st.tabs(["📝 NHẬP VIỆC", "🔍 TRA CỨU"])

# --- TAB 1: NHẬP CÔNG VIỆC MỚI ---
with tab1:
    st.subheader("Ghi nhận ca máy mới")
    with st.form("input_form", clear_on_submit=True):
        noidung = st.text_area("Nội dung công việc (Địa chỉ, lỗi máy...)", placeholder="VD: Sửa máy giặt Q.Gò Vấp...")
        submit = st.form_submit_button("💾 LƯU HỆ THỐNG")
        
        if submit and noidung:
            try:
                # Gửi dữ liệu lên bảng 'LichLamViec'
                # Cột 'Viec' phải khớp 100% với tên cột trên Supabase của bạn
                data = supabase.table("LichLamViec").insert({"Viec": noidung}).execute()
                st.success("✅ Đã lưu thành công!")
                st.balloons()
            except Exception as e:
                st.error(f"Lỗi: {e}")

# --- TAB 2: THÔNG TIN & TÌM KIẾM ---
with tab2:
    st.subheader("Danh sách lịch làm")
    search_query = st.text_input("🔍 Tìm tên khách, địa chỉ hoặc thiết bị...")
    
    try:
        # Lấy dữ liệu từ Supabase, sắp xếp cái mới nhất lên đầu (id giảm dần)
        response = supabase.table("LichLamViec").select("*").order("id", desc=True).execute()
        records = response.data
        
        if records:
            # Bộ lọc tìm kiếm thông minh
            if search_query:
                records = [r for r in records if search_query.lower() in str(r.get('Viec', '')).lower()]
            
            # Hiển thị dạng Card cho dễ đọc trên điện thoại
            for item in records:
                with st.container(border=True):
                    st.write(f"**ID:** {item['id']}")
                    st.write(f"📍 {item.get('Viec', 'N/A')}")
                    # Nếu bạn có cột created_at (mặc định của Supabase)
                    if 'created_at' in item:
                        st.caption(f"⏰ {item['created_at'][:16].replace('T', ' ')}")
        else:
            st.info("Chưa có dữ liệu nào.")
    except Exception as e:
        st.error(f"Lỗi tải dữ liệu: {e}")