import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz  # For timezone handling

# Configuration
IST = pytz.timezone('Asia/Kolkata')
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST
REFRESH_INTERVAL = 300  # 5 minutes in seconds

# Known market holidays (add more as needed)
MARKET_HOLIDAYS = [
    '2023-01-26', '2023-03-07', '2023-03-30', '2023-04-04',
    '2023-04-07', '2023-04-14', '2023-05-01', '2023-06-28',
    '2023-08-15', '2023-09-19', '2023-10-02', '2023-10-24',
    '2023-11-14', '2023-11-27', '2023-12-25'
    # Add future holidays here
]

def is_market_open():
    """Check if market is currently open with timezone and holiday awareness"""
    now_ist = datetime.now(IST)
    
    # Check if weekend
    if now_ist.weekday() >= 5:  # 5=Saturday, 6=Sunday
        return False
    
    # Check if holiday
    if now_ist.strftime('%Y-%m-%d') in MARKET_HOLIDAYS:
        return False
    
    # Check market hours
    market_open = now_ist.replace(hour=MARKET_OPEN_TIME[0], minute=MARKET_OPEN_TIME[1], second=0, microsecond=0)
    market_close = now_ist.replace(hour=MARKET_CLOSE_TIME[0], minute=MARKET_CLOSE_TIME[1], second=0, microsecond=0)
    
    return market_open <= now_ist <= market_close

def get_last_trading_day():
    """Get the most recent trading day (skips weekends/holidays)"""
    day = datetime.now(IST)
    for i in range(1, 6):  # Check up to 5 days back
        prev_day = day - timedelta(days=i)
        if prev_day.weekday() < 5 and prev_day.strftime('%Y-%m-%d') not in MARKET_HOLIDAYS:
            return prev_day.date()
    return day.date()  # fallback

@st.cache_data(ttl=REFRESH_INTERVAL, show_spinner=False)
def get_cached_data(symbol, period, force_live=False):
    """Get cached stock data with time-based invalidation"""
    try:
        ticker = yf.Ticker(symbol)
        
        # For intraday data during market hours
        if force_live and is_market_open() and period == "1d":
            data = ticker.history(period="1d", interval="5m")
        else:
            data = ticker.history(period=period)
            
        if data.empty:
            return None
        return data
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def get_stock_performance(symbol, name):
    """Get performance data for a stock with improved live data handling"""
    try:
        market_open = is_market_open()
        
        if market_open:
            # Get intraday data with smaller interval during market hours
            hist = get_cached_data(symbol, "1d", force_live=True)
            if hist is None or hist.empty:
                return None
                
            current_data = hist.iloc[-1]
            prev_close = hist.iloc[0]['Open'] if len(hist) > 1 else current_data['Open']
            data_source = "Live Market Data"
        else:
            # Get last trading day data
            hist = get_cached_data(symbol, "5d")
            if hist is None:
                return None
                
            # Find most recent trading day
            trading_days = hist[hist['Volume'] > 0]
            if trading_days.empty:
                return None
                
            current_data = trading_days.iloc[-1]
            prev_close = trading_days.iloc[-2]['Close'] if len(trading_days) > 1 else current_data['Open']
            data_source = "Last Trading Day"
        
        # Calculate performance metrics
        current_price = current_data['Close']
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Get weekly and monthly changes
        hist_1w = get_cached_data(symbol, "5d")
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
            'As of Date': current_data.name.strftime('%Y-%m-%d %H:%M') if hasattr(current_data.name, 'strftime') else 'N/A',
            'Market Status': 'OPEN' if market_open else 'CLOSED'
        }
    except Exception as e:
        st.error(f"Error processing {name}: {str(e)}")
        return None

def main():
    # Page configuration
    st.set_page_config(
        page_title="Nifty 50 Live Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Auto-refresh placeholder
    refresh_placeholder = st.empty()
    
    # Header section
    st.title("📊 Nifty 50 Live Market Dashboard")
    current_time = datetime.now(IST).strftime('%Y-%m-%d %H:%M:%S %Z')
    st.markdown(f"*Last updated: {current_time}*")
    
    # Market status with more detailed information
    market_open = is_market_open()
    if market_open:
        next_close = datetime.now(IST).replace(
            hour=MARKET_CLOSE_TIME[0],
            minute=MARKET_CLOSE_TIME[1],
            second=0,
            microsecond=0
        )
        time_left = next_close - datetime.now(IST)
        st.success(f"""
        ✅ **Market Status:** OPEN (Live data)  
        ⏳ **Market closes in:** {str(time_left).split('.')[0]}
        """)
        
        # Auto-refresh countdown
        with refresh_placeholder:
            st.info(f"🔃 Auto-refreshing every {REFRESH_INTERVAL//60} minutes")
    else:
        last_trading_day = get_last_trading_day()
        st.warning(f"""
        ⚠️ **Market Status:** CLOSED  
        📅 **Last trading day:** {last_trading_day.strftime('%A, %d %B %Y')}
        """)
    
    # Refresh button
    if st.button("🔄 Refresh Data Now", help="Force immediate data refresh"):
        st.cache_data.clear()
        st.rerun()
    
    # Rest of your implementation...
    # ... (keep your data loading and display logic)

if __name__ == "__main__":
    main()