import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import get_watchlist  # Only if you need watchlist functionality

# Initialize session states (if needed)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Common header function
def show_header():
    # --- Top bar layout ---
    top_col1, top_col2, top_col3 = st.columns([1, 4, 2])

    with top_col1:
        st.image("logo.jpg", width=100)

    with top_col2:
        st.markdown("<h1 style='padding-top: 10px;'>🌍 Global Market Dashboard</h1>", unsafe_allow_html=True)

    with top_col3:
        if "user" in st.session_state:
            st.markdown(f"<p style='text-align:right; padding-top: 25px;'>👤 Logged in as <strong>{st.session_state.user}</strong></p>", 
                       unsafe_allow_html=True)
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

# Common footer function
def show_footer():
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

# Function to format numbers with 2 decimal places
def format_number(x, is_currency=False, is_percent=False):
    if isinstance(x, (int, float)):
        if is_percent:
            return f"{x:+.2f}%"
        if is_currency:
            return f"${x:,.2f}" if x >= 100 else f"${x:,.4f}"
        return f"{x:,.2f}"
    return str(x)

# Function to get market data
def get_market_data():
    # Major Global Indices with country flags and full names
    global_indices = {
        "🇮🇳 NIFTY 50 (India)": "^NSEI",
        "🇮🇳 SENSEX (India)": "^BSESN",
        "🇮🇳 NIFTY BANK (India)": "^NSEBANK",
        "🇺🇸 NASDAQ (United States)": "^IXIC",
        "🇺🇸 S&P 500 (United States)": "^GSPC",
        "🇺🇸 DOW JONES (United States)": "^DJI",
        "🇬🇧 FTSE 100 (United Kingdom)": "^FTSE",
        "🇩🇪 DAX (Germany)": "^GDAXI",
        "🇫🇷 CAC 40 (France)": "^FCHI",
        "🇯🇵 NIKKEI 225 (Japan)": "^N225",
        "🇭🇰 HANG SENG (Hong Kong)": "^HSI",
        "🇨🇳 SHANGHAI COMP (China)": "000001.SS"
    }

    # Commodities with more details
    commodities = {
        "🟡 GOLD (COMEX)": "GC=F",
        "⚪ SILVER (COMEX)": "SI=F",
        "🛢️ CRUDE OIL (WTI)": "CL=F",
        "🛢️ BRENT CRUDE": "BZ=F",
        "💨 NATURAL GAS": "NG=F",
        "🟠 COPPER": "HG=F"
    }

    # Indian Sectoral Indices with more sectors
    indian_sectors = {
        "💻 NIFTY IT": "^CNXIT",
        "🚗 NIFTY AUTO": "^CNXAUTO",
        "🏦 NIFTY BANK": "^CNXBANK",
        "💰 NIFTY FIN SERVICE": "^CNXFIN",
        "🛒 NIFTY FMCG": "^CNXFMCG",
        "🎬 NIFTY MEDIA": "^CNXMEDIA",
        "🏗️ NIFTY METAL": "^CNXMETAL",
        "💊 NIFTY PHARMA": "^CNXPHARMA",
        "🏛️ NIFTY PSU BANK": "^CNXPSUBANK",
        "🏢 NIFTY REALTY": "^CNXREALTY"
    }

    # Cryptocurrencies with more coins
    cryptocurrencies = {
        "₿ BITCOIN": "BTC-USD",
        "Ξ ETHEREUM": "ETH-USD",
        "🅱️ BNB": "BNB-USD",
        "✕ XRP": "XRP-USD",
        "◎ SOLANA": "SOL-USD"
    }

    # Currency pairs
    currencies = {
        "💵 USD/INR": "INR=X",
        "💶 EUR/INR": "EURINR=X",
        "💷 GBP/INR": "GBPINR=X",
        "💴 JPY/INR": "JPYINR=X"
    }

    # Get all data
    all_data = []
    
    def fetch_data(category, items):
        for name, symbol in items.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current = hist["Close"][-1]
                    previous = hist["Open"][0] if "Open" in hist.columns else hist["Close"][0]
                    change = ((current - previous) / previous) * 100 if previous != 0 else 0
                    
                    # Handle potential missing columns
                    day_low = hist["Low"][-1] if "Low" in hist.columns else current
                    day_high = hist["High"][-1] if "High" in hist.columns else current
                    day_range = f"{day_low:.2f} - {day_high:.2f}"
                    
                    all_data.append({
                        "Category": category,
                        "Name": name,
                        "Symbol": symbol,
                        "Price": current,
                        "Change (%)": change,
                        "Day Range": day_range
                    })
            except Exception as e:
                st.warning(f"Could not load {name}: {str(e)}")

    # Fetch all categories
    fetch_data("Global Indices", global_indices)
    fetch_data("Commodities", commodities)
    fetch_data("Indian Sectors", indian_sectors)
    fetch_data("Cryptocurrencies", cryptocurrencies)
    fetch_data("Currencies", currencies)

    return pd.DataFrame(all_data)

# Main page function
def main():
    st.set_page_config(page_title="Global Market Dashboard", layout="wide")
    
    # Show header
    show_header()
    
    # Custom CSS
    st.markdown("""
    <style>
        .big-font {
            font-size:18px !important;
        }
        .positive {
            color: green;
            font-weight: bold;
        }
        .negative {
            color: red;
            font-weight: bold;
        }
        .day-range-low {
            color: red;
            font-weight: bold;
        }
        .day-range-high {
            color: green;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Current time
    st.markdown(f"<div class='big-font'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</div>", 
               unsafe_allow_html=True)
    
    # Get market data
    with st.spinner("Loading market data..."):
        market_data = get_market_data()
    
    # Display data in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌐 Global Indices", 
        "🛢️ Commodities", 
        "🇮🇳 Indian Sectors", 
        "₿ Cryptocurrencies",
        "💱 Currencies"
    ])
    
    def display_tab_data(df, currency_symbol=""):
        display_df = df.copy()
        display_df["Price"] = display_df["Price"].apply(lambda x: f"{currency_symbol}{format_number(x)}")
        display_df["Change (%)"] = display_df["Change (%)"].apply(
            lambda x: f"<span class='{'positive' if x >= 0 else 'negative'}'>{format_number(x, is_percent=True)}</span>",
            na_action='ignore'
        )
        
        # Split Day Range into two colored parts
        display_df["Day Range"] = display_df["Day Range"].apply(
            lambda x: f"<span class='day-range-low'>{x.split(' - ')[0]}</span> - <span class='day-range-high'>{x.split(' - ')[1]}</span>"
            if isinstance(x, str) and ' - ' in x else x
        )
        
        st.markdown(
            display_df[["Name", "Price", "Change (%)", "Day Range"]].to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
    
    with tab1:
        st.subheader("🌐 Global Market Indices")
        global_data = market_data[market_data["Category"] == "Global Indices"]
        display_tab_data(global_data)
    
    with tab2:
        st.subheader("🛢️ Commodities Market")
        commodities_data = market_data[market_data["Category"] == "Commodities"]
        display_tab_data(commodities_data, "$")
    
    with tab3:
        st.subheader("🇮🇳 Indian Sectoral Indices")
        sectors_data = market_data[market_data["Category"] == "Indian Sectors"]
        display_tab_data(sectors_data, "₹")
    
    with tab4:
        st.subheader("₿ Cryptocurrencies")
        crypto_data = market_data[market_data["Category"] == "Cryptocurrencies"]
        display_tab_data(crypto_data, "$")
    
    with tab5:
        st.subheader("💱 Currency Pairs")
        currency_data = market_data[market_data["Category"] == "Currencies"]
        display_tab_data(currency_data)
    
    # Show footer
    show_footer()

if __name__ == "__main__":
    main()