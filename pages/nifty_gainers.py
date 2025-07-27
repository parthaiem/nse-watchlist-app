import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import time

# Configuration
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST

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

@lru_cache(maxsize=128)
def get_cached_data(symbol, period):
    """Get cached stock data with error handling"""
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
            # Get live market data
            hist = get_cached_data(symbol, "1d")
            if hist is None:
                return None
            current_data = hist.iloc[-1]
            data_source = "Live Market Data"
        else:
            # Get last trading day data
            current_data = get_last_trading_data(symbol)
            if current_data is None:
                return None
            data_source = "Last Trading Day"
        
        # Calculate performance metrics
        current_price = current_data['Close']
        prev_close = current_data['Open'] if 'Open' in current_data else current_data['Close']
        
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Get additional timeframes
        hist_1w = get_cached_data(symbol, "1wk")
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

def color_change(val):
    """Color formatting for percentage changes"""
    if isinstance(val, (int, float)):
        color = 'green' if val >= 0 else 'red'
        return f'color: {color}; font-weight: bold;'
    return ''

def main():
    # Page configuration
    st.set_page_config(
        page_title="Nifty 50 Analysis Dashboard",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
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
        get_cached_data.cache_clear()
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
    
    # Main dashboard sections
    tab1, tab2 = st.tabs(["📊 Complete View", "🏆 Top Performers"])
    
    with tab1:
        # Complete Nifty 50 view
        st.subheader("📜 Complete Nifty 50 Stocks Performance")
        st.dataframe(
            df.style.format({
                'LTP': '₹{:.2f}',
                'Change (%)': '{:+.2f}%',
                '1W Change (%)': '{:+.2f}%',
                '1M Change (%)': '{:+.2f}%'
            }).applymap(color_change, subset=['Change (%)', '1W Change (%)', '1M Change (%)']),
            height=800,
            use_container_width=True,
            column_config={
                "Company": "Company",
                "Symbol": "Symbol",
                "LTP": st.column_config.NumberColumn("Last Price", format="₹%.2f"),
                "Change (%)": "Daily Change",
                "1W Change (%)": "1-Week Change",
                "1M Change (%)": "1-Month Change",
                "Data Source": "Data Source",
                "As of Date": "As of Date"
            }
        )
    
    with tab2:
        # Top performers section
        st.subheader("🏆 Top Performers")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🟢 Top 5 Gainers")
            gainers = df.nlargest(5, 'Change (%)')
            st.dataframe(
                gainers.style.format({
                    'LTP': '₹{:.2f}',
                    'Change (%)': '{:+.2f}%',
                    '1W Change (%)': '{:+.2f}%',
                    '1M Change (%)': '{:+.2f}%'
                }).applymap(color_change, subset=['Change (%)', '1W Change (%)', '1M Change (%)']),
                use_container_width=True,
                hide_index=True
            )
        
        with col2:
            st.markdown("### 🔴 Top 5 Losers")
            losers = df.nsmallest(5, 'Change (%)')
            st.dataframe(
                losers.style.format({
                    'LTP': '₹{:.2f}',
                    'Change (%)': '{:+.2f}%',
                    '1W Change (%)': '{:+.2f}%',
                    '1M Change (%)': '{:+.2f}%'
                }).applymap(color_change, subset=['Change (%)', '1W Change (%)', '1M Change (%)']),
                use_container_width=True,
                hide_index=True
            )
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <p style='font-size: 16px;'>📊 <strong>FinSmart Market Analytics</strong></p>
        <p>Data Source: Yahoo Finance | NSE India</p>
        <p>📞 Contact: +91 XXXXXXXXXX | ✉️ info@finsmart.com</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()