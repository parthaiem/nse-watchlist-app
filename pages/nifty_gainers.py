import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from supabase_helper import get_watchlist

# Initialize session states
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Common header function
def show_header():
    top_col1, top_col2, top_col3 = st.columns([1, 4, 2])
    with top_col1:
        st.image("logo.jpg", width=100)
    with top_col2:
        st.markdown("<h1 style='padding-top: 10px;'>📊 Indian Market Movers</h1>", unsafe_allow_html=True)
    with top_col3:
        if "user" in st.session_state:
            st.markdown(f"<p style='text-align:right; padding-top: 25px;'>👤 Logged in as <strong>{st.session_state.user}</strong></p>", 
                       unsafe_allow_html=True)
            if st.button("Logout", key="logout_btn"):
                st.session_state.clear()
                st.rerun()
        else:
            username = st.text_input("Enter your name to continue:", key="login_input")
            if st.button("Login", key="login_btn"):
                if username:
                    st.session_state.user = username
                    st.session_state.watchlist = get_watchlist(username)
                    st.rerun()
                else:
                    st.warning("Please enter a name to login.")
            st.stop()

# Common footer function
def show_footer():
    st.markdown("---")
    st.image("https://upload.wikimedia.org/wikipedia/commons/1/1b/Angel_One_Logo.svg", width=100)
    st.markdown(f"""
        <div style='text-align: center; font-size: 16px; padding-top: 20px;'>
            <strong>📊 FinSmart Wealth Advisory</strong><br>
            Partha Chakraborty<br><br>
            <a href="tel:+91XXXXXXXXXX">📞 Call</a> &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="https://wa.me/91XXXXXXXXXX">💬 WhatsApp</a> &nbsp;&nbsp;|&nbsp;&nbsp;
            <a href="https://angel-one.onelink.me/Wjgr/m8njiek1">📂 Open DMAT</a>
        </div>
    """, unsafe_allow_html=True)

def color_change(val):
    if isinstance(val, (int, float)):
        color = 'green' if val >= 0 else 'red'
        return f'color: {color}; font-weight: bold;'
    return ''

def get_historical_data(symbol, periods):
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=periods)
        if not hist.empty:
            return hist
    except:
        return None
    return None

def get_stock_data(stock_list):
    data = []
    today = datetime.today()
    
    for name, symbol in stock_list.items():
        try:
            # Get daily data
            daily_data = yf.Ticker(symbol).history(period="1d")
            if daily_data.empty:
                continue
            
            # Get historical data
            hist_1m = get_historical_data(symbol, "1mo")
            hist_3m = get_historical_data(symbol, "3mo")
            hist_1y = get_historical_data(symbol, "1y")
            
            current_price = daily_data['Close'][-1]
            prev_close = daily_data['Open'][0] if 'Open' in daily_data.columns else daily_data['Close'][0]
            
            # Calculate daily change
            day_change = ((current_price - prev_close) / prev_close) * 100 if prev_close != 0 else 0
            
            # Calculate 1-month change
            if hist_1m is not None and not hist_1m.empty:
                month_ago_price = hist_1m['Close'][0]
                month_change = ((current_price - month_ago_price) / month_ago_price) * 100 if month_ago_price != 0 else 0
            else:
                month_change = 0
                
            # Calculate 3-month change
            if hist_3m is not None and not hist_3m.empty:
                three_month_ago_price = hist_3m['Close'][0]
                three_month_change = ((current_price - three_month_ago_price) / three_month_ago_price) * 100 if three_month_ago_price != 0 else 0
            else:
                three_month_change = 0
                
            # Calculate 52-week high/low
            if hist_1y is not None and not hist_1y.empty:
                week52_high = hist_1y['High'].max()
                week52_low = hist_1y['Low'].min()
            else:
                week52_high = current_price
                week52_low = current_price
            
            data.append({
                'Symbol': name,
                'LTP': current_price,
                'Change (%)': day_change,
                '1M Change (%)': month_change,
                '3M Change (%)': three_month_change,
                '52W High': week52_high,
                '52W Low': week52_low
            })
        except Exception as e:
            st.warning(f"Could not load {name}: {str(e)}")
            continue
    return pd.DataFrame(data)

def display_gainers_losers(df, title, num=5):
    if df.empty:
        st.warning(f"No data available for {title}")
        return
    
    # Ensure we have enough stocks to show gainers and losers
    if len(df) < num*2:
        num = min(3, len(df)//2)
        if num == 0:
            st.warning(f"Not enough data to show gainers/losers for {title}")
            return
    
    # Get distinct top gainers and losers
    gainers = df.nlargest(num, 'Change (%)').drop_duplicates(subset=['Symbol'])
    losers = df.nsmallest(num, 'Change (%)').drop_duplicates(subset=['Symbol'])
    
    # Remove any stock that appears in both gainers and losers
    common = set(gainers['Symbol']).intersection(set(losers['Symbol']))
    gainers = gainers[~gainers['Symbol'].isin(common)]
    losers = losers[~losers['Symbol'].isin(common)]
    
    # If we lost some stocks due to overlap, fill up again
    if len(gainers) < num:
        additional = df[~df['Symbol'].isin(gainers['Symbol']) & ~df['Symbol'].isin(losers['Symbol'])]
        additional = additional.nlargest(num - len(gainers), 'Change (%)')
        gainers = pd.concat([gainers, additional])
    
    if len(losers) < num:
        additional = df[~df['Symbol'].isin(gainers['Symbol']) & ~df['Symbol'].isin(losers['Symbol'])]
        additional = additional.nsmallest(num - len(losers), 'Change (%)')
        losers = pd.concat([losers, additional])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🏆 {title} Top Gainers")
        st.dataframe(
            gainers.style.format({
                'LTP': '₹{:.2f}',
                'Change (%)': '{:+.2f}%',
                '1M Change (%)': '{:+.2f}%',
                '3M Change (%)': '{:+.2f}%',
                '52W High': '₹{:.2f}',
                '52W Low': '₹{:.2f}'
            }).applymap(color_change, subset=['Change (%)', '1M Change (%)', '3M Change (%)']),
            use_container_width=True,
            hide_index=True,
            height=min(400, 75 + num * 45)
        )
    
    with col2:
        st.subheader(f"📉 {title} Top Losers")
        st.dataframe(
            losers.style.format({
                'LTP': '₹{:.2f}',
                'Change (%)': '{:+.2f}%',
                '1M Change (%)': '{:+.2f}%',
                '3M Change (%)': '{:+.2f}%',
                '52W High': '₹{:.2f}',
                '52W Low': '₹{:.2f}'
            }).applymap(color_change, subset=['Change (%)', '1M Change (%)', '3M Change (%)']),
            use_container_width=True,
            hide_index=True,
            height=min(400, 75 + num * 45)
        )

def main():
    st.set_page_config(page_title="Indian Market Movers", layout="wide")
    show_header()
    
    st.markdown(f"<div style='text-align: right;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    
    if st.button("🔄 Refresh Data", key="refresh_btn"):
        st.rerun()
    
    # Define stock lists with more stocks to ensure enough data
    nifty50_stocks = {
        'RELIANCE': 'RELIANCE.NS',
        'TCS': 'TCS.NS',
        'HDFCBANK': 'HDFCBANK.NS',
        'ICICIBANK': 'ICICIBANK.NS',
        'HINDUNILVR': 'HINDUNILVR.NS',
        'INFY': 'INFY.NS',
        'ITC': 'ITC.NS',
        'SBIN': 'SBIN.NS',
        'BHARTIARTL': 'BHARTIARTL.NS',
        'LT': 'LT.NS',
        'KOTAKBANK': 'KOTAKBANK.NS',
        'HCLTECH': 'HCLTECH.NS',
        'BAJFINANCE': 'BAJFINANCE.NS',
        'ASIANPAINT': 'ASIANPAINT.NS',
        'MARUTI': 'MARUTI.NS',
        'TITAN': 'TITAN.NS',
        'NESTLEIND': 'NESTLEIND.NS',
        'BRITANNIA': 'BRITANNIA.NS',
        'HDFCLIFE': 'HDFCLIFE.NS',
        'ONGC': 'ONGC.NS',
        'TATASTEEL': 'TATASTEEL.NS'
    }
    
    nifty_next50_stocks = {
        'PEL': 'PEL.NS',
        'ADANIENT': 'ADANIENT.NS',
        'ADANIPORTS': 'ADANIPORTS.NS',
        'DIVISLAB': 'DIVISLAB.NS',
        'DRREDDY': 'DRREDDY.NS',
        'GRASIM': 'GRASIM.NS',
        'JSWSTEEL': 'JSWSTEEL.NS',
        'EICHERMOT': 'EICHERMOT.NS',
        'ULTRACEMCO': 'ULTRACEMCO.NS',
        'BAJAJFINSV': 'BAJAJFINSV.NS',
        'INDUSINDBK': 'INDUSINDBK.NS',
        'PIDILITIND': 'PIDILITIND.NS',
        'SIEMENS': 'SIEMENS.NS',
        'HAVELLS': 'HAVELLS.NS',
        'GODREJCP': 'GODREJCP.NS',
        'AMBUJACEM': 'AMBUJACEM.NS',
        'MOTHERSON': 'MOTHERSON.NS',
        'AUROPHARMA': 'AUROPHARMA.NS',
        'DABUR': 'DABUR.NS',
        'BAJAJHLDNG': 'BAJAJHLDNG.NS'
    }
    
    small_cap_stocks = {
        'IRB': 'IRB.NS',
        'JBCHEPHARM': 'JBCHEPHARM.NS',
        'RBLBANK': 'RBLBANK.NS',
        'CANFINHOME': 'CANFINHOME.NS',
        'FEDERALBNK': 'FEDERALBNK.NS',
        'JKCEMENT': 'JKCEMENT.NS',
        'MANAPPURAM': 'MANAPPURAM.NS',
        'MFSL': 'MFSL.NS',
        'SUNDRMFAST': 'SUNDRMFAST.NS',
        'TV18BRDCST': 'TV18BRDCST.NS',
        'IBULHSGFIN': 'IBULHSGFIN.NS',
        'JINDALSTEL': 'JINDALSTEL.NS',
        'NCC': 'NCC.NS',
        'PFC': 'PFC.NS',
        'RECLTD': 'RECLTD.NS',
        'SAIL': 'SAIL.NS',
        'SRF': 'SRF.NS',
        'TATACOMM': 'TATACOMM.NS',
        'UNIONBANK': 'UNIONBANK.NS',
        'VOLTAS': 'VOLTAS.NS'
    }
    
    # Nifty 50 Section
    st.markdown("## 🇮🇳 NIFTY 50")
    with st.spinner("Loading Nifty 50 data..."):
        nifty50_data = get_stock_data(nifty50_stocks)
        display_gainers_losers(nifty50_data, "Nifty 50", num=5)
    
    st.markdown("---")
    
    # Nifty Next 50 Section
    st.markdown("## 🇮🇳 NIFTY NEXT 50")
    with st.spinner("Loading Nifty Next 50 data..."):
        nifty_next50_data = get_stock_data(nifty_next50_stocks)
        display_gainers_losers(nifty_next50_data, "Nifty Next 50", num=5)
    
    st.markdown("---")
    
    # Small Cap Section
    st.markdown("## 📊 Small Cap Stocks")
    with st.spinner("Loading Small Cap data..."):
        small_cap_data = get_stock_data(small_cap_stocks)
        display_gainers_losers(small_cap_data, "Small Cap", num=5)
    
    show_footer()

if __name__ == "__main__":
    main()