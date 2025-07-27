import streamlit as st
import yfinance as yf
import pandas as pd
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh

# Predefined list of popular NSE stocks for autocomplete
POPULAR_NSE_STOCKS = {
    "RELIANCE.NS": "Reliance Industries",
    "TCS.NS": "Tata Consultancy Services",
    "HDFCBANK.NS": "HDFC Bank",
    "INFY.NS": "Infosys",
    "ICICIBANK.NS": "ICICI Bank",
    "ITC.NS": "ITC Limited",
    "SBIN.NS": "State Bank of India",
    "BHARTIARTL.NS": "Bharti Airtel",
    "LT.NS": "Larsen & Toubro",
    "KOTAKBANK.NS": "Kotak Mahindra Bank",
    "HCLTECH.NS": "HCL Technologies",
    "ASIANPAINT.NS": "Asian Paints",
    "MARUTI.NS": "Maruti Suzuki",
    "TITAN.NS": "Titan Company",
    "BAJFINANCE.NS": "Bajaj Finance",
    "ONGC.NS": "Oil & Natural Gas Corporation",
    "NTPC.NS": "NTPC Limited",
    "POWERGRID.NS": "Power Grid Corporation",
    "ULTRACEMCO.NS": "UltraTech Cement",
    "WIPRO.NS": "Wipro Limited"
}

# Initialize session states
if 'search_results' not in st.session_state:
    st.session_state.search_results = {}
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}'
    except:
        return ''

def get_autocomplete_suggestions(search_term):
    """Get autocomplete suggestions from predefined list"""
    if not search_term or len(search_term) < 2:
        return {}
    
    search_term_lower = search_term.lower()
    return {k: v for k, v in POPULAR_NSE_STOCKS.items() 
            if search_term_lower in v.lower() or search_term_lower in k.lower()}

def search_nse_stocks(search_term):
    """Search for NSE stocks using Yahoo Finance with autocomplete"""
    suggestions = get_autocomplete_suggestions(search_term)
    
    # Also try direct Yahoo Finance search
    try:
        ticker = yf.Ticker(f"{search_term.upper()}.NS")
        info = ticker.info
        if 'symbol' in info and info['symbol'].endswith('.NS'):
            suggestions[info['symbol']] = info.get('longName', info['symbol'])
    except:
        pass
    
    return suggestions

def stock_search_component():
    """Stock search component with real-time suggestions"""
    st.subheader("🔍 Search NSE Stocks")
    
    # Search input with autocomplete
    search_term = st.text_input(
        "Start typing company name or symbol (e.g., 'RELIANCE' or 'TCS')", 
        "", 
        key="stock_search_input",
        help="Search will show suggestions as you type"
    )
    
    # Show autocomplete suggestions
    if search_term and len(search_term) >= 2:
        suggestions = get_autocomplete_suggestions(search_term)
        
        if suggestions:
            st.markdown("**Suggestions**")
            for symbol, name in suggestions.items():
                if st.button(f"{name} ({symbol})", key=f"suggest_{symbol}"):
                    st.session_state.selected_stock = symbol
                    return symbol
    
    # Full search when user clicks the button
    if st.button("Search", key="search_button"):
        if search_term:
            with st.spinner("Searching..."):
                search_results = search_nse_stocks(search_term)
                st.session_state.search_results = search_results
                
                if not search_results:
                    st.warning("No NSE stocks found matching your search")
                    return None
                else:
                    st.success(f"Found {len(search_results)} matching stocks")
                    
                    # Display search results
                    name_to_symbol = {v: k for k, v in search_results.items()}
                    selected_name = st.selectbox(
                        "Select a stock to add to watchlist", 
                        list(name_to_symbol.keys()),
                        key="stock_select"
                    )
                    
                    st.session_state.selected_stock = name_to_symbol.get(selected_name)
                    
                    if st.button("➕ Add to Watchlist", key="add_stock"):
                        return st.session_state.selected_stock
        else:
            st.warning("Please enter a search term")
    
    return None

# --- Rest of your existing code remains the same ---
# (Keep all the other functions and main app logic as they were)

# --- Main App ---
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

# --- Stock Watchlist Section ---
user = st.session_state.user
watchlist = get_watchlist(user)

# Search and add stocks
selected_symbol = stock_search_component()

if selected_symbol:
    if selected_symbol not in watchlist:
        add_to_watchlist(user, selected_symbol)
        st.success(f"{st.session_state.search_results[selected_symbol]} added to watchlist!")
        st.rerun()
    else:
        st.warning("This stock is already in your watchlist!")

# Display watchlist
st.subheader("📉 Your Watchlist")

if not watchlist:
    st.info("Your watchlist is empty. Search for stocks above to add them.")
else:
    data_rows = []
    for symbol in watchlist:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            
            # Get company name
            company_name = info.get('longName', symbol)
            
            # Get price data
            hist_1d = stock.history(period="1d")
            hist_1wk = stock.history(period="7d")
            hist_1y = stock.history(period="1y")

            if not hist_1d.empty:
                current_price = hist_1d["Close"][-1]
                previous_close = hist_1d["Open"][0] if len(hist_1d) > 0 else current_price
                day_change = ((current_price - previous_close) / previous_close) * 100
            else:
                current_price = info.get('currentPrice', 0)
                day_change = 0

            if not hist_1wk.empty:
                week_change = ((hist_1wk["Close"][-1] - hist_1wk["Close"][0]) / hist_1wk["Close"][0]) * 100
            else:
                week_change = 0

            if not hist_1y.empty:
                month_change = ((hist_1y["Close"][-1] - hist_1y["Close"][0]) / hist_1y["Close"][0]) * 100
                high_52 = hist_1y["High"].max()
                low_52 = hist_1y["Low"].min()
            else:
                month_change = 0
                high_52 = info.get('fiftyTwoWeekHigh', 0)
                low_52 = info.get('fiftyTwoWeekLow', 0)

            data_rows.append({
                "Symbol": symbol,
                "Company": company_name,
                "Current Price": round(current_price, 2),
                "Day Change (%)": f"{day_change:+.2f}%",
                "1-Week Change (%)": f"{week_change:+.2f}%",
                "1-Month Change (%)": f"{month_change:+.2f}%",
                "52-Week High": f"{high_52:.2f}",
                "52-Week Low": f"{low_52:.2f}"
            })
        except Exception as e:
            st.error(f"Error fetching {symbol}: {str(e)}")

    if data_rows:
        # Display the watchlist table
        df = pd.DataFrame(data_rows)
        st.dataframe(
            df.style.applymap(color_percent, subset=[
                "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
            ]),
            use_container_width=True,
            height=(min(len(df) * 35 + 35, 500))  # Dynamic height
        )
        
        # Add remove buttons for each stock
        st.subheader("Manage Watchlist")
        for symbol in watchlist:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"{st.session_state.search_results.get(symbol, symbol)}")
            with col2:
                if st.button(f"Remove {symbol}", key=f"remove_{symbol}"):
                    remove_from_watchlist(user, symbol)
                    st.success(f"Removed {symbol} from watchlist")
                    st.rerun()
        
        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV", 
            csv, 
            file_name="watchlist.csv", 
            mime="text/csv"
        )

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