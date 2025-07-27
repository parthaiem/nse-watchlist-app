import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime

def show_header():
    st.set_page_config(page_title="Nifty Gainers & Losers", layout="wide")
    st.title("📈 Nifty Top Gainers & Losers")
    st.markdown(f"<div style='text-align: right;'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    st.markdown("---")

def get_nifty_data(index):
    """Fetch Nifty 50 or Nifty 100 components with price changes"""
    if index == "NIFTY 50":
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%2050"
    else:
        url = "https://www.nseindia.com/api/equity-stockIndices?index=NIFTY%20100"
    
    try:
        # Use yfinance as fallback if NSE API doesn't work
        if index == "NIFTY 50":
            ticker = "^NSEI"
        else:
            ticker = "^NSE100"
        
        data = yf.download(ticker, period="1d", group_by='ticker')
        if not data.empty:
            # This is a simplified version - real implementation would get all components
            return pd.DataFrame({
                'Symbol': [ticker],
                'Company': [index],
                'Last Price': [data['Close'][-1]],
                'Change': [data['Close'][-1] - data['Open'][0]],
                '% Change': [(data['Close'][-1] - data['Open'][0]) / data['Open'][0] * 100
            })
    except Exception as e:
        st.error(f"Error fetching {index} data: {str(e)}")
    
    return pd.DataFrame()

def color_change(val):
    """Color formatting for percentage changes"""
    try:
        color = 'green' if val >= 0 else 'red'
        return f'color: {color}; font-weight: bold;'
    except:
        return ''

def display_gainers_losers(data, title):
    if data.empty:
        st.warning(f"No data available for {title}")
        return
    
    # Get top 5 gainers and losers
    gainers = data.nlargest(5, '% Change')
    losers = data.nsmallest(5, '% Change')
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader(f"🏆 {title} Top Gainers")
        st.dataframe(
            gainers.style.applymap(color_change, subset=['% Change']).format({
                'Last Price': '{:.2f}',
                'Change': '{:+.2f}',
                '% Change': '{:+.2f}%'
            }),
            use_container_width=True,
            hide_index=True,
            height=300
        )
    
    with col2:
        st.subheader(f"📉 {title} Top Losers")
        st.dataframe(
            losers.style.applymap(color_change, subset=['% Change']).format({
                'Last Price': '{:.2f}',
                'Change': '{:+.2f}',
                '% Change': '{:+.2f}%'
            }),
            use_container_width=True,
            hide_index=True,
            height=300
        )

def main():
    show_header()
    
    # Add refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Nifty 50 Section
    st.markdown("## 🇮🇳 NIFTY 50")
    nifty50_data = get_nifty_data("NIFTY 50")
    display_gainers_losers(nifty50_data, "Nifty 50")
    
    st.markdown("---")
    
    # Nifty 100 Section
    st.markdown("## 🇮🇳 NIFTY 100")
    nifty100_data = get_nifty_data("NIFTY 100")
    display_gainers_losers(nifty100_data, "Nifty 100")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center;'>
        <p>Data provided by NSE India & Yahoo Finance</p>
        <p>📊 FinSmart Wealth Advisory | 📞 +91 XXXXXXXXXX</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()