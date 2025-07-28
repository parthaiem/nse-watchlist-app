import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz
from functools import lru_cache

# Configuration
IST = pytz.timezone('Asia/Kolkata')
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST

# Complete Nifty 50 stocks with symbols
NIFTY_50_STOCKS = {
    'ADANI PORTS': 'ADANIPORTS.NS',
    # ... (rest of your stock dictionary)
}

def is_market_open():
    """Check if market is currently open in IST"""
    now_ist = datetime.now(IST)
    
    # Check if weekend (Saturday=5, Sunday=6)
    if now_ist.weekday() >= 5:
        return False
    
    # Check market hours
    market_open = now_ist.replace(hour=MARKET_OPEN_TIME[0], minute=MARKET_OPEN_TIME[1], second=0, microsecond=0)
    market_close = now_ist.replace(hour=MARKET_CLOSE_TIME[0], minute=MARKET_CLOSE_TIME[1], second=0, microsecond=0)
    
    return market_open <= now_ist <= market_close

def get_last_trading_day():
    """Get the most recent trading day (skips weekends)"""
    day = datetime.now(IST)
    days_to_check = 1  # Start checking from yesterday
    
    while days_to_check <= 5:  # Don't look back more than 5 days
        prev_day = day - timedelta(days=days_to_check)
        if prev_day.weekday() < 5:  # Monday-Friday
            return prev_day
        days_to_check += 1
    return day  # fallback

@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_historical_data(symbol, days=5):
    """Get historical data for the symbol"""
    try:
        end_date = datetime.now(IST)
        start_date = end_date - timedelta(days=days)
        data = yf.download(symbol, start=start_date, end=end_date)
        return data
    except Exception as e:
        st.error(f"Error fetching data for {symbol}: {str(e)}")
        return None

def get_last_trading_data(symbol):
    """Get data from the last trading day"""
    data = get_historical_data(symbol)
    if data is None or data.empty:
        return None
    
    # Find the last day with trading volume
    trading_days = data[data['Volume'] > 0]
    if not trading_days.empty:
        return trading_days.iloc[-1]
    return None

def main():
    st.set_page_config(
        page_title="Nifty 50 Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Header
    st.title("📊 Nifty 50 Market Dashboard")
    
    # Market status display
    market_open = is_market_open()
    last_trading_day = get_last_trading_day()
    
    if market_open:
        st.success("✅ **Market Status:** OPEN (Live data)")
    else:
        st.warning(f"""
        ⚠️ **Market Status:** CLOSED  
        📅 **Last trading day:** {last_trading_day.strftime('%A, %d %B %Y')}
        """)
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Load and display data
    with st.spinner("Loading market data..."):
        data = []
        for name, symbol in NIFTY_50_STOCKS.items():
            if market_open:
                # Get live data
                stock_data = yf.Ticker(symbol).history(period='1d')
                if not stock_data.empty:
                    current = stock_data.iloc[-1]
                    prev_close = stock_data.iloc[0]['Open'] if len(stock_data) > 1 else current['Open']
                    data_source = "Live"
            else:
                # Get last trading day data
                current = get_last_trading_data(symbol)
                if current is not None:
                    prev_close = get_historical_data(symbol).iloc[-2]['Close']  # Previous day's close
                    data_source = f"Last Trading Day ({last_trading_day.strftime('%d-%b')})"
                else:
                    continue
            
            # Calculate performance
            change_pct = ((current['Close'] - prev_close) / prev_close) * 100
            
            data.append({
                'Company': name,
                'Symbol': symbol,
                'LTP': current['Close'],
                'Change (%)': change_pct,
                'Data Source': data_source
            })
        
        df = pd.DataFrame(data)
    
    # Display data
    if not df.empty:
        st.dataframe(
            df.style.format({
                'LTP': '₹{:.2f}',
                'Change (%)': '{:+.2f}%'
            }).applymap(
                lambda x: 'color: green' if isinstance(x, (int, float)) and x >= 0 else 'color: red',
                subset=['Change (%)']
            ),
            height=800,
            use_container_width=True
        )
    else:
        st.error("No data available. Please try again later.")

if __name__ == "__main__":
    main()