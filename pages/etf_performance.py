import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from functools import lru_cache
import time

# Configuration
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST

# Comprehensive list of Indian ETFs with categories
INDIAN_ETFS = {
    # Index ETFs
    'NIFTY 50 ETF': {'symbol': 'NIFTYBEES.NS', 'category': 'Index', 'aum': 9500},
    'SENSEX ETF': {'symbol': 'SETFNN50.NS', 'category': 'Index', 'aum': 3200},
    'NIFTY NEXT 50 ETF': {'symbol': 'JUNIORBEES.NS', 'category': 'Index', 'aum': 2800},
    'NIFTY 100 ETF': {'symbol': 'ICICINIFTY.NS', 'category': 'Index', 'aum': 4200},
    'NIFTY MIDCAP 150 ETF': {'symbol': 'M150.NS', 'category': 'Index', 'aum': 1800},
    
    # Sector ETFs
    'BANK ETF': {'symbol': 'BANKBEES.NS', 'category': 'Sector', 'aum': 5300},
    'IT ETF': {'symbol': 'ITBEES.NS', 'category': 'Sector', 'aum': 2100},
    'PSU BANK ETF': {'symbol': 'PSUBANKBEES.NS', 'category': 'Sector', 'aum': 1500},
    'CONSUMPTION ETF': {'symbol': 'CONSUMBEES.NS', 'category': 'Sector', 'aum': 1200},
    'INFRA ETF': {'symbol': 'INFRABEES.NS', 'category': 'Sector', 'aum': 900},
    
    # Commodity ETFs
    'GOLD ETF': {'symbol': 'GOLDBEES.NS', 'category': 'Commodity', 'aum': 12500},
    'SILVER ETF': {'symbol': 'SILVERBEES.NS', 'category': 'Commodity', 'aum': 3800},
    
    # Factor & Smart Beta ETFs
    'LOW VOLATILITY ETF': {'symbol': 'MINVOLTILE.NS', 'category': 'Factor', 'aum': 800},
    'QUALITY ETF': {'symbol': 'QUALITYBEES.NS', 'category': 'Factor', 'aum': 1100},
    'VALUE ETF': {'symbol': 'VALUEBEES.NS', 'category': 'Factor', 'aum': 700},
    'MOMENTUM ETF': {'symbol': 'MOM100BEES.NS', 'category': 'Factor', 'aum': 950},
    
    # Thematic ETFs
    'BHARAT 22 ETF': {'symbol': 'BHARAT22ETF.NS', 'category': 'Thematic', 'aum': 6500},
    'CPSE ETF': {'symbol': 'CPSEETF.NS', 'category': 'Thematic', 'aum': 5800},
    'MIRAE EMERGING BLUECHIP ETF': {'symbol': 'MIRAEEMG.NS', 'category': 'Thematic', 'aum': 3200},
    
    # Fixed Income ETFs
    'LIQUID ETF': {'symbol': 'LIQUIDBEES.NS', 'category': 'Fixed Income', 'aum': 2800},
    'GILT ETF': {'symbol': 'GILTBEES.NS', 'category': 'Fixed Income', 'aum': 1500},
    
    # International ETFs
    'NASDAQ 100 ETF': {'symbol': 'M100.NS', 'category': 'International', 'aum': 2500},
    'HANG SENG ETF': {'symbol': 'HSETF.NS', 'category': 'International', 'aum': 800}
}

@lru_cache(maxsize=256)
def get_cached_etf_data(symbol, period):
    """Get cached ETF data with error handling"""
    try:
        data = yf.Ticker(symbol).history(period=period)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def is_market_open():
    """Check if market is currently open"""
    now = datetime.now()
    market_open = datetime(now.year, now.month, now.day, *MARKET_OPEN_TIME)
    market_close = datetime(now.year, now.month, now.day, *MARKET_CLOSE_TIME)
    return market_open <= now <= market_close

def calculate_performance(current_price, historical_data):
    """Calculate performance metrics"""
    if historical_data is None or len(historical_data) < 2:
        return None
    old_price = historical_data['Close'][0]
    return ((current_price - old_price) / old_price) * 100 if old_price != 0 else None

def get_etf_performance(etf_info):
    """Get comprehensive performance data for an ETF"""
    try:
        symbol = etf_info['symbol']
        name = etf_info['name']
        
        # Get data for different time periods
        hist_1d = get_cached_etf_data(symbol, "1d")
        if hist_1d is None:
            return None
            
        current_price = hist_1d['Close'][-1]
        prev_close = hist_1d['Open'][0] if 'Open' in hist_1d.columns else hist_1d['Close'][0]
        day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
        
        # Calculate performance for different periods
        week_change = calculate_performance(current_price, get_cached_etf_data(symbol, "1wk"))
        month_change = calculate_performance(current_price, get_cached_etf_data(symbol, "1mo"))
        quarter_change = calculate_performance(current_price, get_cached_etf_data(symbol, "3mo"))
        year_change = calculate_performance(current_price, get_cached_etf_data(symbol, "1y"))
        max_change = calculate_performance(current_price, get_cached_etf_data(symbol, "max"))
        
        # Volume and turnover
        volume = hist_1d['Volume'][-1] if 'Volume' in hist_1d.columns else 0
        
        return {
            'ETF Name': name,
            'Symbol': symbol,
            'Category': etf_info['category'],
            'AUM (Cr)': etf_info['aum'],
            'Current Price': current_price,
            'Volume': volume,
            '1D Change (%)': day_change,
            '1W Change (%)': week_change,
            '1M Change (%)': month_change,
            '3M Change (%)': quarter_change,
            '1Y Change (%)': year_change,
            'Max Change (%)': max_change,
            'Last Updated': hist_1d.index[-1].strftime('%Y-%m-%d %H:%M')
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

def format_volume(volume):
    """Format volume for display"""
    if volume >= 1e7:
        return f"{volume/1e7:.1f} Cr"
    elif volume >= 1e5:
        return f"{volume/1e5:.1f} L"
    return f"{volume:,.0f}"

def show_header():
    """Consistent header with the other pages"""
    st.set_page_config(page_title="ETF Performance Dashboard", layout="wide")
    
    col1, col2, col3 = st.columns([1, 4, 2])
    with col1:
        st.image("logo.jpg", width=100)
    with col2:
        st.markdown("<h1 style='padding-top: 10px;'>📊 Comprehensive ETF Tracker</h1>", unsafe_allow_html=True)
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

def display_top_performers(df, period):
    """Display top performing ETFs for a given period"""
    col1, col2 = st.columns(2)
    sort_column = f"{period} Change (%)"
    
    with col1:
        st.markdown(f"### 🏆 Top 5 {period} Performers")
        top_gainers = df.nlargest(5, sort_column)[['ETF Name', 'Current Price', sort_column]]
        st.dataframe(
            top_gainers.style.format({
                'Current Price': '₹{:.2f}',
                sort_column: '{:+.2f}%'
            }).applymap(color_change, subset=[sort_column]),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown(f"### 📉 Worst 5 {period} Performers")
        top_losers = df.nsmallest(5, sort_column)[['ETF Name', 'Current Price', sort_column]]
        st.dataframe(
            top_losers.style.format({
                'Current Price': '₹{:.2f}',
                sort_column: '{:+.2f}%'
            }).applymap(color_change, subset=[sort_column]),
            use_container_width=True,
            hide_index=True
        )

def main():
    show_header()
    
    # Market status
    market_status = "✅ LIVE (Market Open)" if is_market_open() else "⚠️ LAST TRADED (Market Closed)"
    st.markdown(f"### {market_status} • {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if st.button("🔄 Refresh All Data"):
        get_cached_etf_data.cache_clear()
        st.rerun()
    
    # Load ETF data
    with st.spinner("Loading comprehensive ETF data..."):
        progress_bar = st.progress(0)
        etf_data = []
        
        # Prepare ETF data with names
        etf_list = [{'name': name, **info} for name, info in INDIAN_ETFS.items()]
        
        for i, etf in enumerate(etf_list):
            etf_perf = get_etf_performance(etf)
            if etf_perf:
                etf_data.append(etf_perf)
            progress_bar.progress((i + 1) / len(etf_list))
            time.sleep(0.1)
        
        df = pd.DataFrame(etf_data)
    
    if df.empty:
        st.error("No ETF data available. Please check your connection and try again.")
        show_footer()
        return
    
    # Category filter
    categories = sorted(df['Category'].unique())
    selected_categories = st.multiselect(
        "Filter by Category:", 
        categories, 
        default=categories
    )
    
    filtered_df = df[df['Category'].isin(selected_categories)]
    
    # Time period selector
    time_period = st.selectbox(
        "View performance for:", 
        ["1D", "1W", "1M", "3M", "1Y", "Max"], 
        index=2
    )
    
    # Sort by selected time period
    sort_column = f"{time_period} Change (%)"
    sorted_df = filtered_df.sort_values(by=sort_column, ascending=False)
    
    # Top performers section
    st.markdown("---")
    st.subheader("🌟 Top Performing ETFs")
    
    tab1, tab2, tab3 = st.tabs(["1 Month Performers", "1 Year Performers", "All Time Performers"])
    
    with tab1:
        display_top_performers(filtered_df, "1M")
    with tab2:
        display_top_performers(filtered_df, "1Y")
    with tab3:
        display_top_performers(filtered_df, "Max")
    
    # Main ETF data table
    st.markdown("---")
    st.subheader("📋 Complete ETF Performance Data")
    
    # Format volume before display
    display_df = sorted_df.copy()
    display_df['Volume'] = display_df['Volume'].apply(format_volume)
    
    st.dataframe(
        display_df.style.format({
            'Current Price': '₹{:.2f}',
            'AUM (Cr)': '₹{:.0f} Cr',
            '1D Change (%)': '{:+.2f}%',
            '1W Change (%)': '{:+.2f}%',
            '1M Change (%)': '{:+.2f}%',
            '3M Change (%)': '{:+.2f}%',
            '1Y Change (%)': '{:+.2f}%',
            'Max Change (%)': '{:+.2f}%'
        }).applymap(color_change, subset=[
            '1D Change (%)', '1W Change (%)', '1M Change (%)',
            '3M Change (%)', '1Y Change (%)', 'Max Change (%)'
        ]),
        height=800,
        use_container_width=True,
        column_config={
            "ETF Name": st.column_config.TextColumn("ETF Name", width="medium"),
            "Symbol": "Symbol",
            "Category": "Category",
            "AUM (Cr)": st.column_config.NumberColumn("AUM", format="₹%.0f Cr"),
            "Current Price": st.column_config.NumberColumn("Price", format="₹%.2f"),
            "Volume": "Volume",
            "1D Change (%)": "1D",
            "1W Change (%)": "1W",
            "1M Change (%)": "1M",
            "3M Change (%)": "3M",
            "1Y Change (%)": "1Y",
            "Max Change (%)": "Max",
            "Last Updated": "Updated"
        }
    )
    
    show_footer()

if __name__ == "__main__":
    main()