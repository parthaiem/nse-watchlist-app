import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go

def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}'
    except:
        return ''

st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="datarefresh")

# --- Top bar layout: logo + title (left), login/logout (right) ---
top_col1, top_col2, top_col3 = st.columns([1, 4, 2])

with top_col1:
    st.image("logo.jpg", width=100)

with top_col2:
    st.markdown("<h1 style='padding-top: 10px;'>📈 NSE Stock Watchlist</h1>", unsafe_allow_html=True)

with top_col3:
    if "user" in st.session_state:
        st.markdown(f"<p style='text-align:right; padding-top: 25px;'>👤 Logged in as <strong>{st.session_state.user}</strong></p>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()
    else:
        username = st.text_input("Enter your name to continue:", key="login_input")
        if st.button("Login", key="login_btn"):
            if username:
                st.session_state.user = username
                st.rerun()
            else:
                st.warning("Please enter a name to login.")
        st.stop()

# --- Stock Dictionary ---
stock_dict = {
    "TCS.NS": "TATA CONSULTANCY SERVICES",
    "INFY.NS": "INFOSYS",
    "WIPRO.NS": "WIPRO",
    "HCLTECH.NS": "HCL TECHNOLOGIES",
    "RELIANCE.NS": "RELIANCE INDUSTRIES",
    "SBIN.NS": "STATE BANK OF INDIA",
    "ICICIBANK.NS": "ICICI BANK",
    "TECHM.NS": "TECH MAHINDRA"
}

name_to_symbol = {v: k for k, v in stock_dict.items()}
all_names = list(name_to_symbol.keys())

user = st.session_state.user
watchlist = get_watchlist(user)

st.subheader("📌 Add to Watchlist")
add_name = st.selectbox("Select stock to add", all_names)
if st.button("➕ Add"):
    symbol = name_to_symbol[add_name]
    if symbol not in watchlist:
        add_to_watchlist(user, symbol)
        st.success(f"{add_name} added!")
        st.rerun()

st.subheader("📉 Your Watchlist")

if not watchlist:
    st.info("Your watchlist is empty.")
else:
    for symbol in watchlist:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="6mo")
            info = stock.info

            current_price = hist["Close"][-1]
            previous_close = hist["Close"][-2]
            day_change = ((current_price - previous_close) / previous_close) * 100

            company = stock_dict.get(symbol, "Unknown")
            pe_ratio = info.get("trailingPE", "N/A")
            revenue = info.get("totalRevenue", "N/A")
            net_profit = info.get("grossProfits", "N/A")
            description = info.get("longBusinessSummary", "No description available.")

            with st.expander(f"🔍 {symbol} - {company}"):
                st.markdown(f"### {company} ({symbol})")
                st.markdown(f"**Current Price**: ₹{current_price:.2f}")
                st.markdown(f"**Day Change**: {day_change:+.2f}%")
                st.markdown(f"**P/E Ratio**: {pe_ratio}")
                st.markdown(f"**Total Revenue**: {revenue}")
                st.markdown(f"**Net Profit**: {net_profit}")
                st.markdown("**Business Summary:**")
                st.info(description)

                fig = go.Figure()
                fig.add_trace(go.Scatter(x=hist.index, y=hist["Close"], mode="lines", name="Close Price"))
                fig.update_layout(title="Price Trend (6 Months)", xaxis_title="Date", yaxis_title="Price")
                st.plotly_chart(fig, use_container_width=True)

        except Exception as e:
            st.error(f"Error loading {symbol}: {e}")

# --- Footer ---
st.markdown("---")
st.image("https://upload.wikimedia.org/wikipedia/commons/1/1b/Angel_One_Logo.svg", width=100)
st.markdown(f"""
    <div style='text-align: center; font-size: 16px; padding-top: 20px;'>
        <strong>📊 FinSmart Wealth Advisory</strong><br>
        Partha Chakraborty<br><br>
        <a href="tel:+91XXXXXXXXXX">📞 Call</a> &nbsp;&nbsp;|&nbsp;&nbsp;
        <a href="https://wa.me/91XXXXXXXXXX">💬 WhatsApp</a> &nbsp;&nbsp;|&nbsp;&nbsp;
        <a href="https://angel-one.onelink.me/Wjgr/m8njiek1">📂 Open DMAT</a>
    </div>
""", unsafe_allow_html=True)
