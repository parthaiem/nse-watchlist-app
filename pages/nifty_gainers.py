import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import requests
from functools import lru_cache
import time
from supabase_helper import get_watchlist

# Initialize session states
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Configuration
CACHE_EXPIRY = 60 * 5  # 5 minutes cache
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM

# Complete list of Nifty 50 stocks with their symbols
NIFTY_50_STOCKS = {
    'ADANI PORTS': 'ADANIPORTS.NS',
    'ASIAN PAINT': 'ASIANPAINT.NS',
    # ... [rest of your NIFTY_50_STOCKS dictionary]
}

# Cache with expiry
@lru_cache(maxsize=128)
def get_cached_data(symbol, period):
    try:
        return yf.Ticker(symbol).history(period=period)
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def is_market_open():
    now = datetime.now()
    market_open = datetime(now.year, now.month, now.day, *MARKET_OPEN_TIME)
    market_close = datetime(now.year, now.month, now.day, *MARKET_CLOSE_TIME)
    return market_open <= now <= market_close

def is_market_holiday():
    try:
        today = datetime.now().strftime("%d-%m-%Y")
        url = f"https://www.nseindia.com/api/holiday-master?type=trading"
        response = requests.get(url, timeout=5)
        holidays = response.json().get('holidayMaster', [])
        return today in [h['tradingDate'] for h in holidays]
    except:
        return False

def get_last_trading_day_data(symbol):
    """Get data from the last trading day"""
    try:
        # Get data for last 5 days to ensure we get at least one trading day
        hist = yf.Ticker(symbol).history(period="5d")
        if not hist.empty:
            # Get the most recent day with trading volume
            last_trading_day = hist[hist['Volume'] > 0].iloc[-1]
            return last_trading_day
    except Exception as e:
        st.error(f"Error fetching last trading data for {symbol}: {str(e)}")
    return None

def show_header():
    # ... [your existing show_header function]

def show_footer():
    # ... [your existing show_footer function]

def color_change(val):
    # ... [your existing color_change function]

def get_stock_performance(symbol, name):
    try:
        if is_market_open():
            # Get current day data if market is open
            hist_1d = get_cached_data(symbol, "1d")
            current_data = hist_1d.iloc[-1] if hist_1d is not None and not hist_1d.empty else None
        else:
            # Get last trading day data if market is closed
            current_data = get_last_trading_day_data(symbol)
            if current_data is not None:
                st.warning("Market is closed. Showing last trading day data.")
        
        if current_data is None:
            return None

        # Get historical data for weekly/monthly changes
        hist_1w = get_cached_data(symbol, "1wk")
        hist_1m = get_cached_data(symbol, "1mo")
        
        current_price = current_data['Close']
        prev_close = current_data['Open'] if 'Open' in current_data else current_data['Close']
        
        # Calculate changes
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Weekly change
        if hist_1w is not None and not hist_1w.empty:
            week_ago_price = hist_1w['Close'][0]
            week_change = ((current_price - week_ago_price) / week_ago_price) * 100 if week_ago_price != 0 else 0
        else:
            week_change = 0
            
        # Monthly change
        if hist_1m is not None and not hist_1m.empty:
            month_ago_price = hist_1m['Close'][0]
            month_change = ((current_price - month_ago_price) / month_ago_price) * 100 if month_ago_price != 0 else 0
        else:
            month_change = 0
            
        return {
            'Company': name,
            'Symbol': symbol,
            'LTP': current_price,
            'Change (%)': day_change,
            '1W Change (%)': week_change,
            '1M Change (%)': month_change,
            'Data Date': current_data.name.strftime('%Y-%m-%d') if hasattr(current_data.name, 'strftime') else 'N/A'
        }
    except Exception as e:
        st.warning(f"Error processing {name}: {str(e)}")
        return None

def get_nifty50_data():
    data = []
    market_status = "open" if is_market_open() else "closed"
    
    for name, symbol in NIFTY_50_STOCKS.items():
        if is_market_holiday():
            st.warning("Today is a market holiday. Showing last available data.")
            break
            
        performance = get_stock_performance(symbol, name)
        if performance:
            data.append(performance)
        
        # Rate limiting to avoid overwhelming the API
        time.sleep(0.1)
    
    return pd.DataFrame(data)

def display_performance(df, title, num=5):
    # ... [your existing display_performance function]

def main():
    st.set_page_config(page_title="Nifty 50 Analysis", layout="wide")
    show_header()
    
    st.markdown(f"<div style='text-align: right;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        get_cached_data.cache_clear()
        st.rerun()
    
    # Get all Nifty 50 data
    with st.spinner("Loading Nifty 50 data..."):
        nifty50_data = get_nifty50_data()
    
    # Show market status
    if is_market_holiday():
        st.warning("⚠️ Today is a market holiday. Showing last trading day data.")
    elif not is_market_open():
        st.warning("⚠️ Market is currently closed. Showing last trading day data.")
    else:
        st.success("✅ Market is currently open. Showing live data.")
    
    # Show complete list of Nifty 50 stocks
    st.markdown("## 📜 Complete Nifty 50 Stocks List")
    if not nifty50_data.empty:
        st.dataframe(
            nifty50_data.style.format({
                'LTP': '₹{:.2f}',
                'Change (%)': '{:+.2f}%',
                '1W Change (%)': '{:+.2f}%',
                '1M Change (%)': '{:+.2f}%'
            }).applymap(color_change, subset=['Change (%)', '1W Change (%)', '1M Change (%)']),
            use_container_width=True,
            height=800
        )
    
        # Display performance tables
        display_performance(nifty50_data, "Nifty 50")
    else:
        st.error("No data available. Please try again later.")
    
    show_footer()

if __name__ == "__main__":
    main()