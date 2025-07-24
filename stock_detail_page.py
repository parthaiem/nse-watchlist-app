import streamlit as st
import yfinance as yf
import plotly.graph_objs as go

st.set_page_config(page_title="Stock Details", layout="wide")

# --- Parse selected stock ---
query_params = st.query_params
stock_symbol = query_params.get("stock", "")[0] if "stock" in query_params else None

if not stock_symbol:
    st.error("No stock selected. Please go back to the watchlist.")
    st.stop()

stock = yf.Ticker(stock_symbol)
info = stock.info

# --- Title and Back Button ---
st.markdown("""
    <div style='display: flex; justify-content: space-between; align-items: center;'>
        <h2 style='margin: 0;'>📊 {}</h2>
        <a href='/'><button style='padding: 8px 20px; font-size: 16px;'>⬅ Back</button></a>
    </div>
""".format(info.get("shortName", stock_symbol)), unsafe_allow_html=True)

# --- Stock Chart ---
hist = stock.history(period="1y")
fig = go.Figure()
fig.add_trace(go.Scatter(x=hist.index, y=hist['Close'], mode='lines', name='Close'))
fig.update_layout(title=f"12-Month Price Chart for {stock_symbol}", xaxis_title="Date", yaxis_title="Price (INR)", height=400)
st.plotly_chart(fig, use_container_width=True)

# --- Key Metrics ---
st.subheader("📌 Key Financial Metrics")
metrics = {
    "Current Price": f"₹ {info.get('currentPrice', 'NA')}",
    "Market Cap": f"₹ {info.get('marketCap', 'NA'):,}" if info.get("marketCap") else "NA",
    "P/E Ratio": info.get("trailingPE", "NA"),
    "EPS (TTM)": info.get("trailingEps", "NA"),
    "Revenue (TTM)": f"₹ {info.get('totalRevenue', 'NA'):,}" if info.get("totalRevenue") else "NA",
    "Net Income": f"₹ {info.get('netIncomeToCommon', 'NA'):,}" if info.get("netIncomeToCommon") else "NA"
}
metric_cols = st.columns(len(metrics))
for i, (k, v) in enumerate(metrics.items()):
    metric_cols[i].metric(label=k, value=v)

# --- Business Summary ---
st.subheader("🏢 Business Overview")
st.markdown(info.get("longBusinessSummary", "Business summary not available."))

# --- Business Image (if available) ---
if "logo_url" in info and info["logo_url"]:
    st.image(info["logo_url"], width=120)

# --- Latest News Section ---
st.subheader("📰 Latest News")
news = info.get("news", [])
if news:
    for article in news[:5]:
        st.markdown(f"- [{article['title']}]({article['link']})")
else:
    st.info("News not available from Yahoo Finance API.")
