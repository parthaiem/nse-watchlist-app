import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Configuration
IST = pytz.timezone('Asia/Kolkata')
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST
ROWS_PER_PAGE = 10

# Complete Nifty 50 stocks with symbols
NIFTY_50_STOCKS = {
    'ADANI PORTS': 'ADANIPORTS.NS',
    'ASIAN PAINT': 'ASIANPAINT.NS',
    'AXIS BANK': 'AXISBANK.NS',
    'BAJAJ AUTO': 'BAJAJ-AUTO.NS',
    'BAJAJ FINSV': 'BAJAJFINSV.NS',
    'BAJAJ FINANCE': 'BAJFINANCE.NS',
    'BHARTI AIRTEL': 'BHARTIARTL.NS',
    'BPCL': 'BPCL.NS',
    'BRITANNIA': 'BRITANNIA.NS',
    'CIPLA': 'CIPLA.NS',
    'COAL INDIA': 'COALINDIA.NS',
    'DIVIS LAB': 'DIVISLAB.NS',
    'DR. REDDYS': 'DRREDDY.NS',
    'EICHER MOTORS': 'EICHERMOT.NS',
    'GRASIM': 'GRASIM.NS',
    'HCL TECH': 'HCLTECH.NS',
    'HDFC BANK': 'HDFCBANK.NS',
    'HDFC LIFE': 'HDFCLIFE.NS',
    'HERO MOTOCORP': 'HEROMOTOCO.NS',
    'HINDALCO': 'HINDALCO.NS',
    'HINDUNILVR': 'HINDUNILVR.NS',
    'ICICI BANK': 'ICICIBANK.NS',
    'INDUSIND BANK': 'INDUSINDBK.NS',
    'INFOSYS': 'INFY.NS',
    'ITC': 'ITC.NS',
    'JSW STEEL': 'JSWSTEEL.NS',
    'KOTAK BANK': 'KOTAKBANK.NS',
    'LT': 'LT.NS',
    'M&M': 'M&M.NS',
    'MARUTI': 'MARUTI.NS',
    'NESTLE': 'NESTLEIND.NS',
    'NTPC': 'NTPC.NS',
    'ONGC': 'ONGC.NS',
    'POWERGRID': 'POWERGRID.NS',
    'RELIANCE': 'RELIANCE.NS',
    'SBILIFE': 'SBILIFE.NS',
    'SBIN': 'SBIN.NS',
    'SUN PHARMA': 'SUNPHARMA.NS',
    'TATA CONSUMER': 'TATACONSUM.NS',
    'TATA MOTORS': 'TATAMOTORS.NS',
    'TATA STEEL': 'TATASTEEL.NS',
    'TCS': 'TCS.NS',
    'TECH MAHINDRA': 'TECHM.NS',
    'TITAN': 'TITAN.NS',
    'ULTRATECH CEMENT': 'ULTRACEMCO.NS',
    'UPL': 'UPL.NS',
    'WIPRO': 'WIPRO.NS'
}

# Initialize session state for pagination
if 'page_number' not in st.session_state:
    st.session_state.page_number = 0
if 'df' not in st.session_state:
    st.session_state.df = None

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

def get_stock_data(symbol):
    """Get stock data with error handling"""
    try:
        ticker = yf.Ticker(symbol)
        
        # Get current data (1d for intraday or 5d for last close)
        current_data = ticker.history(period="1d" if is_market_open() else "5d")
        if current_data.empty:
            return None
            
        # Get 52-week data
        yearly_data = ticker.history(period="1y")
        high_52w = yearly_data['High'].max() if not yearly_data.empty else None
        low_52w = yearly_data['Low'].min() if not yearly_data.empty else None
        
        return {
            'current_data': current_data,
            'high_52w': high_52w,
            'low_52w': low_52w
        }
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
    if value is None:
        return "N/A"
    return f"₹{safe_float(value):,.2f}"

def get_paginated_data(df, page_number, rows_per_page):
    """Return a slice of data for the current page"""
    start_idx = page_number * rows_per_page
    end_idx = start_idx + rows_per_page
    return df.iloc[start_idx:end_idx]

def load_all_data():
    """Load data for all stocks"""
    data = []
    progress_bar = st.progress(0)
    total_stocks = len(NIFTY_50_STOCKS)
    
    for i, (name, symbol) in enumerate(NIFTY_50_STOCKS.items()):
        stock_data = get_stock_data(symbol)
        if stock_data is None:
            continue
            
        current_data = stock_data['current_data']
        if is_market_open():
            current_price = safe_float(current_data.iloc[-1]['Close'])
            prev_close = safe_float(current_data.iloc[0]['Open'] if len(current_data) > 1 else current_data.iloc[-1]['Close'])
        else:
            trading_days = current_data[current_data['Volume'] > 0]
            if trading_days.empty:
                continue
            current_price = safe_float(trading_days.iloc[-1]['Close'])
            prev_close = safe_float(trading_days.iloc[-2]['Close'] if len(trading_days) > 1 else trading_days.iloc[-1]['Open'])
        
        # Calculate changes
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Get weekly change
        weekly_data = yf.Ticker(symbol).history(period="5d")
        week_change = ((current_price - weekly_data.iloc[0]['Close']) / weekly_data.iloc[0]['Close']) * 100 if not weekly_data.empty else None
        
        # Get monthly change
        monthly_data = yf.Ticker(symbol).history(period="1mo")
        month_change = ((current_price - monthly_data.iloc[0]['Close']) / monthly_data.iloc[0]['Close']) * 100 if not monthly_data.empty else None
        
        data.append({
            'Company': name,
            'Current Price': current_price,
            'Daily Change (%)': day_change,
            'Weekly Change (%)': week_change,
            'Monthly Change (%)': month_change,
            '52-Week High': stock_data['high_52w'],
            '52-Week Low': stock_data['low_52w']
        })
        
        progress_bar.progress((i + 1) / total_stocks)
    
    return pd.DataFrame(data) if data else None

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
    
    # Load data only if not already loaded or refresh requested
    if st.button("🔄 Refresh Data") or st.session_state.df is None:
        with st.spinner("Loading market data..."):
            st.session_state.df = load_all_data()
            st.session_state.page_number = 0  # Reset to first page on refresh
    
    if st.session_state.df is None:
        st.error("No data available. Please try again later.")
        return
    
    # Get paginated data
    total_pages = (len(st.session_state.df) // ROWS_PER_PAGE) + (1 if len(st.session_state.df) % ROWS_PER_PAGE else 0)
    paginated_df = get_paginated_data(st.session_state.df, st.session_state.page_number, ROWS_PER_PAGE)
    
    # Display the table
    display_df = paginated_df.copy()
    display_df['Current Price'] = display_df['Current Price'].apply(format_price)
    display_df['Daily Change (%)'] = display_df['Daily Change (%)'].apply(format_change)
    display_df['Weekly Change (%)'] = display_df['Weekly Change (%)'].apply(format_change)
    display_df['Monthly Change (%)'] = display_df['Monthly Change (%)'].apply(format_change)
    display_df['52-Week High'] = display_df['52-Week High'].apply(format_price)
    display_df['52-Week Low'] = display_df['52-Week Low'].apply(format_price)
    
    st.markdown(
        display_df[[
            'Company', 'Current Price', 'Daily Change (%)',
            'Weekly Change (%)', 'Monthly Change (%)',
            '52-Week High', '52-Week Low'
        ]].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    
    # Pagination controls at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("⏮️ Previous") and st.session_state.page_number > 0:
            st.session_state.page_number -= 1
            st.rerun()
    
    with col2:
        if st.button("Next ⏭️") and st.session_state.page_number < total_pages - 1:
            st.session_state.page_number += 1
            st.rerun()
    
    with col3:
        st.markdown(f"**Page {st.session_state.page_number + 1} of {total_pages} | Showing {len(paginated_df)} stocks**")

if __name__ == "__main__":
    main()
    # ... (keep all the existing code above main() function)

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
    
    # Load data only if not already loaded or refresh requested
    if st.button("🔄 Refresh Data") or st.session_state.df is None:
        with st.spinner("Loading market data..."):
            st.session_state.df = load_all_data()
            st.session_state.page_number = 0  # Reset to first page on refresh
    
    if st.session_state.df is None:
        st.error("No data available. Please try again later.")
        return
    
    # Get paginated data
    total_pages = (len(st.session_state.df) // ROWS_PER_PAGE) + (1 if len(st.session_state.df) % ROWS_PER_PAGE else 0)
    paginated_df = get_paginated_data(st.session_state.df, st.session_state.page_number, ROWS_PER_PAGE)
    
    # Display the table
    display_df = paginated_df.copy()
    display_df['Current Price'] = display_df['Current Price'].apply(format_price)
    display_df['Daily Change (%)'] = display_df['Daily Change (%)'].apply(format_change)
    display_df['Weekly Change (%)'] = display_df['Weekly Change (%)'].apply(format_change)
    display_df['Monthly Change (%)'] = display_df['Monthly Change (%)'].apply(format_change)
    display_df['52-Week High'] = display_df['52-Week High'].apply(format_price)
    display_df['52-Week Low'] = display_df['52-Week Low'].apply(format_price)
    
    st.markdown(
        display_df[[
            'Company', 'Current Price', 'Daily Change (%)',
            'Weekly Change (%)', 'Monthly Change (%)',
            '52-Week High', '52-Week Low'
        ]].to_html(escape=False, index=False),
        unsafe_allow_html=True
    )
    
    # New Section: Stocks Near 52-Week Low
    st.markdown("---")
    st.subheader("📉 Stocks Near 52-Week Low (Potential Buying Opportunities)")
    
    # Calculate distance from 52-week low (within 5%)
    if st.session_state.df is not None:
        df = st.session_state.df.copy()
        df['Distance from 52W Low (%)'] = ((df['Current Price'] - df['52-Week Low']) / df['52-Week Low']) * 100
        near_low_df = df[(df['Distance from 52W Low (%)'] <= 5) & (df['Distance from 52W Low (%)'] >= 0)].sort_values('Distance from 52W Low (%)')
        
        if not near_low_df.empty:
            # Format the display dataframe
            display_near_low = near_low_df.copy()
            display_near_low['Current Price'] = display_near_low['Current Price'].apply(format_price)
            display_near_low['52-Week Low'] = display_near_low['52-Week Low'].apply(format_price)
            display_near_low['Distance from 52W Low (%)'] = display_near_low['Distance from 52W Low (%)'].apply(lambda x: f"{x:.2f}%")
            
            # Add color to distance column
            def color_distance(val):
                distance = float(val.strip('%'))
                if distance <= 2:
                    return f"<span style='color: red; font-weight: bold'>{val}</span>"
                elif distance <= 5:
                    return f"<span style='color: orange'>{val}</span>"
                return val
            
            display_near_low['Distance from 52W Low (%)'] = display_near_low['Distance from 52W Low (%)'].apply(color_distance)
            
            st.markdown(
                display_near_low[[
                    'Company', 'Current Price', '52-Week Low', 
                    'Distance from 52W Low (%)', 'Daily Change (%)'
                ]].to_html(escape=False, index=False),
                unsafe_allow_html=True
            )
            
            st.caption("💡 **Note:** Stocks within 5% of their 52-week low. Those in red are within 2% of their low.")
        else:
            st.info("No stocks are currently within 5% of their 52-week low.")
    
    # Pagination controls at the bottom
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        if st.button("⏮️ Previous") and st.session_state.page_number > 0:
            st.session_state.page_number -= 1
            st.rerun()
    
    with col2:
        if st.button("Next ⏭️") and st.session_state.page_number < total_pages - 1:
            st.session_state.page_number += 1
            st.rerun()
    
    with col3:
        st.markdown(f"**Page {st.session_state.page_number + 1} of {total_pages} | Showing {len(paginated_df)} stocks**")

if __name__ == "__main__":
    main()