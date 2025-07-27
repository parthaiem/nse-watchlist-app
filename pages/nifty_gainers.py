import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import get_watchlist  # Match your existing imports

# Initialize session states (consistent with your other pages)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Common header function (same as your global markets dashboard)
def show_header():
    # --- Top bar layout ---
    top_col1, top_col2, top_col3 = st.columns([1, 4, 2])

    with top_col1:
        st.image("logo.jpg", width=100)

    with top_col2:
        st.markdown("<h1 style='padding-top: 10px;'>📈 Nifty Top Gainers & Losers</h1>", unsafe_allow_html=True)

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

# Common footer function (same as your global markets dashboard)
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

def color_change(val):
    """Color formatting for percentage changes"""
    if isinstance(val, (int, float)):
        color = 'green' if val >= 0 else 'red'
        return f'color: {color}; font-weight: bold;'
    return ''

def get_nifty_components(index):
    """Get Nifty components with price changes"""
    # Note: In production, replace this with actual NSE API calls
    # This is a mock implementation using yfinance as fallback
    
    # List of major Nifty 50 stocks (sample)
    nifty50_stocks = {
        'RELIANCE': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'HDFCBANK': 'HDFCBANK.NS',
        'ICICIBANK': 'ICICIBANK.NS',
        'HINDUNILVR': 'HINDUNILVR.NS',
        'INFY': 'INFY.NS',
        'ITC': 'ITC.NS',
        'SBIN': 'SBIN.NS',
        'BHARTIARTL': 'BHARTIARTL.NS',
        'LT': 'LT.NS'
    }
    
    data = []
    for name, symbol in nifty50_stocks.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                data.append({
                    'Symbol': name,
                    'LTP': hist['Close'][-1],
                    'Change': hist['Close'][-1] - hist['Open'][0],
                    '% Change': ((hist['Close'][-1] - hist['Open'][0]) / hist['Open'][0]) * 100,
                    'Volume': hist['Volume'][-1]
                })
        except:
            continue
    
    return pd.DataFrame(data)

def display_gainers_losers(df, title):
    if df.empty:
        st.warning(f"No data available for {title}")
        return
    
    # Get top 5 gainers and losers
    gainers = df.nlargest(5, '% Change').reset_index(drop=True)
    losers = df.nsmallest(5, '% Change').reset_index(drop=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🏆 {title} Top Gainers")
        st.dataframe(
            gainers.style.format({
                'LTP': '{:.2f}',
                'Change': '{:+.2f}',
                '% Change': '{:+.2f}%',
                'Volume': '{:,}'
            }).applymap(color_change, subset=['% Change']),
            use_container_width=True,
            hide_index=True,
            height=300
        )
    
    with col2:
        st.subheader(f"📉 {title} Top Losers")
        st.dataframe(
            losers.style.format({
                'LTP': '{:.2f}',
                'Change': '{:+.2f}',
                '% Change': '{:+.2f}%',
                'Volume': '{:,}'
            }).applymap(color_change, subset=['% Change']),
            use_container_width=True,
            hide_index=True,
            height=300
        )

def main():
    st.set_page_config(page_title="Nifty Gainers & Losers", layout="wide")
    show_header()
    
    st.markdown(f"<div style='text-align: right;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.rerun()
    
    # Nifty 50 Section
    st.markdown("## 🇮🇳 NIFTY 50")
    with st.spinner("Loading Nifty 50 data..."):
        nifty50_data = get_nifty_components("NIFTY 50")
        display_gainers_losers(nifty50_data, "Nifty 50")
    
    st.markdown("---")
    
    # Nifty Next 50 Section (as proxy for Nifty 100)
    st.markdown("## 🇮🇳 Nifty Next 50")
    with st.spinner("Loading Nifty Next 50 data..."):
        nifty_next50_data = get_nifty_components("NIFTY NEXT 50")
        display_gainers_losers(nifty_next50_data, "Nifty Next 50")
    
    show_footer()

if __name__ == "__main__":
    main()