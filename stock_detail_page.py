import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

st.set_page_config(page_title="Stock Details", layout="wide")

# --- Read stock symbol from query params ---
query_params = st.experimental_get_query_params()
symbol = query_params.get("stock", [None])[0]

if not symbol:
    st.error("No stock selected.")
    st.stop()

ticker = yf.Ticker(symbol)
info = ticker.info

st.title(f"📊 {info.get('longName', symbol)} ({symbol})")

# --- Price Chart ---
st.subheader("📈 Price Chart (Last 6 Months)")

hist = ticker.history(period="6mo")
if hist.empty:
    st.warning("No historical data available.")
else:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=hist.index, y=hist["Close"],
        mode='lines', name="Close Price"
    ))
    fig.update_layout(title=f"{symbol} Closing Price", xaxis_title="Date", yaxis_title="Price (INR)")
    st.plotly_chart(fig, use_container_width=True)

# --- Key Financial Metrics ---
st.subheader("📌 Key Metrics")

col1, col2, col3 = st.columns(3)
col1.metric("📈 Current Price", f"₹{hist['Close'][-1]:.2f}")
col2.metric("52W High", f"₹{hist['High'].max():.2f}")
col3.metric("52W Low", f"₹{hist['Low'].min():.2f}")

col4, col5, col6 = st.columns(3)
col4.metric("🧮 P/E Ratio", f"{info.get('trailingPE', 'N/A')}")
col5.metric("📊 EPS (TTM)", f"{info.get('trailingEps', 'N/A')}")
col6.metric("🏢 Market Cap", f"{info.get('marketCap', 'N/A'):,}")

# --- Profit and Sales ---
st.subheader("📋 Financial Summary (Latest)")

st.write(f"**Net Profit:** ₹{info.get('netIncomeToCommon', 'N/A'):,}")
st.write(f"**Revenue (Net Sales):** ₹{info.get('totalRevenue', 'N/A'):,}")
st.write(f"**Book Value:** ₹{info.get('bookValue', 'N/A')}")
st.write(f"**ROE:** {info.get('returnOnEquity', 'N/A'):.2%}" if info.get("returnOnEquity") else "ROE: N/A")

# --- Company Overview ---
st.subheader("🏢 Company Overview")
business_summary = info.get("longBusinessSummary", "No company description available.")
st.write(business_summary)

# --- Back Button ---
st.markdown("### 🔙 [Back to Watchlist](./)")
