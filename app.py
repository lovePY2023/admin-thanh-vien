import streamlit as st
from supabase import create_client

# ==========================================
# 🔑 PHẦN DÁN MÃ API (LẤY TỪ SUPABASE)
# ==========================================
SUPABASE_URL = "https://xflksccmmebvjtsdeyxm.supabase.co" 
SUPABASE_KEY = "sb_publishable_ivhaobRcgHAGNKMwCg61aA_Dsxnayno"

# Kết nối hệ thống
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# 🎨 GIAO DIỆN QUẢN LÝ LỊCH LÀM VIỆC
# ==========================================
st.set_page_config(page_title="Lịch Làm Việc Thành Viễn", layout="wide")

st.title("📅 QUẢN LÝ LỊCH LÀM VIỆC - THÀNH VIỄN")
st.markdown("---")

# Menu điều hướng
menu = st.sidebar.radio("CHỨC NĂNG", ["📋 Xem lịch làm việc", "➕ Thêm việc mới"])

# --- TAB 1: XEM LỊCH LÀM VIỆC ---
if menu == "📋 Xem lịch làm việc":
    st.subheader("🔍 Danh sách công việc đã ghi chú")
    
    # Ô tìm kiếm nội dung công việc
    search_query = st.text_input("Tìm kiếm nội dung công việc...")

    try:
        # Lấy dữ liệu từ bảng LichLamViec
        res = supabase.table("LichLamViec").select("*").order("id", desc=True).execute()
        data = res.data

        if data:
            # Lọc dữ liệu nếu người dùng nhập ô tìm kiếm
            if search_query:
                data = [i for i in data if search_query.lower() in str(i['Viec']).lower()]
            
            # Hiển thị bảng
            st.dataframe(data, use_container_width=True, hide_index=True)
        else:
            st.info("Chưa có lịch làm việc nào được tạo.")
    except Exception as e:
        st.error(f"Lỗi: Không tìm thấy bảng hoặc lỗi kết nối. ({e})")

# --- TAB 2: THÊM VIỆC MỚI ---
elif menu == "➕ Thêm việc mới":
    st.subheader("📝 Ghi chú công việc mới")
    
    with st.form("form_add_work"):
        # Nhập nội dung công việc vào cột 'Viec'
        noidung_viec = st.text_area("Nội dung công việc (Ví dụ: Sửa máy giặt nhà chị Lan - Gò Vấp)")
        
        submit_btn = st.form_submit_button("💾 LƯU LỊCH LÀM VIỆC")

        if submit_btn:
            if noidung_viec:
                try:
                    # Gửi dữ liệu vào cột 'Viec'
                    # Cột ID và Time stamp thường sẽ tự động nhảy nếu bạn cài 'Default value' trên Supabase
                    new_record = {"Viec": noidung_viec}
                    supabase.table("LichLamViec").insert(new_record).execute()
                    
                    st.success("✅ Đã lưu công việc thành công!")
                    st.balloons() 
                except Exception as e:
                    st.error(f"Lỗi khi lưu dữ liệu: {e}")
            else:
                st.warning("Vui lòng nhập nội dung công việc!")

# Chân trang
st.sidebar.markdown("---")
st.sidebar.info("Mẹo: Cột ID và Time stamp sẽ được hệ thống tự động tạo khi bạn lưu.")