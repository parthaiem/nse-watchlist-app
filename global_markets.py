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

# Function to style percentage changes
def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}'
    except:
        return ''

# Function to get market data
def get_market_data():
    # Major Global Indices with country flags
    global_indices = {
        "🇮🇳 NIFTY 50": "^NSEI",
        "🇮🇳 SENSEX": "^BSESN",
        "🇮🇳 NIFTY BANK": "^NSEBANK",
        "🇺🇸 NASDAQ": "^IXIC",
        "🇺🇸 S&P 500": "^GSPC",
        "🇺🇸 DOW JONES": "^DJI",
        "🇬🇧 FTSE 100": "^FTSE",
        "🇩🇪 DAX": "^GDAXI",
        "🇯🇵 NIKKEI 225": "^N225",
        "🇭🇰 HANG SENG": "^HSI",
        "🇨🇳 SHANGHAI COMP": "000001.SS"
    }

    # Commodities
    commodities = {
        "🟡 GOLD": "GC=F",
        "⚪ SILVER": "SI=F",
        "🛢️ CRUDE OIL": "CL=F",
        "🛢️ BRENT CRUDE": "BZ=F",
        "💨 NATURAL GAS": "NG=F",
        "🟠 COPPER": "HG=F"
    }

    # Indian Sectoral Indices
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

    # Cryptocurrencies
    cryptocurrencies = {
        "₿ BITCOIN": "BTC-USD",
        "Ξ ETHEREUM": "ETH-USD",
        "🅱️ BNB": "BNB-USD",
        "✕ XRP": "XRP-USD",
        "◎ SOLANA": "SOL-USD"
    }

    # Get all data
    all_data = []
    
    # Global Indices
    for name, symbol in global_indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current = hist["Close"][-1]
                previous = hist["Open"][0]
                change = ((current - previous) / previous) * 100
                all_data.append({
                    "Category": "Global Indices",
                    "Name": name,
                    "Symbol": symbol,
                    "Price": current,
                    "Change (%)": change,
                    "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")

    # Commodities
    for name, symbol in commodities.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current = hist["Close"][-1]
                previous = hist["Open"][0]
                change = ((current - previous) / previous) * 100
                all_data.append({
                    "Category": "Commodities",
                    "Name": name,
                    "Symbol": symbol,
                    "Price": current,
                    "Change (%)": change,
                    "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")

    # Indian Sectors
    for name, symbol in indian_sectors.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current = hist["Close"][-1]
                previous = hist["Open"][0]
                change = ((current - previous) / previous) * 100
                all_data.append({
                    "Category": "Indian Sectors",
                    "Name": name,
                    "Symbol": symbol,
                    "Price": current,
                    "Change (%)": change,
                    "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")

    # Cryptocurrencies
    for name, symbol in cryptocurrencies.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                current = hist["Close"][-1]
                previous = hist["Open"][0]
                change = ((current - previous) / previous) * 100
                all_data.append({
                    "Category": "Cryptocurrencies",
                    "Name": name,
                    "Symbol": symbol,
                    "Price": current,
                    "Change (%)": change,
                    "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                })
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")

    return pd.DataFrame(all_data)

# Main page function
def main():
    st.set_page_config(page_title="Global Market Dashboard", layout="wide")
    
    # Show header
    show_header()
    
    # Market overview
    st.markdown("""
    <style>
        .big-font {
            font-size:18px !important;
        }
        .metric-box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Current time
    st.markdown(f"<div class='big-font'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    
    # Get market data
    with st.spinner("Loading market data..."):
        market_data = get_market_data()
    
    # Display data in tabs
    tab1, tab2, tab3, tab4 = st.tabs(["Global Indices", "Commodities", "Indian Sectors", "Cryptocurrencies"])
    
    with tab1:
        st.subheader("🌐 Global Market Indices")
        global_data = market_data[market_data["Category"] == "Global Indices"]
        st.dataframe(
            global_data.style.format({
                "Price": "{:.2f}",
                "Change (%)": "{:+.2f}%"
            }).applymap(color_percent, subset=["Change (%)"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Name": "Index",
                "Price": "Price",
                "Change (%)": "Change",
                "Last Updated": "Updated"
            }
        )
    
    with tab2:
        st.subheader("🛢️ Commodities Market")
        commodities_data = market_data[market_data["Category"] == "Commodities"]
        st.dataframe(
            commodities_data.style.format({
                "Price": "{:.2f}",
                "Change (%)": "{:+.2f}%"
            }).applymap(color_percent, subset=["Change (%)"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Name": "Commodity",
                "Price": "Price",
                "Change (%)": "Change",
                "Last Updated": "Updated"
            }
        )
    
    with tab3:
        st.subheader("🇮🇳 Indian Sectoral Indices")
        sectors_data = market_data[market_data["Category"] == "Indian Sectors"]
        st.dataframe(
            sectors_data.style.format({
                "Price": "{:.2f}",
                "Change (%)": "{:+.2f}%"
            }).applymap(color_percent, subset=["Change (%)"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Name": "Sector",
                "Price": "Price",
                "Change (%)": "Change",
                "Last Updated": "Updated"
            }
        )
    
    with tab4:
        st.subheader("₿ Cryptocurrencies")
        crypto_data = market_data[market_data["Category"] == "Cryptocurrencies"]
        st.dataframe(
            crypto_data.style.format({
                "Price": "{:.2f}",
                "Change (%)": "{:+.2f}%"
            }).applymap(color_percent, subset=["Change (%)"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Name": "Crypto",
                "Price": "Price",
                "Change (%)": "Change",
                "Last Updated": "Updated"
            }
        )
    
    # Show footer
    show_footer()

if __name__ == "__main__":
    main()