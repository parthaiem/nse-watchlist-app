from supabase import create_client
import streamlit as st

@st.cache_resource
def get_supabase_client():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_ANON_KEY"]
    return create_client(url, key)

supabase = get_supabase_client()

def sign_in(email, password):
    return supabase.auth.sign_in_with_password({"email": email, "password": password})

def sign_up(email, password):
    return supabase.auth.sign_up({"email": email, "password": password})

def add_to_watchlist(user_id, symbol):
    return supabase.table("watchlists").insert({"user_id": user_id, "symbol": symbol}).execute()

def get_watchlist(user_id):
    result = supabase.table("watchlists").select("symbol").eq("user_id", user_id).execute()
    return [row["symbol"] for row in result.data]

def remove_from_watchlist(user_id, symbol):
    return supabase.table("watchlists").delete().eq("user_id", user_id).eq("symbol", symbol).execute()