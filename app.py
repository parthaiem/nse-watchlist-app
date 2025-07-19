import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go

st.set_page_config(page_title="📈 NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="autorefresh")

st.title("📊 NSE Stock Watchlist")

# --- Login Section ---
if "user" not in st.session_state:
    username = st.text_input("Enter your name to continue:")
    if st.button("Login"):
        if username:
            st.session_state.user = username
            st.rerun()
        else:
            st.warning("Please enter a name to login.")
else:
    user = st.session_state.user
    st.success(f"Logged in as: {user}")
    st.button("Logout", on_click=lambda: st.session_state.clear())

    # --- Stock Symbol Mapping ---
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

    watchlist = get_watchlist(user)

    st.subheader("➕ Add Stocks to Watchlist")
    add_name = st.selectbox("Choose a stock", all_names)
    if st.button("Add Stock"):
        symbol = name_to_symbol[add_name]
        if symbol not in watchlist:
            add_to_watchlist(user, symbol)
            st.success(f"{add_name} added to your watchlist!")
            st.rerun()

    st.subheader("📈 Your Watchlist")

    if not watchlist:
        st.info("No stocks in your watchlist yet.")
    else:
        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)

                hist_1mo = stock.history(period="1mo")
                hist_1wk = stock.history(period="7d")
                hist_1y = stock.history(period="1y")

                current_price = hist_1mo["Close"][-1]
                prev_close = hist_1mo["Close"][-2]
                day_change = ((current_price - prev_close) / prev_close) * 100
                week_change = ((hist_1wk["Close"][-1] - hist_1wk["Close"][0]) / hist_1wk["Close"][0]) * 100
                month_change = ((hist_1mo["Close"][-1] - hist_1mo["Close"][0]) / hist_1mo["Close"][0]) * 100
                high_52 = hist_1y["High"].max()
                low_52 = hist_1y["Low"].min()
                company = stock_dict.get(symbol, "Unknown")

                with st.expander(f"{symbol} - {company}"):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    c1.metric("💰 Current Price", f"₹{round(current_price, 2)}", f"{round(day_change, 2)}%")
                    c2.metric("📅 1-Week Change", f"{round(week_change, 2)}%", delta_color="inverse")
                    c3.metric("📆 1-Month Change", f"{round(month_change, 2)}%", delta_color="inverse")

                    c4, c5 = st.columns(2)
                    c4.metric("📈 52-Week High", f"₹{round(high_52, 2)}")
                    c5.metric("📉 52-Week Low", f"₹{round(low_52, 2)}")

                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=hist_1mo.index, y=hist_1mo["Close"],
                                             mode='lines', name=symbol, line=dict(color="royalblue")))
                    fig.update_layout(title="1-Month Price Trend", xaxis_title="Date", yaxis_title="Price (₹)",
                                      margin=dict(l=20, r=20, t=30, b=20), height=250)
                    st.plotly_chart(fig, use_container_width=True)

                    if st.button("❌ Remove from Watchlist", key=f"rm_{symbol}"):
                        remove_from_watchlist(user, symbol)
                        st.rerun()

            except Exception as e:
                st.error(f"Error fetching data for {symbol}: {e}")

    # --- Export Data ---
    if watchlist:
        export_data = []
        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1mo")
                current_price = hist["Close"][-1]
                prev_close = hist["Close"][-2]
                change = ((current_price - prev_close) / prev_close) * 100
                high_52 = stock.history(period="1y")["High"].max()
                low_52 = stock.history(period="1y")["Low"].min()
                week_change = ((stock.history(period="7d")["Close"][-1] - stock.history(period="7d")["Close"][0]) / stock.history(period="7d")["Close"][0]) * 100
                month_change = ((hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]) * 100

                export_data.append({
                    "Symbol": symbol,
                    "Company": stock_dict.get(symbol, "Unknown"),
                    "Current Price": round(current_price, 2),
                    "Day Change (%)": round(change, 2),
                    "1-Week Change (%)": round(week_change, 2),
                    "1-Month Change (%)": round(month_change, 2),
                    "52-Week High": round(high_52, 2),
                    "52-Week Low": round(low_52, 2)
                })
            except:
                continue

        df = pd.DataFrame(export_data)
        st.download_button("📥 Download Watchlist CSV", df.to_csv(index=False), file_name="watchlist.csv", mime="text/csv")

    # --- Footer ---
    st.markdown("---")
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1b/Angel_One_Logo.svg", width=100)
    st.markdown("""
        <div style='text-align: center; font-size: 16px; padding-top: 20px;'>
            <strong>📊 FinSmart Wealth Advisory</strong><br>
            Partha Chakraborty<br><br>
            <a href="tel:+91XXXXXXXXXX">📞 Call</a> &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="https://wa.me/91XXXXXXXXXX">💬 WhatsApp</a> &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="https://angel-one.onelink.me/Wjgr/m8njiek1">📂 Open DMAT</a>
        </div>
    """, unsafe_allow_html=True)
