import streamlit as st
import yfinance as yf
import pandas as pd
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh
import time

# Initialize session states
if 'search_results' not in st.session_state:
    st.session_state.search_results = {}
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None

# Custom CSS for better UI
st.markdown("""
<style>
    .stTextInput input {
        border-radius: 8px;
        padding: 12px;
    }
    .stButton button {
        border-radius: 8px;
        padding: 8px 16px;
        background-color: #4CAF50;
        color: white;
        border: none;
    }
    .stButton button:hover {
        background-color: #45a049;
    }
    .stock-card {
        border-radius: 10px;
        padding: 15px;
        margin: 10px 0;
        background-color: #f9f9f9;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .positive {
        color: #2ecc71;
    }
    .negative {
        color: #e74c3c;
    }
    .header {
        color: #3498db;
    }
</style>
""", unsafe_allow_html=True)

def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}'
    except:
        return ''

def display_market_data(indices):
    """Display market data in a styled table"""
    data = []
    for name, symbol in indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            current = hist["Close"][-1]
            previous = hist["Close"][-2]
            day_change = ((current - previous) / previous) * 100
            
            data.append({
                "Index": name,
                "Price": f"{current:.2f}",
                "Change (%)": f"{day_change:+.2f}%",
                "Status": "🟢 Up" if day_change >= 0 else "🔴 Down"
            })
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")
    
    if data:
        df = pd.DataFrame(data)
        st.dataframe(
            df.style.applymap(color_percent, subset=["Change (%)"]),
            use_container_width=True,
            hide_index=True
        )

def display_watchlist(watchlist, user):
    """Display watchlist with interactive cards"""
    for symbol in watchlist:
        with st.container():
            st.markdown(f"<div class='stock-card'>", unsafe_allow_html=True)
            
            try:
                stock = yf.Ticker(symbol)
                info = stock.info
                hist = stock.history(period="1mo")
                
                col1, col2, col3 = st.columns([3, 2, 1])
                
                with col1:
                    st.markdown(f"### {info.get('longName', symbol)}")
                    st.markdown(f"**{symbol}** | {info.get('sector', 'N/A')}")
                
                with col2:
                    if not hist.empty:
                        current_price = hist["Close"][-1]
                        prev_close = hist["Close"][-2] if len(hist) > 1 else current_price
                        change = ((current_price - prev_close) / prev_close) * 100
                        
                        st.metric(
                            label="Current Price",
                            value=f"₹{current_price:.2f}",
                            delta=f"{change:+.2f}%",
                            delta_color="normal"
                        )
                
                with col3:
                    if st.button(f"Remove", key=f"remove_{symbol}"):
                        remove_from_watchlist(user, symbol)
                        st.success(f"Removed {symbol} from watchlist")
                        time.sleep(1)
                        st.rerun()
                
                # Additional details in expander
                with st.expander("View Details"):
                    tab1, tab2 = st.tabs(["Overview", "Chart"])
                    
                    with tab1:
                        col1, col2 = st.columns(2)
                        with col1:
                            st.write(f"**52W High:** ₹{info.get('fiftyTwoWeekHigh', 'N/A')}")
                            st.write(f"**52W Low:** ₹{info.get('fiftyTwoWeekLow', 'N/A')}")
                            st.write(f"**Volume:** {info.get('volume', 'N/A')}")
                        
                        with col2:
                            st.write(f"**PE Ratio:** {info.get('trailingPE', 'N/A')}")
                            st.write(f"**Market Cap:** {info.get('marketCap', 'N/A')}")
                            st.write(f"**Dividend Yield:** {info.get('dividendYield', 'N/A')}")
                    
                    with tab2:
                        if not hist.empty:
                            st.line_chart(hist["Close"])
            
            except Exception as e:
                st.error(f"Error loading {symbol}: {str(e)}")
            
            st.markdown("</div>", unsafe_allow_html=True)

def search_nse_stocks(search_term):
    """Search for NSE stocks in real-time using Yahoo Finance"""
    if not search_term or len(search_term) < 2:
        return {}
    
    try:
        # Predefined list of popular NSE stocks for autocomplete
        popular_nse_stocks = {
            "RELIANCE.NS": "Reliance Industries",
            "TCS.NS": "Tata Consultancy Services",
            "HDFCBANK.NS": "HDFC Bank",
            "INFY.NS": "Infosys",
            "HINDUNILVR.NS": "Hindustan Unilever",
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
            "ULTRACEMCO.NS": "UltraTech Cement"
        }
        
        # Filter for autocomplete suggestions
        search_term_lower = search_term.lower()
        suggestions = {k: v for k, v in popular_nse_stocks.items() 
                      if search_term_lower in v.lower() or search_term_lower in k.lower()}
        
        # Also try direct Yahoo Finance search
        try:
            ticker = yf.Ticker(f"{search_term.upper()}.NS")
            info = ticker.info
            if 'symbol' in info and info['symbol'].endswith('.NS'):
                suggestions[info['symbol']] = info.get('longName', info['symbol'])
        except:
            pass
            
        return suggestions
    
    except Exception as e:
        st.error(f"Error searching stocks: {str(e)}")
        return {}

def stock_search_component():
    """Stock search component with autocomplete"""
    with st.container():
        st.subheader("🔍 Search NSE Stocks", anchor=False)
        
        # Create two columns for search input and button
        col1, col2 = st.columns([4, 1])
        
        with col1:
            search_term = st.text_input(
                "Start typing company name or symbol (e.g., 'Reliance' or 'TCS')", 
                "", 
                key="stock_search_input",
                help="Search will autocomplete as you type",
                placeholder="Search for NSE stocks..."
            )
        
        with col2:
            st.write("")  # Spacer
            st.write("")  # Spacer
            search_clicked = st.button("Search", key="search_button")
        
        # Display autocomplete suggestions as user types
        if search_term and len(search_term) >= 2:
            with st.spinner("Searching..."):
                suggestions = search_nse_stocks(search_term)
                
                if suggestions:
                    st.markdown("#### Suggestions")
                    for symbol, name in suggestions.items():
                        with st.expander(f"{name} ({symbol})"):
                            try:
                                stock = yf.Ticker(symbol)
                                info = stock.info
                                
                                col1, col2 = st.columns([2, 1])
                                with col1:
                                    st.write(f"**Sector:** {info.get('sector', 'N/A')}")
                                    st.write(f"**Current Price:** ₹{info.get('currentPrice', 'N/A')}")
                                    st.write(f"**52W Range:** ₹{info.get('fiftyTwoWeekLow', 'N/A')} - ₹{info.get('fiftyTwoWeekHigh', 'N/A')}")
                                
                                with col2:
                                    if st.button(f"Add {symbol}", key=f"add_{symbol}"):
                                        return symbol
                            except:
                                st.warning("Couldn't fetch details for this stock")
        
        # Handle search button click
        if search_clicked and search_term:
            with st.spinner("Searching stocks..."):
                search_results = search_nse_stocks(search_term)
                st.session_state.search_results = search_results
                
                if not search_results:
                    st.warning("No NSE stocks found matching your search. Try different terms like 'Reliance' or 'TCS'")
                    return None
                else:
                    st.success(f"Found {len(search_results)} matching NSE stocks")
                    
                    # Display search results
                    st.markdown("#### Search Results")
                    for symbol, name in search_results.items():
                        with st.container():
                            st.markdown(f"<div class='stock-card'>", unsafe_allow_html=True)
                            
                            col1, col2 = st.columns([4, 1])
                            with col1:
                                st.markdown(f"**{name}**")
                                st.markdown(f"*{symbol}*")
                                
                                try:
                                    stock = yf.Ticker(symbol)
                                    info = stock.info
                                    st.write(f"Current: ₹{info.get('currentPrice', 'N/A')} | "
                                            f"52W High: ₹{info.get('fiftyTwoWeekHigh', 'N/A')} | "
                                            f"52W Low: ₹{info.get('fiftyTwoWeekLow', 'N/A')}")
                                except:
                                    st.warning("Couldn't fetch price data")
                            
                            with col2:
                                if st.button(f"Add", key=f"add_{symbol}"):
                                    return symbol
                            
                            st.markdown("</div>", unsafe_allow_html=True)
    return None

# --- Main App ---
st.set_page_config(
    page_title="NSE Stock Watchlist", 
    layout="wide",
    page_icon="📈"
)

# Auto-refresh every 10 minutes
st_autorefresh(interval=600000, key="datarefresh")

# --- Top bar layout ---
st.markdown("<div style='background-color:#3498db;padding:10px;border-radius:10px;margin-bottom:20px;'>"
            "<h1 style='color:white;text-align:center;'>📈 NSE Stock Watchlist</h1>"
            "</div>", unsafe_allow_html=True)

# User authentication
if "user" not in st.session_state:
    with st.container():
        st.subheader("Login", anchor=False)
        username = st.text_input("Enter your name to continue:", key="login_input")
        if st.button("Login", key="login_btn"):
            if username:
                st.session_state.user = username
                st.rerun()
            else:
                st.warning("Please enter a name to login.")
    st.stop()
else:
    # Display user info and logout button
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown(f"<p style='font-size:18px;'>👤 Logged in as <strong>{st.session_state.user}</strong></p>", 
                   unsafe_allow_html=True)
    with col2:
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()

# --- Market Snapshot Section ---
with st.container():
    st.subheader("🌐 Global & Commodity Market Snapshot", anchor=False)
    
    index_symbols = {
        "NIFTY 50": "^NSEI",
        "SENSEX": "^BSESN",
        "NASDAQ": "^IXIC",
        "DOW JONES": "^DJI",
        "GOLD": "GC=F",
        "SILVER": "SI=F",
        "CRUDE OIL": "CL=F"
    }
    
    # Create tabs for different market segments
    tab1, tab2, tab3 = st.tabs(["Indian Indices", "US Indices", "Commodities"])
    
    with tab1:
        st.markdown("#### Indian Market Indices")
        indian_indices = {k: v for k, v in index_symbols.items() if k in ["NIFTY 50", "SENSEX"]}
        display_market_data(indian_indices)
    
    with tab2:
        st.markdown("#### US Market Indices")
        us_indices = {k: v for k, v in index_symbols.items() if k in ["NASDAQ", "DOW JONES"]}
        display_market_data(us_indices)
    
    with tab3:
        st.markdown("#### Commodities")
        commodities = {k: v for k, v in index_symbols.items() if k in ["GOLD", "SILVER", "CRUDE OIL"]}
        display_market_data(commodities)

# --- Stock Watchlist Section ---
user = st.session_state.user
watchlist = get_watchlist(user)

# Search and add stocks
selected_symbol = stock_search_component()

if selected_symbol:
    if selected_symbol not in watchlist:
        add_to_watchlist(user, selected_symbol)
        st.success(f"{st.session_state.search_results.get(selected_symbol, selected_symbol)} added to watchlist!")
        time.sleep(1)
        st.rerun()
    else:
        st.warning("This stock is already in your watchlist!")

# Display watchlist
with st.container():
    st.subheader("📉 Your Watchlist", anchor=False)
    
    if not watchlist:
        st.info("Your watchlist is empty. Search for stocks above to add them.")
    else:
        display_watchlist(watchlist, user)

# --- Footer ---
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background-color: #f9f9f9; border-radius: 10px;'>
    <h4>📊 FinSmart Wealth Advisory</h4>
    <p>Partha Chakraborty</p>
    <div style='display: flex; justify-content: center; gap: 20px;'>
        <a href="tel:+91XXXXXXXXXX">📞 Call</a>
        <a href="https://wa.me/91XXXXXXXXXX">💬 WhatsApp</a>
        <a href="https://angel-one.onelink.me/Wjgr/m8njiek1">📂 Open DMAT</a>
    </div>
</div>
""", unsafe_allow_html=True)