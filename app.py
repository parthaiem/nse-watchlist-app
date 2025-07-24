import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.graph_objs as go

st.set_page_config(page_title="📊 Stock Details", layout="wide")

params = st.query_params
symbol = params.get("symbol", None)

if not symbol:
    st.error("No stock symbol provided in URL.")
    st.stop()

stock = yf.Ticker(symbol)

# --- Layout ---
header_col1, header_col2 = st.columns([4, 1])

with header_col1:
    st.title(f"📊 {symbol} - Detailed View")

with header_col2:
    if st.button("🔙 Back to Watchlist"):
        st.switch_page("app.py")

# --- Price Chart ---
st.markdown("## 📈 6-Month Price Chart")
hist = stock.history(period="6mo")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
fig.update_layout(height=400, margin=dict(t=20, b=20, l=10, r=10))
st.plotly_chart(fig, use_container_width=True)

# --- Financial Info ---
st.markdown("## 📊 Key Financial Metrics")
info = stock.info

metrics = {
    "Current Price": info.get("currentPrice"),
    "P/E Ratio": info.get("trailingPE"),
    "Market Cap": info.get("marketCap"),
    "Net Income (TTM)": info.get("netIncomeToCommon"),
    "Revenue (TTM)": info.get("totalRevenue"),
    "52-Week High": info.get("fiftyTwoWeekHigh"),
    "52-Week Low": info.get("fiftyTwoWeekLow")
}

col1, col2 = st.columns(2)
for i, (k, v) in enumerate(metrics.items()):
    with (col1 if i % 2 == 0 else col2):
        st.metric(label=k, value=f"{v:,}" if isinstance(v, (int, float)) else v)

# --- Company Info ---
st.markdown("## 🏢 Business Summary")
summary = info.get("longBusinessSummary", "No summary available.")
st.write(summary)

# --- Mobile UI Tweaks ---
st.markdown("""
<style>
@media only screen and (max-width: 768px) {
    .block-container {
        padding: 1rem 1rem 2rem 1rem;
    }
    .stTitle { font-size: 22px; }
}
</style>
""", unsafe_allow_html=True)
