import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
from functools import lru_cache
import time
import schedule
import threading

# Configuration
MARKET_OPEN_TIME = (9, 15)  # 9:15 AM IST
MARKET_CLOSE_TIME = (15, 30)  # 3:30 PM IST
REFRESH_INTERVAL = 15  # minutes

# Expanded list of Indian ETFs with complete details
INDIAN_ETFS = {
    # Large Cap Index ETFs
    'NIFTY 50 ETF': {'symbol': 'NIFTYBEES.NS', 'category': 'Index', 'aum': 9500, 'expense': 0.05},
    'SENSEX ETF': {'symbol': 'SETFNN50.NS', 'category': 'Index', 'aum': 3200, 'expense': 0.07},
    'NIFTY 100 ETF': {'symbol': 'ICICINIFTY.NS', 'category': 'Index', 'aum': 4200, 'expense': 0.20},
    
    # Mid/Small Cap ETFs
    'NIFTY NEXT 50 ETF': {'symbol': 'JUNIORBEES.NS', 'category': 'Index', 'aum': 2800, 'expense': 0.15},
    'NIFTY MIDCAP 150 ETF': {'symbol': 'M150.NS', 'category': 'Index', 'aum': 1800, 'expense': 0.30},
    'SMALL CAP ETF': {'symbol': 'SMALLETF.NS', 'category': 'Index', 'aum': 1200, 'expense': 0.35},
    
    # Sector ETFs
    'BANK ETF': {'symbol': 'BANKBEES.NS', 'category': 'Sector', 'aum': 5300, 'expense': 0.25},
    'IT ETF': {'symbol': 'ITBEES.NS', 'category': 'Sector', 'aum': 2100, 'expense': 0.25},
    'PHARMA ETF': {'symbol': 'PHARMAETF.NS', 'category': 'Sector', 'aum': 1500, 'expense': 0.30},
    'AUTOMOBILE ETF': {'symbol': 'AUTOETF.NS', 'category': 'Sector', 'aum': 900, 'expense': 0.30},
    
    # Commodity ETFs
    'GOLD ETF': {'symbol': 'GOLDBEES.NS', 'category': 'Commodity', 'aum': 12500, 'expense': 0.15},
    'SILVER ETF': {'symbol': 'SILVERBEES.NS', 'category': 'Commodity', 'aum': 3800, 'expense': 0.25},
    
    # Factor & Smart Beta ETFs
    'LOW VOLATILITY ETF': {'symbol': 'MINVOLTILE.NS', 'category': 'Factor', 'aum': 800, 'expense': 0.35},
    'QUALITY ETF': {'symbol': 'QUALITYBEES.NS', 'category': 'Factor', 'aum': 1100, 'expense': 0.30},
    'MOMENTUM ETF': {'symbol': 'MOM100BEES.NS', 'category': 'Factor', 'aum': 950, 'expense': 0.35},
    
    # Thematic ETFs
    'BHARAT 22 ETF': {'symbol': 'BHARAT22ETF.NS', 'category': 'Thematic', 'aum': 6500, 'expense': 0.10},
    'CPSE ETF': {'symbol': 'CPSEETF.NS', 'category': 'Thematic', 'aum': 5800, 'expense': 0.07},
    'CONSUMPTION ETF': {'symbol': 'CONSUMBEES.NS', 'category': 'Thematic', 'aum': 1200, 'expense': 0.25},
    
    # Fixed Income ETFs
    'LIQUID ETF': {'symbol': 'LIQUIDBEES.NS', 'category': 'Fixed Income', 'aum': 2800, 'expense': 0.08},
    'GILT ETF': {'symbol': 'GILTBEES.NS', 'category': 'Fixed Income', 'aum': 1500, 'expense': 0.10},
    
    # International ETFs
    'NASDAQ 100 ETF': {'symbol': 'M100.NS', 'category': 'International', 'aum': 2500, 'expense': 0.30},
    'HANG SENG ETF': {'symbol': 'HSETF.NS', 'category': 'International', 'aum': 800, 'expense': 0.35},
    'S&P 500 ETF': {'symbol': 'SP500ETF.NS', 'category': 'International', 'aum': 1200, 'expense': 0.30}
}

# Scheduled data refresh
def schedule_refresh():
    while True:
        schedule.run_pending()
        time.sleep(60)

@lru_cache(maxsize=512)
def get_cached_etf_data(symbol, period):
    """Get cached ETF data with error handling"""
    try:
        data = yf.Ticker(symbol).history(period=period)
        return data if not data.empty else None
    except Exception as e:
        st.error(f"Error fetching {symbol}: {str(e)}")
        return None

def refresh_data():
    """Clear cache to force data refresh"""
    get_cached_etf_data.cache_clear()
    st.rerun()

# Initialize scheduled refresh
schedule.every(REFRESH_INTERVAL).minutes.do(refresh_data)
threading.Thread(target=schedule_refresh, daemon=True).start()

def is_market_open():
    """Check if market is currently open"""
    now = datetime.now()
    market_open = datetime(now.year, now.month, now.day, *MARKET_OPEN_TIME)
    market_close = datetime(now.year, now.month, now.day, *MARKET_CLOSE_TIME)
    return market_open <= now <= market_close

def get_historical_chart(symbol, name):
    """Get historical performance chart for an ETF"""
    try:
        hist = get_cached_etf_data(symbol, "1y")
        if hist is None:
            return None
            
        fig = px.line(hist, x=hist.index, y='Close', 
                     title=f"{name} ({symbol}) - 1 Year Performance",
                     labels={'Close': 'Price (₹)', 'Date': 'Date'})
        fig.update_layout(
            hovermode="x unified",
            showlegend=False,
            margin=dict(l=20, r=20, t=40, b=20)
        return fig
    except Exception as e:
        st.error(f"Error generating chart for {name}: {str(e)}")
        return None

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
        def calculate_change(period):
            hist = get_cached_etf_data(symbol, period)
            if hist is None or len(hist) < 2:
                return None
            old_price = hist['Close'][0]
            return ((current_price - old_price) / old_price) * 100 if old_price != 0 else None
        
        week_change = calculate_change("1wk")
        month_change = calculate_change("1mo")
        quarter_change = calculate_change("3mo")
        year_change = calculate_change("1y")
        max_change = calculate_change("max")
        
        # Volume and turnover
        volume = hist_1d['Volume'][-1] if 'Volume' in hist_1d.columns else 0
        
        return {
            'ETF Name': name,
            'Symbol': symbol,
            'Category': etf_info['category'],
            'AUM (Cr)': etf_info['aum'],
            'Expense Ratio (%)': etf_info['expense'],
            'Current Price': current_price,
            'Volume': volume,
            '1D Change (%)': day_change,
            '1W Change (%)': week_change,
            '1M Change (%)': month_change,
            '3M Change (%)': quarter_change,
            '1Y Change (%)': year_change,
            'Max Change (%)': max_change,
            'Last Updated': hist_1d.index[-1].strftime('%Y-%m-%d %H:%M'),
            'Chart': get_historical_chart(symbol, name)
        }
    except Exception as e:
        st.error(f"Error processing {name}: {str(e)}")
        return None

def show_header():
    """Consistent header with the other pages"""
    st.set_page_config(page_title="Advanced ETF Dashboard", layout="wide")
    
    col1, col2, col3 = st.columns([1, 4, 2])
    with col1:
        st.image("logo.jpg", width=100)
    with col2:
        st.markdown("<h1 style='padding-top: 10px;'>📈 Advanced ETF Performance Dashboard</h1>", unsafe_allow_html=True)
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

def format_volume(volume):
    """Format volume for display"""
    if volume >= 1e7:
        return f"{volume/1e7:.1f} Cr"
    elif volume >= 1e5:
        return f"{volume/1e5:.1f} L"
    return f"{volume:,.0f}"

def display_top_performers(df, period):
    """Display top performing ETFs for a given period"""
    col1, col2 = st.columns(2)
    sort_column = f"{period} Change (%)"
    
    with col1:
        st.markdown(f"### 🏆 Top 5 {period} Performers")
        top_gainers = df.nlargest(5, sort_column)[['ETF Name', 'Current Price', sort_column, 'Expense Ratio (%)']]
        st.dataframe(
            top_gainers.style.format({
                'Current Price': '₹{:.2f}',
                sort_column: '{:+.2f}%',
                'Expense Ratio (%)': '{:.2f}%'
            }),
            use_container_width=True,
            hide_index=True
        )
    
    with col2:
        st.markdown(f"### 📉 Worst 5 {period} Performers")
        top_losers = df.nsmallest(5, sort_column)[['ETF Name', 'Current Price', sort_column, 'Expense Ratio (%)']]
        st.dataframe(
            top_losers.style.format({
                'Current Price': '₹{:.2f}',
                sort_column: '{:+.2f}%',
                'Expense Ratio (%)': '{:.2f}%'
            }),
            use_container_width=True,
            hide_index=True
        )

def main():
    show_header()
    
    # Market status and refresh info
    market_status = "✅ LIVE (Market Open)" if is_market_open() else "⚠️ LAST TRADED (Market Closed)"
    last_refresh = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    next_refresh = (datetime.now() + timedelta(minutes=REFRESH_INTERVAL)).strftime('%H:%M')
    
    st.markdown(f"""
    ### {market_status} • Last Refresh: {last_refresh} • Next Refresh: {next_refresh}
    """)
    
    if st.button("🔄 Manual Refresh Now"):
        refresh_data()
    
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
    
    tab1, tab2, tab3, tab4 = st.tabs(["1 Month", "3 Months", "1 Year", "All Time"])
    
    with tab1:
        display_top_performers(filtered_df, "1M")
    with tab2:
        display_top_performers(filtered_df, "3M")
    with tab3:
        display_top_performers(filtered_df, "1Y")
    with tab4:
        display_top_performers(filtered_df, "Max")
    
    # ETF Performance Charts
    st.markdown("---")
    st.subheader("📈 ETF Performance Charts")
    
    selected_etf = st.selectbox(
        "Select ETF to view historical performance:",
        sorted_df['ETF Name']
    )
    
    selected_data = sorted_df[sorted_df['ETF Name'] == selected_etf].iloc[0]
    if selected_data['Chart'] is not None:
        st.plotly_chart(selected_data['Chart'], use_container_width=True)
    else:
        st.warning(f"No historical data available for {selected_etf}")
    
    # Main ETF data table
    st.markdown("---")
    st.subheader("📋 Complete ETF Performance Data")
    
    # Format volume before display
    display_df = sorted_df.copy()
    display_df['Volume'] = display_df['Volume'].apply(format_volume)
    
    st.dataframe(
        display_df.drop(columns=['Chart']).style.format({
            'Current Price': '₹{:.2f}',
            'AUM (Cr)': '₹{:.0f} Cr',
            'Expense Ratio (%)': '{:.2f}%',
            '1D Change (%)': '{:+.2f}%',
            '1W Change (%)': '{:+.2f}%',
            '1M Change (%)': '{:+.2f}%',
            '3M Change (%)': '{:+.2f}%',
            '1Y Change (%)': '{:+.2f}%',
            'Max Change (%)': '{:+.2f}%'
        }),
        height=800,
        use_container_width=True,
        column_config={
            "ETF Name": st.column_config.TextColumn("ETF Name", width="medium"),
            "Symbol": "Symbol",
            "Category": "Category",
            "AUM (Cr)": st.column_config.NumberColumn("AUM", format="₹%.0f Cr"),
            "Expense Ratio (%)": st.column_config.NumberColumn("Expense", format="%.2f%"),
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