import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Configuration
IST = pytz.timezone('Asia/Kolkata')
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST

# Complete Nifty 50 stocks with symbols
NIFTY_50_STOCKS = {
    'ADANI PORTS': 'ADANIPORTS.NS',
    'ASIAN PAINT': 'ASIANPAINT.NS',
    # ... (rest of your stock dictionary)
}

def is_market_open():
    """Check if market is currently open in IST"""
    now_ist = datetime.now(IST)
    if now_ist.weekday() >= 5:  # Weekend
        return False
    market_open = now_ist.replace(hour=MARKET_OPEN_TIME[0], minute=MARKET_OPEN_TIME[1], second=0, microsecond=0)
    market_close = now_ist.replace(hour=MARKET_CLOSE_TIME[0], minute=MARKET_CLOSE_TIME[1], second=0, microsecond=0)
    return market_open <= now_ist <= market_close

def get_last_trading_day():
    """Get the most recent trading day (skips weekends)"""
    day = datetime.now(IST)
    for i in range(1, 6):  # Check up to 5 days back
        prev_day = day - timedelta(days=i)
        if prev_day.weekday() < 5:  # Monday-Friday
            return prev_day
    return day  # fallback

@st.cache_data(ttl=3600)
def get_historical_data(symbol, days=5):
    """Get historical data with error handling"""
    try:
        end_date = datetime.now(IST)
        start_date = end_date - timedelta(days=days)
        data = yf.download(symbol, start=start_date, end=end_date)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def safe_float(value, default=0.0):
    """Safely convert to float with fallback"""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default

def format_change(value):
    """Format percentage change with color"""
    value = safe_float(value)
    color = "green" if value >= 0 else "red"
    return f"<span style='color: {color}'>{value:+.2f}%</span>"

def main():
    st.set_page_config(
        page_title="Nifty 50 Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("📊 Nifty 50 Market Dashboard")
    
    # Market status
    market_open = is_market_open()
    last_trading_day = get_last_trading_day()
    
    if market_open:
        st.success("✅ **Market Status:** OPEN (Live data)")
    else:
        st.warning(f"""
        ⚠️ **Market Status:** CLOSED  
        📅 **Last trading day:** {last_trading_day.strftime('%A, %d %B %Y')}
        """)
    
    if st.button("🔄 Refresh Data"):
        st.cache_data.clear()
        st.rerun()
    
    # Load data with progress
    with st.spinner("Loading market data..."):
        data = []
        for name, symbol in NIFTY_50_STOCKS.items():
            try:
                if market_open:
                    stock_data = yf.Ticker(symbol).history(period='1d')
                    if stock_data.empty:
                        continue
                    current = stock_data.iloc[-1]
                    prev_close = stock_data.iloc[0]['Open'] if len(stock_data) > 1 else current['Open']
                    data_source = "Live"
                else:
                    hist_data = get_historical_data(symbol)
                    if hist_data is None:
                        continue
                    trading_days = hist_data[hist_data['Volume'] > 0]
                    if trading_days.empty:
                        continue
                    current = trading_days.iloc[-1]
                    prev_close = trading_days.iloc[-2]['Close'] if len(trading_days) > 1 else current['Open']
                    data_source = f"Last Trading Day ({last_trading_day.strftime('%d-%b')})"
                
                change_pct = ((safe_float(current['Close']) - safe_float(prev_close)) / safe_float(prev_close)) * 100
                
                data.append({
                    'Company': name,
                    'Symbol': symbol,
                    'LTP': safe_float(current['Close']),
                    'Change (%)': change_pct,
                    'Data Source': data_source
                })
            except Exception as e:
                st.error(f"Error processing {name}: {str(e)}")
                continue
        
        if not data:
            st.error("No data available. Please try again later.")
            return
        
        df = pd.DataFrame(data)
    
    # Display the DataFrame safely
    try:
        # Convert numeric columns for display
        display_df = df.copy()
        display_df['LTP'] = display_df['LTP'].apply(lambda x: f"₹{x:,.2f}")
        display_df['Change (%)'] = display_df['Change (%)'].apply(format_change)
        
        # Display using HTML to preserve styling
        st.markdown(
            display_df[['Company', 'Symbol', 'LTP', 'Change (%)', 'Data Source']]
            .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")
        st.write(df)  # Fallback to simple display

if __name__ == "__main__":
    main()