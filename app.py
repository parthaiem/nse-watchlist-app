import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go

st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="datarefresh")  # 10 minutes

# --- Page Routing ---
query_params = st.experimental_get_query_params()
detail_symbol = query_params.get("symbol", [None])[0]

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

# --- Detail Page ---
if detail_symbol:
    stock = yf.Ticker(detail_symbol)
    st.header(f"🔍 Details for {stock.info.get('shortName', detail_symbol)}")

    # Chart
    hist = stock.history(period="6mo")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
    fig.update_layout(title='6 Month Price Chart', xaxis_title='Date', yaxis_title='Price (INR)')
    st.plotly_chart(fig, use_container_width=True)

    # Info
    info = stock.info
    st.markdown("### Company Info")
    st.write(info.get("longBusinessSummary", "No business summary available."))

    st.markdown("### Key Metrics")
    st.write({
        "P/E Ratio": info.get("trailingPE"),
        "Market Cap": info.get("marketCap"),
        "Revenue": info.get("totalRevenue"),
        "Net Income": info.get("netIncomeToCommon")
    })

    if st.button("⬅ Back to Watchlist"):
        st.experimental_set_query_params()
        st.rerun()
    st.stop()

# --- Watchlist Page ---
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
    data_rows = []

    for symbol in watchlist:
        try:
            stock = yf.Ticker(symbol)

            hist_1mo = stock.history(period="1mo")
            hist_1wk = stock.history(period="7d")
            hist_1y = stock.history(period="1y")

            current_price = hist_1mo["Close"][-1]
            previous_close = hist_1mo["Close"][-2]
            day_change = ((current_price - previous_close) / previous_close) * 100
            week_change = ((hist_1wk["Close"][-1] - hist_1wk["Close"][0]) / hist_1wk["Close"][0]) * 100
            month_change = ((hist_1mo["Close"][-1] - hist_1mo["Close"][0]) / hist_1mo["Close"][0]) * 100

            high_52 = hist_1y["High"].max()
            low_52 = hist_1y["Low"].min()

            company = stock_dict.get(symbol, "Unknown")

            data_rows.append({
                "Symbol": symbol,
                "Company": f"[{company}](?symbol={symbol})",
                "Current Price": round(current_price, 2),
                "Day Change (%)": f"{day_change:+.2f}%",
                "1-Week Change (%)": f"{week_change:+.2f}%",
                "1-Month Change (%)": f"{month_change:+.2f}%",
                "52-Week High": f"{high_52:.2f}",
                "52-Week Low": f"{low_52:.2f}"
            })

        except Exception as e:
            st.error(f"Error fetching {symbol}: {e}")

    df = pd.DataFrame(data_rows)

    def color_percent(val):
        try:
            val_float = float(val.strip('%+'))
            color = 'green' if val_float >= 0 else 'red'
            return f'color: {color}'
        except:
            return ''

    st.dataframe(df.style.applymap(color_percent, subset=[
        "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"]), use_container_width=True)

    csv = df.to_csv(index=False)
    st.download_button("📥 Export to CSV", csv, file_name="watchlist.csv", mime="text/csv")

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
