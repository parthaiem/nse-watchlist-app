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
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

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
            cols = st.columns(3)  # Create 3 columns for suggestions
            col_index = 0
            
            for symbol, name in suggestions.items():
                with cols[col_index]:
                    if st.button(f"{name} ({symbol})", key=f"suggest_{symbol}"):
                        st.session_state.selected_stock = symbol
                        st.session_state.search_results = {symbol: name}
                        st.rerun()
                col_index = (col_index + 1) % 3
    
    # Full search when user clicks the button
    if st.button("🔍 Search Stocks", key="search_button"):
        if search_term:
            with st.spinner("Searching..."):
                search_results = search_nse_stocks(search_term)
                st.session_state.search_results = search_results
                
                if not search_results:
                    st.warning("No NSE stocks found matching your search")
                else:
                    st.success(f"Found {len(search_results)} matching stocks")
        else:
            st.warning("Please enter a search term")
    
    # Display search results if available
    if st.session_state.search_results:
        st.markdown("---")
        st.markdown("### Search Results")
        
        for symbol, name in st.session_state.search_results.items():
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{name}**")
                st.markdown(f"*{symbol}*")
                
                try:
                    stock = yf.Ticker(symbol)
                    info = stock.info
                    st.write(f"**Current Price:** ₹{info.get('currentPrice', 'N/A')}")
                    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                except:
                    st.warning("Couldn't fetch price data")
            
            with col2:
                if st.button(f"➕ Add", key=f"add_{symbol}"):
                    if symbol not in st.session_state.watchlist:
                        add_to_watchlist(st.session_state.user, symbol)
                        st.session_state.watchlist = get_watchlist(st.session_state.user)
                        st.success(f"Added {name} to watchlist!")
                        st.rerun()
                    else:
                        st.warning("Already in watchlist")
    
    return None

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
                st.session_state.watchlist = get_watchlist(username)
                st.rerun()
            else:
                st.warning("Please enter a name to login.")
        st.stop()

# --- Market Snapshot Section ---
st.subheader("🌐 Global & Commodity Market Snapshot")

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

st.dataframe(pd.DataFrame(index_data).style.applymap(color_percent, subset=[
    "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
]), use_container_width=True)

# --- Search Stocks Section ---
stock_search_component()

# --- Watchlist Section ---
st.subheader("📉 Your Watchlist")

if not st.session_state.watchlist:
    st.info("Your watchlist is empty. Search for stocks above to add them.")
else:
    # Custom CSS for beautiful table
    st.markdown("""
    <style>
        .dataframe {
            width: 100%;
            border-collapse: collapse;
            margin: 1em 0;
            font-size: 0.9em;
            font-family: sans-serif;
            box-shadow: 0 0 20px rgba(0, 0, 0, 0.15);
        }
        .dataframe thead tr {
            background-color: #2c3e50;
            color: #ffffff;
            text-align: left;
        }
        .dataframe th,
        .dataframe td {
            padding: 12px 15px;
        }
        .dataframe tbody tr {
            border-bottom: 1px solid #dddddd;
        }
        .dataframe tbody tr:nth-of-type(even) {
            background-color: #f3f3f3;
        }
        .dataframe tbody tr:last-of-type {
            border-bottom: 2px solid #2c3e50;
        }
        .dataframe tbody tr:hover {
            background-color: #f1f1f1;
        }
        .positive-change {
            color: #28a745;
            font-weight: bold;
        }
        .negative-change {
            color: #dc3545;
            font-weight: bold;
        }
        .remove-btn {
            background-color: #dc3545;
            color: white;
            border: none;
            padding: 5px 10px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 0.8em;
        }
        .remove-btn:hover {
            background-color: #c82333;
        }
    </style>
    """, unsafe_allow_html=True)

    # Prepare data for the table
    watchlist_data = []
    for symbol in st.session_state.watchlist:
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
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

            watchlist_data.append({
                "Company": company_name,
                "Symbol": symbol,
                "Price (₹)": f"{current_price:,.2f}",
                "Day %": f"{day_change:+.2f}%",
                "Week %": f"{week_change:+.2f}%",
                "Month %": f"{month_change:+.2f}%",
                "52W High": f"{high_52:,.2f}",
                "52W Low": f"{low_52:,.2f}"
            })
        except Exception as e:
            st.error(f"Error fetching {symbol}: {str(e)}")

    if watchlist_data:
        # Create DataFrame
        df = pd.DataFrame(watchlist_data)
        
        # Style the DataFrame
        def style_change(val):
            try:
                val_float = float(val.strip('%+'))
                color = 'green' if val_float >= 0 else 'red'
                return f'color: {color}; font-weight: bold'
            except:
                return ''
        
        styled_df = df.style.applymap(style_change, subset=["Day %", "Week %", "Month %"])
        
        # Display the styled DataFrame
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Company": "Company",
                "Symbol": "Symbol",
                "Price (₹)": st.column_config.NumberColumn("Price (₹)", format="₹%.2f"),
                "Day %": "Day Change",
                "Week %": "Week Change",
                "Month %": "Month Change",
                "52W High": st.column_config.NumberColumn("52W High", format="₹%.2f"),
                "52W Low": st.column_config.NumberColumn("52W Low", format="₹%.2f")
            }
        )
        
        # Add remove functionality
        st.markdown("---")
        st.subheader("Manage Watchlist")
        
        # Create a list to track stocks to remove
        to_remove = []
        
        # Display each stock with a remove button
        for symbol in st.session_state.watchlist:
            cols = st.columns([4, 2, 1])
            company_name = st.session_state.search_results.get(symbol, symbol)
            
            # Get current price for display
            try:
                current_price = yf.Ticker(symbol).history(period='1d')['Close'][-1]
                price_display = f"₹{current_price:,.2f}"
            except:
                price_display = "Price: N/A"
            
            cols[0].markdown(f"**{company_name}**")
            cols[1].markdown(f"*{price_display}*")
            
            if cols[2].button("Remove", key=f"remove_{symbol}"):
                to_remove.append(symbol)
        
        # Process removals
        for symbol in to_remove:
            remove_from_watchlist(st.session_state.user, symbol)
            st.session_state.watchlist = get_watchlist(st.session_state.user)
            st.success(f"Removed {symbol} from watchlist")
            st.rerun()
        
        # Export to CSV
        csv = df.to_csv(index=False)
        st.download_button(
            "📥 Export to CSV", 
            csv, 
            file_name="watchlist.csv", 
            mime="text/csv",
            help="Download your watchlist as a CSV file"
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