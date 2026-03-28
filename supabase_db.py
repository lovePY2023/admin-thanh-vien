import streamlit as st
from supabase import create_client, Client

# Kết nối lấy từ Secrets của Streamlit (Không dán Key trực tiếp vào đây)
@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

# Các hàm thao tác dữ liệu bạn có thể viết sẵn ở đây
def load_products():
    return supabase.table("products").select("*").execute()

def insert_order(data):
    return supabase.table("orders").insert(data).execute()
