import streamlit as st
from supabase import create_client, Client

# Kết nối lấy từ Secrets của Streamlit Cloud
@st.cache_resource
def get_supabase_client():
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Lỗi cấu hình Secrets: {e}")
        return None

# Biến dùng chung cho toàn bộ App
supabase = get_supabase_client()

def load_products():
    """Lấy danh sách sản phẩm từ bảng products"""
    if supabase:
        try:
            return supabase.table("products").select("*").execute()
        except Exception as e:
            st.error(f"Lỗi tải sản phẩm: {e}")
    return None

def insert_order(order_data):
    """Lưu đơn hàng vào bảng orders"""
    if supabase:
        try:
            return supabase.table("orders").insert(order_data).execute()
        except Exception as e:
            st.error(f"Lỗi lưu đơn hàng: {e}")
    return None
