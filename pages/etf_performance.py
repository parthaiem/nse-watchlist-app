import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import time

# Configuration
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST

# Popular Indian ETFs with their symbols
INDIAN_ETFS = {
    'NIFTY BEES': 'NIFTYBEES.NS',
    'GOLD BEES': 'GOLDBEES.NS',
    'BANK BEES': 'BANKBEES.NS',
    'LIQUID BEES': 'LIQUIDBEES.NS',
    'SILVER BEES': 'SILVERBEES.NS',
    'JUNIOR BEES': 'JUNIORBEES.NS',
    'PSU BANK BEES': 'PSUBANKBEES.NS',
    'CONSUMPTION BEES': 'CONSUMBEES.NS',
    'ENERGY BEES': 'ENERGYBEES.NS',
    'INFRA BEES': 'INFRABEES.NS',
    'MOMENTUM BEES': 'MOM100BEES.NS',
    'SHARIAH BEES': 'SHARIABEES.NS',
    'MON100 BEES': 'MON100BEES.NS',
    'NV20 BEES': 'NV20BEES.NS',
    'CPSE ETF': 'CPSEETF.NS',
    'BHARAT 22 ETF': 'BHARAT22ETF.NS',
    'MIRAE EMERGING BLUECHIP ETF': 'MIRAEEMG.NS',
    'MIRAE ASSET NIFTY NEXT 50 ETF': 'MIRAE_N50.NS',
    'KOTAK NIFTY ETF': 'KOTAKNIFTY.NS',
    'ICICI PRUDENTIAL NIFTY ETF': 'ICICINIFTY.NS'
}

@lru_cache(maxsize=128)
def get_cached_etf_data(symbol, period):
    """Get cached ETF data with error handling"""
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

def get_etf_performance(symbol, name):
    """Get performance data for an ETF"""
    try:
        # Get data for different time periods
        hist_1d = get_cached_etf_data(symbol, "1d")
        hist_1w = get_cached_etf_data(symbol, "1wk")
        hist_1m = get_cached_etf_data(symbol, "1mo")
        hist_1y = get_cached_etf_data(symbol, "1y")
        hist_max = get_cached_etf_data(symbol, "max")
        
        if hist_1d is None:
            return None

        # Current price and daily change
        current_price = hist_1d['Close'][-1]
        prev_close = hist_1d['Open'][0] if 'Open' in hist_1d.columns else hist_1d['Close'][0]
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Calculate changes for different time periods
        def calculate_change(hist, days):
            if hist is None or len(hist) < 2:
                return None
            old_price = hist['Close'][0]
            return ((current_price - old_price) / old_price) * 100 if old_price != 0 else None
        
        week_change = calculate_change(hist_1w, 7)
        month_change = calculate_change(hist_1m, 30)
        year_change = calculate_change(hist_1y, 365)
        
        # Max change since inception
        max_change = None
        if hist_max is not None and len(hist_max) > 1:
            inception_price = hist_max['Close'][0]
            max_change = ((current_price - inception_price) / inception_price) * 100 if inception_price != 0 else None
        
        return {
            'ETF Name': name,
            'Symbol': symbol,
            'Current Price': current_price,
            '1D Change (%)': day_change,
            '1W Change (%)': week_change,
            '1M Change (%)': month_change,
            '1Y Change (%)': year_change,
            'Max Change (%)': max_change,
            'As of Date': hist_1d.index[-1].strftime('%Y-%m-%d %H:%M')
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

def show_header():
    """Consistent header with the other pages"""
    st.set_page_config(page_title="ETF Performance", layout="wide")
    
    # Header layout
    col1, col2, col3 = st.columns([1, 4, 2])
    
    with col1:
        st.image("logo.jpg", width=100)
    
    with col2:
        st.markdown("<h1 style='padding-top: 10px;'>📈 ETF Performance Tracker</h1>", unsafe_allow_html=True)
    
    with col3:
        if "user" in st.session_state:
            st.markdown(f"<p style='text-align:right; padding-top: 25px;'>👤 {st.session_state.user}</p>", 
                       unsafe_allow_html=True)
            if st.button("Logout", key="logout_btn"):
                st.session_state.clear()
                st.rerun()
        else:
            username = st.text_input("Enter your name:", key="login_input")
            if st.button("Login", key="login_btn"):
                if username:
                    st.session_state.user = username
                    st.rerun()
                else:
                    st.warning("Please enter a name")
                st.stop()

def show_footer():
    """Consistent footer with the other pages"""
    st.markdown("---")
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1b/Angel_One_Logo.svg", width=100)
    st.markdown("""
    <div style='text-align: center; font-size: 16px; padding-top: 20px;'>
        <strong>📊 FinSmart Wealth Advisory</strong><br>
        Partha Chakraborty<br><br>
        <a href="tel:+91XXXXXXXXXX">📞 Call</a> | 
        <a href="https://wa.me/91XXXXXXXXXX">💬 WhatsApp</a> | 
        <a href="https://angel-one.onelink.me/Wjgr/m8njiek1">📂 Open DMAT</a>
    </div>
    """, unsafe_allow_html=True)

def main():
    show_header()
    
    # Market status
    if is_market_open():
        st.success("✅ Market is OPEN - showing live data")
    else:
        st.warning("⚠️ Market is CLOSED - showing last available data")
    
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    if st.button("🔄 Refresh Data"):
        get_cached_etf_data.cache_clear()
        st.rerun()
    
    # Load ETF data
    with st.spinner("Loading ETF performance data..."):
        progress_bar = st.progress(0)
        etf_data = []
        
        for i, (name, symbol) in enumerate(INDIAN_ETFS.items()):
            etf_perf = get_etf_performance(symbol, name)
            if etf_perf:
                etf_data.append(etf_perf)
            progress_bar.progress((i + 1) / len(INDIAN_ETFS))
            time.sleep(0.1)  # Rate limiting
        
        df = pd.DataFrame(etf_data)
    
    if df.empty:
        st.error("No ETF data available. Please try again later.")
        show_footer()
        return
    
    # Main display
    st.subheader("📊 ETF Performance Overview")
    
    # Time period selector
    time_period = st.selectbox(
        "View performance for:",
        ["1 Day", "1 Week", "1 Month", "1 Year", "Max"],
        index=0
    )
    
    # Sort by selected time period
    sort_column = {
        "1 Day": "1D Change (%)",
        "1 Week": "1W Change (%)",
        "1 Month": "1M Change (%)",
        "1 Year": "1Y Change (%)",
        "Max": "Max Change (%)"
    }[time_period]
    
    sorted_df = df.sort_values(by=sort_column, ascending=False)
    
    # Display ETF performance
    st.dataframe(
        sorted_df.style.format({
            'Current Price': '₹{:.2f}',
            '1D Change (%)': '{:+.2f}%',
            '1W Change (%)': '{:+.2f}%',
            '1M Change (%)': '{:+.2f}%',
            '1Y Change (%)': '{:+.2f}%',
            'Max Change (%)': '{:+.2f}%'
        }).applymap(color_change, subset=[
            '1D Change (%)', '1W Change (%)', 
            '1M Change (%)', '1Y Change (%)', 
            'Max Change (%)'
        ]),
        height=800,
        use_container_width=True,
        column_config={
            "ETF Name": "ETF Name",
            "Symbol": "Symbol",
            "Current Price": st.column_config.NumberColumn("Current Price", format="₹%.2f"),
            "1D Change (%)": "1 Day",
            "1W Change (%)": "1 Week",
            "1M Change (%)": "1 Month",
            "1Y Change (%)": "1 Year",
            "Max Change (%)": "Since Inception",
            "As of Date": "Last Updated"
        }
    )
    
    # Top performers section
    st.subheader("🏆 Top Performers")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🟢 Top 5 Gainers")
        top_gainers = sorted_df.nlargest(5, sort_column)
        st.dataframe(
            top_gainers.style.format({
                'Current Price': '₹{:.2f}',
                sort_column: '{:+.2f}%'
            }).applymap(color_change, subset=[sort_column]),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown("### 🔴 Top 5 Losers")
        top_losers = sorted_df.nsmallest(5, sort_column)
        st.dataframe(
            top_losers.style.format({
                'Current Price': '₹{:.2f}',
                sort_column: '{:+.2f}%'
            }).applymap(color_change, subset=[sort_column]),
            use_container_width=True,
            hide_index=True
        )
    
    show_footer()

if __name__ == "__main__":
    main()