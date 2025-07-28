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
def get_cached_data(symbol, period):
    """Get cached stock data with error handling"""
    try:
        data = yf.Ticker(symbol).history(period=period)
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
    if value is None:
        return "N/A"
    value = safe_float(value)
    color = "green" if value >= 0 else "red"
    arrow = "↑" if value >= 0 else "↓"
    return f"<span style='color: {color}'>{arrow} {abs(value):.2f}%</span>"

def format_price(value):
    """Format price with INR symbol"""
    return f"₹{safe_float(value):,.2f}"

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
                    # Get intraday data during market hours
                    current_data = get_cached_data(symbol, "1d")
                    if current_data is None or current_data.empty:
                        continue
                        
                    current_data = current_data.iloc[-1]
                    current_price = safe_float(current_data['Close'])
                    prev_close = safe_float(current_data['Open'] if 'Open' in current_data else current_data['Close'])
                    data_source = "Live Data"
                else:
                    # Get last trading day data
                    current_data = get_cached_data(symbol, "5d")
                    if current_data is None or current_data.empty:
                        continue
                        
                    trading_days = current_data[current_data['Volume'] > 0]
                    if trading_days.empty:
                        continue
                        
                    current_data = trading_days.iloc[-1]
                    current_price = safe_float(current_data['Close'])
                    prev_close = safe_float(trading_days.iloc[-2]['Close'] if len(trading_days) > 1 else current_data['Open'])
                    data_source = f"Last Trading Day ({last_trading_day.strftime('%d-%b')})"
                
                # Calculate daily change
                day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
                
                # Calculate weekly change
                hist_1w = get_cached_data(symbol, "1wk")
                week_change = ((current_price - hist_1w['Close'][0]) / hist_1w['Close'][0]) * 100 if hist_1w is not None and not hist_1w.empty else None
                
                # Calculate monthly change
                hist_1m = get_cached_data(symbol, "1mo")
                month_change = ((current_price - hist_1m['Close'][0]) / hist_1m['Close'][0]) * 100 if hist_1m is not None and not hist_1m.empty else None
                
                data.append({
                    'Company': name,
                    'Symbol': symbol,
                    'LTP': current_price,
                    'Daily Change (%)': day_change,
                    'Weekly Change (%)': week_change,
                    'Monthly Change (%)': month_change,
                    'Data Source': data_source
                })
            except Exception as e:
                st.error(f"Error processing {name}: {str(e)}")
                continue
        
        if not data:
            st.error("No data available. Please try again later.")
            return
        
        df = pd.DataFrame(data)
    
    # Display the DataFrame with all parameters
    try:
        # Create a display copy with formatted values
        display_df = df.copy()
        display_df['LTP'] = display_df['LTP'].apply(format_price)
        display_df['Daily Change (%)'] = display_df['Daily Change (%)'].apply(format_change)
        display_df['Weekly Change (%)'] = display_df['Weekly Change (%)'].apply(format_change)
        display_df['Monthly Change (%)'] = display_df['Monthly Change (%)'].apply(format_change)
        
        # Display using HTML to preserve styling
        st.markdown(
            display_df[['Company', 'Symbol', 'LTP', 'Daily Change (%)', 
                      'Weekly Change (%)', 'Monthly Change (%)', 'Data Source']]
            .to_html(escape=False, index=False),
            unsafe_allow_html=True
        )
        
        # Add some space and metrics
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stocks Tracked", len(df))
        with col2:
            avg_daily_change = df['Daily Change (%)'].mean()
            st.metric("Avg Daily Change", f"{avg_daily_change:.2f}%")
        with col3:
            positive_stocks = len(df[df['Daily Change (%)'] > 0])
            st.metric("Advancing Stocks", positive_stocks)
            
    except Exception as e:
        st.error(f"Error displaying data: {str(e)}")
        st.dataframe(df)  # Fallback to simple display

if __name__ == "__main__":
    main()