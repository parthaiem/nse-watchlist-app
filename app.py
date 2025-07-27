import streamlit as st
import yfinance as yf
import pandas as pd
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh

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

def search_nse_stocks(search_term):
    """Search for NSE stocks based on user input"""
    if not search_term:
        return {}
    
    try:
        # Sample list of popular NSE stocks
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
        
        # Filter stocks based on search term
        search_term_lower = search_term.lower()
        results = {k: v for k, v in popular_nse_stocks.items() 
                  if search_term_lower in v.lower() or search_term_lower in k.lower()}
        
        return results
    
    except Exception as e:
        st.error(f"Error searching stocks: {e}")
        return {}

def stock_search_component():
    """Stock search component that returns selected symbol"""
    st.subheader("🔍 Search NSE Stocks")
    
    search_term = st.text_input("Enter company name or symbol", "", key="stock_search_input")
    
    if search_term:
        search_results = search_nse_stocks(search_term)
        st.session_state.search_results = search_results
        
        if not search_results:
            st.warning("No stocks found matching your search.")
            return None
        else:
            st.success(f"Found {len(search_results)} matching stocks")
            
            # Display search results in a dropdown
            name_to_symbol = {v: k for k, v in search_results.items()}
            selected_name = st.selectbox("Select a stock", list(name_to_symbol.keys()))
            
            # Store selected stock in session state
            st.session_state.selected_stock = name_to_symbol.get(selected_name)
            
            # Add button next to the select box
            if st.button("➕ Add to Watchlist"):
                if st.session_state.selected_stock:
                    return st.session_state.selected_stock
    return None

# --- Main App ---
st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="datarefresh")

# User authentication (same as before)
if "user" not in st.session_state:
    username = st.text_input("Enter your name to continue:", key="login_input")
    if st.button("Login", key="login_btn"):
        if username:
            st.session_state.user = username
            st.rerun()
        else:
            st.warning("Please enter a name to login.")
    st.stop()
else:
    # Display logout button
    if st.button("Logout", key="logout_btn"):
        st.session_state.clear()
        st.rerun()

# --- Market Snapshot Section ---
# (Same as before)

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

# Display watchlist
st.subheader("📉 Your Watchlist")

if not watchlist:
    st.info("Your watchlist is empty. Search for stocks above to add them.")
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

            # Get company name
            company_name = st.session_state.search_results.get(symbol, symbol)

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
            st.error(f"Error fetching {symbol}: {e}")

    if data_rows:
        # Display the watchlist table
        df = pd.DataFrame(data_rows)
        st.dataframe(
            df.style.applymap(color_percent, subset=[
                "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
            ]),
            use_container_width=True
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
# (Same as before)