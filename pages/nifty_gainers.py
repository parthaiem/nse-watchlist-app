import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import time

# Configuration
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST
REFRESH_INTERVAL = 300  # 5 minutes in seconds

# Complete Nifty 50 stocks with symbols
NIFTY_50_STOCKS = {
    'ADANI PORTS': 'ADANIPORTS.NS',
    # ... (rest of your stock dictionary remains the same)
}

@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def get_cached_data(symbol, period):
    """Get cached stock data with error handling and time-based invalidation"""
    try:
        data = yf.Ticker(symbol).history(period=period)
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def is_market_open():
    """Check if market is currently open"""
    now = datetime.now()
    market_open = datetime(now.year, now.month, now.day, *MARKET_OPEN_TIME)
    market_close = datetime(now.year, now.month, now.day, *MARKET_CLOSE_TIME)
    return market_open <= now <= market_close

def get_last_trading_data(symbol):
    """Get data from the last trading day"""
    try:
        # Get 5 days data to ensure we find a trading day
        hist = get_cached_data(symbol, "5d")
        if hist is None:
            return None
            
        # Find most recent day with trading volume
        trading_days = hist[hist['Volume'] > 0]
        if not trading_days.empty:
            return trading_days.iloc[-1]
    except Exception as e:
        st.error(f"Error fetching last trading data: {str(e)}")
    return None

def get_stock_performance(symbol, name):
    """Get performance data for a stock"""
    try:
        if is_market_open():
            # For intraday data during market hours
            hist = get_cached_data(symbol, "1d")
            if hist is None or hist.empty:
                return None
            
            # Get the latest data point
            current_data = hist.iloc[-1]
            data_source = "Live Market Data"
            
            # For intraday, we need to compare with today's open
            prev_close = hist.iloc[0]['Open'] if len(hist) > 1 else current_data['Open']
        else:
            # Get last trading day data
            current_data = get_last_trading_data(symbol)
            if current_data is None:
                return None
            data_source = "Last Trading Day"
            prev_close = current_data['Open']
        
        # Calculate performance metrics
        current_price = current_data['Close']
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Get additional timeframes
        hist_1w = get_cached_data(symbol, "5d")  # 5 days covers a week
        week_change = ((current_price - hist_1w['Close'][0]) / hist_1w['Close'][0]) * 100 if hist_1w is not None and not hist_1w.empty else None
        
        hist_1m = get_cached_data(symbol, "1mo")
        month_change = ((current_price - hist_1m['Close'][0]) / hist_1m['Close'][0]) * 100 if hist_1m is not None and not hist_1m.empty else None
        
        return {
            'Company': name,
            'Symbol': symbol,
            'LTP': current_price,
            'Change (%)': day_change,
            '1W Change (%)': week_change,
            '1M Change (%)': month_change,
            'Data Source': data_source,
            'As of Date': current_data.name.strftime('%Y-%m-%d %H:%M') if hasattr(current_data.name, 'strftime') else 'N/A'
        }
    except Exception as e:
        st.error(f"Error processing {name}: {str(e)}")
        return None

def main():
    # Page configuration
    st.set_page_config(
        page_title="Nifty 50 Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Auto-refresh logic
    if is_market_open():
        st_autorefresh = st.empty()
        st_autorefresh.info(f"🔃 Auto-refreshing every {REFRESH_INTERVAL//60} minutes during market hours")
    
    # Header section
    st.title("📊 Nifty 50 Market Dashboard")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Market status indicator
    if is_market_open():
        st.success("✅ **Market Status:** OPEN (Live data)")
    else:
        st.warning("⚠️ **Market Status:** CLOSED (Showing last trading day data)")
    
    # Refresh button
    if st.button("🔄 Refresh Data", help="Click to refresh all data"):
        st.cache_data.clear()
        st.rerun()
    
    # Load data with progress
    with st.spinner("Loading Nifty 50 data. Please wait..."):
        progress_bar = st.progress(0)
        data = []
        total_stocks = len(NIFTY_50_STOCKS)
        
        for i, (name, symbol) in enumerate(NIFTY_50_STOCKS.items()):
            stock_data = get_stock_performance(symbol, name)
            if stock_data:
                data.append(stock_data)
            progress_bar.progress((i + 1) / total_stocks)
            time.sleep(0.1)  # Rate limiting
        
        df = pd.DataFrame(data)
    
    # Check if data loaded successfully
    if df.empty:
        st.error("⚠️ No data available. Please check your internet connection and try again.")
        return
    
    # Rest of your display code remains the same...
    # ... (keep your tab1, tab2, and footer sections as they were)

if __name__ == "__main__":
    main()