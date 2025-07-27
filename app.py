import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go

# Initialize session state for search results
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}'
    except:
        return ''

def search_nse_stocks(search_term):
    """Search for NSE stocks based on user input"""
    if not search_term:
        return []
    
    try:
        # You might want to replace this with actual NSE stock data
        # For now, we'll use a sample list of popular NSE stocks
        popular_nse_stocks = {
            "TCS.NS": "TATA CONSULTANCY SERVICES",
            "INFY.NS": "INFOSYS",
            "WIPRO.NS": "WIPRO",
            "HCLTECH.NS": "HCL TECHNOLOGIES",
            "RELIANCE.NS": "RELIANCE INDUSTRIES",
            "SBIN.NS": "STATE BANK OF INDIA",
            "ICICIBANK.NS": "ICICI BANK",
            "TECHM.NS": "TECH MAHINDRA",
            "HDFCBANK.NS": "HDFC BANK",
            "BHARTIARTL.NS": "BHARTI AIRTEL",
            "ITC.NS": "ITC LIMITED",
            "LT.NS": "LARSEN & TOUBRO",
            "MARUTI.NS": "MARUTI SUZUKI",
            "ONGC.NS": "OIL & NATURAL GAS CORP",
            "SUNPHARMA.NS": "SUN PHARMACEUTICALS",
            "TATAMOTORS.NS": "TATA MOTORS",
            "NTPC.NS": "NTPC LIMITED",
            "POWERGRID.NS": "POWER GRID CORP",
            "ULTRACEMCO.NS": "ULTRATECH CEMENT",
            "BAJFINANCE.NS": "BAJAJ FINANCE"
        }
        
        # Filter stocks based on search term (case insensitive)
        search_term_lower = search_term.lower()
        results = {k: v for k, v in popular_nse_stocks.items() 
                  if search_term_lower in v.lower() or search_term_lower in k.lower()}
        
        return results
    
    except Exception as e:
        st.error(f"Error searching stocks: {e}")
        return {}

def stock_search():
    """Stock search component"""
    st.subheader("🔍 Search NSE Stocks")
    
    search_term = st.text_input("Enter company name or symbol", "", key="stock_search_input")
    
    if search_term:
        search_results = search_nse_stocks(search_term)
        st.session_state.search_results = search_results
        
        if not search_results:
            st.warning("No stocks found matching your search.")
        else:
            st.success(f"Found {len(search_results)} matching stocks")
            
            # Display search results in a dropdown
            name_to_symbol = {v: k for k, v in search_results.items()}
            selected_name = st.selectbox("Select a stock", list(name_to_symbol.keys()))
            
            return name_to_symbol.get(selected_name)
    return None

st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="datarefresh")

# --- Top bar layout ---
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

# --- Market Snapshot Section ---
index_symbols = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "CRUDE OIL": "CL=F"
}

index_data = []
for name, symbol in index_symbols.items():
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1mo")
        current = hist["Close"][-1]
        previous = hist["Close"][-2]
        day_change = ((current - previous) / previous) * 100
        week_change = ((hist["Close"][-1] - hist["Close"][-5]) / hist["Close"][-5]) * 100 if len(hist) >= 5 else 0
        month_change = ((hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]) * 100 if len(hist) > 0 else 0
        index_data.append({
            "Index": name,
            "Current Price": f"{current:.2f}",
            "Day Change (%)": f"{day_change:+.2f}%",
            "1-Week Change (%)": f"{week_change:+.2f}%",
            "1-Month Change (%)": f"{month_change:+.2f}%"
        })
    except Exception as e:
        st.warning(f"Could not load {name}: {e}")

st.subheader("🌐 Global & Commodity Market Snapshot")
st.dataframe(pd.DataFrame(index_data).style.applymap(color_percent, subset=[
    "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
]), use_container_width=True)

# --- Stock Search and Watchlist Management ---
user = st.session_state.user
watchlist = get_watchlist(user)

st.subheader("📌 Add to Watchlist")
selected_symbol = stock_search()

if selected_symbol and st.button("➕ Add to Watchlist"):
    if selected_symbol not in watchlist:
        add_to_watchlist(user, selected_symbol)
        st.success(f"{st.session_state.search_results[selected_symbol]} added!")
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

            # Get company name from search results or use symbol as fallback
            company = st.session_state.search_results.get(symbol, symbol)

            link = f"[Details](?stock={symbol})"

            data_rows.append({
                "Symbol": symbol,
                "Company": company,
                "Current Price": round(current_price, 2),
                "Day Change (%)": f"{day_change:+.2f}%",
                "1-Week Change (%)": f"{week_change:+.2f}%",
                "1-Month Change (%)": f"{month_change:+.2f}%",
                "52-Week High": f"{high_52:.2f}",
                "52-Week Low": f"{low_52:.2f}",
                "Details": link
            })
        except Exception as e:
            st.error(f"Error fetching {symbol}: {e}")

    df = pd.DataFrame(data_rows)
    st.dataframe(df.style.applymap(color_percent, subset=[
        "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
    ]), use_container_width=True)

    # Add remove button for each stock
    for symbol in watchlist:
        col1, col2 = st.columns([4, 1])
        with col1:
            st.write(f"Currently viewing: {st.session_state.search_results.get(symbol, symbol)}")
        with col2:
            if st.button(f"Remove {symbol}", key=f"remove_{symbol}"):
                remove_from_watchlist(user, symbol)
                st.success(f"Removed {symbol} from watchlist")
                st.rerun()

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