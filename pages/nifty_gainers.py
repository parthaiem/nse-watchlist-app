import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import get_watchlist  # Match your existing imports

# Initialize session states
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Common header function
def show_header():
    # --- Top bar layout ---
    top_col1, top_col2, top_col3 = st.columns([1, 4, 2])

    with top_col1:
        st.image("logo.jpg", width=100)

    with top_col2:
        st.markdown("<h1 style='padding-top: 10px;'>📊 Indian Market Movers</h1>", unsafe_allow_html=True)

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

def color_change(val):
    """Color formatting for percentage changes"""
    if isinstance(val, (int, float)):
        color = 'green' if val >= 0 else 'red'
        return f'color: {color}; font-weight: bold;'
    return ''

def get_stock_data(stock_list):
    """Get stock data for a list of symbols"""
    data = []
    for name, symbol in stock_list.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            if not hist.empty:
                data.append({
                    'Symbol': name,
                    'LTP': hist['Close'][-1],
                    'Change': hist['Close'][-1] - hist['Open'][0],
                    '% Change': ((hist['Close'][-1] - hist['Open'][0]) / hist['Open'][0]) * 100,
                    'Volume': hist['Volume'][-1] if 'Volume' in hist.columns else 0
                })
        except Exception as e:
            st.warning(f"Could not load {name}: {str(e)}")
            continue
    return pd.DataFrame(data)

def display_gainers_losers(df, title, num=5):
    if df.empty:
        st.warning(f"No data available for {title}")
        return
    
    # Get top gainers and losers
    gainers = df.nlargest(num, '% Change').reset_index(drop=True)
    losers = df.nsmallest(num, '% Change').reset_index(drop=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🏆 {title} Top Gainers")
        st.dataframe(
            gainers.style.format({
                'LTP': '₹{:.2f}',
                'Change': '{:+.2f}',
                '% Change': '{:+.2f}%',
                'Volume': '{:,}'
            }).applymap(color_change, subset=['% Change']),
            use_container_width=True,
            hide_index=True,
            height=min(400, 75 + num * 35)
        )
    
    with col2:
        st.subheader(f"📉 {title} Top Losers")
        st.dataframe(
            losers.style.format({
                'LTP': '₹{:.2f}',
                'Change': '{:+.2f}',
                '% Change': '{:+.2f}%',
                'Volume': '{:,}'
            }).applymap(color_change, subset=['% Change']),
            use_container_width=True,
            hide_index=True,
            height=min(400, 75 + num * 35)
        )

def main():
    st.set_page_config(page_title="Indian Market Movers", layout="wide")
    show_header()
    
    st.markdown(f"<div style='text-align: right;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    
    # Refresh button
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.rerun()
    
    # Define stock lists for different indices
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
        'LT': 'LT.NS',
        'KOTAKBANK': 'KOTAKBANK.NS',
        'HCLTECH': 'HCLTECH.NS',
        'BAJFINANCE': 'BAJFINANCE.NS',
        'ASIANPAINT': 'ASIANPAINT.NS',
        'MARUTI': 'MARUTI.NS'
    }
    
    nifty_next50_stocks = {
        'PEL': 'PEL.NS',
        'ADANIENT': 'ADANIENT.NS',
        'ADANIPORTS': 'ADANIPORTS.NS',
        'DIVISLAB': 'DIVISLAB.NS',
        'DRREDDY': 'DRREDDY.NS',
        'GRASIM': 'GRASIM.NS',
        'JSWSTEEL': 'JSWSTEEL.NS',
        'EICHERMOT': 'EICHERMOT.NS',
        'ULTRACEMCO': 'ULTRACEMCO.NS',
        'BAJAJFINSV': 'BAJAJFINSV.NS'
    }
    
    sensex_stocks = {
        'RELIANCE': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'HDFCBANK': 'HDFCBANK.NS',
        'ICICIBANK': 'ICICIBANK.NS',
        'HINDUNILVR': 'HINDUNILVR.NS',
        'INFY': 'INFY.NS',
        'ITC': 'ITC.NS',
        'SBIN': 'SBIN.NS',
        'BHARTIARTL': 'BHARTIARTL.NS',
        'LT': 'LT.NS',
        'KOTAKBANK': 'KOTAKBANK.NS',
        'HCLTECH': 'HCLTECH.NS',
        'BAJFINANCE': 'BAJFINANCE.NS',
        'ASIANPAINT': 'ASIANPAINT.NS',
        'MARUTI': 'MARUTI.NS'
    }
    
    large_cap_stocks = {
        'TITAN': 'TITAN.NS',
        'NESTLEIND': 'NESTLEIND.NS',
        'BRITANNIA': 'BRITANNIA.NS',
        'HDFCLIFE': 'HDFCLIFE.NS',
        'ONGC': 'ONGC.NS',
        'TATASTEEL': 'TATASTEEL.NS',
        'SUNPHARMA': 'SUNPHARMA.NS',
        'NTPC': 'NTPC.NS',
        'POWERGRID': 'POWERGRID.NS',
        'COALINDIA': 'COALINDIA.NS'
    }
    
    mid_cap_stocks = {
        'DABUR': 'DABUR.NS',
        'BAJAJHLDNG': 'BAJAJHLDNG.NS',
        'INDUSINDBK': 'INDUSINDBK.NS',
        'PIDILITIND': 'PIDILITIND.NS',
        'SIEMENS': 'SIEMENS.NS',
        'HAVELLS': 'HAVELLS.NS',
        'GODREJCP': 'GODREJCP.NS',
        'AMBUJACEM': 'AMBUJACEM.NS',
        'MOTHERSON': 'MOTHERSON.NS',
        'AUROPHARMA': 'AUROPHARMA.NS'
    }
    
    # Nifty 50 Section
    st.markdown("## 🇮🇳 NIFTY 50")
    with st.spinner("Loading Nifty 50 data..."):
        nifty50_data = get_stock_data(nifty50_stocks)
        display_gainers_losers(nifty50_data, "Nifty 50", num=10)
    
    st.markdown("---")
    
    # Nifty Next 50 Section
    st.markdown("## 🇮🇳 NIFTY NEXT 50")
    with st.spinner("Loading Nifty Next 50 data..."):
        nifty_next50_data = get_stock_data(nifty_next50_stocks)
        display_gainers_losers(nifty_next50_data, "Nifty Next 50", num=10)
    
    st.markdown("---")
    
    # Sensex Section
    st.markdown("## 🇮🇳 SENSEX")
    with st.spinner("Loading Sensex data..."):
        sensex_data = get_stock_data(sensex_stocks)
        display_gainers_losers(sensex_data, "Sensex", num=10)
    
    st.markdown("---")
    
    # Large Cap Section
    st.markdown("## 📊 Large Cap Stocks")
    with st.spinner("Loading Large Cap data..."):
        large_cap_data = get_stock_data(large_cap_stocks)
        display_gainers_losers(large_cap_data, "Large Cap", num=10)
    
    st.markdown("---")
    
    # Mid Cap Section
    st.markdown("## 📊 Mid Cap Stocks")
    with st.spinner("Loading Mid Cap data..."):
        mid_cap_data = get_stock_data(mid_cap_stocks)
        display_gainers_losers(mid_cap_data, "Mid Cap", num=10)
    
    show_footer()

if __name__ == "__main__":
    main()