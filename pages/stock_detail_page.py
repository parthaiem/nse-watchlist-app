import streamlit as st
import yfinance as yf
import pandas as pd
import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Configuration
st.set_page_config(page_title="Stock Analysis Dashboard", layout="wide")

# Custom CSS
st.markdown("""
<style>
    .positive { color: green; font-weight: bold; }
    .negative { color: red; font-weight: bold; }
    .metric-card { 
        border: 1px solid #ddd; 
        border-radius: 5px; 
        padding: 15px; 
        margin: 10px 0;
        background-color: #f9f9f9;
    }
    .stock-header {
        display: flex;
        align-items: center;
        margin-bottom: 20px;
    }
    .news-card {
        border: 1px solid #eee;
        border-radius: 5px;
        padding: 15px;
        margin: 10px 0;
    }
    .dataframe th, .dataframe td {
        text-align: right;
    }
    .section-title {
        margin-top: 20px;
        margin-bottom: 10px;
        padding-bottom: 5px;
        border-bottom: 1px solid #eee;
    }
    .pros-cons {
        margin: 10px 0;
        padding: 10px;
        border-radius: 5px;
    }
    .pros {
        background-color: #e6f7e6;
    }
    .cons {
        background-color: #ffebee;
    }
</style>
""", unsafe_allow_html=True)

# Nifty 50 stocks with symbols
NIFTY_50 = {
    'RELIANCE': 'RELIANCE.NS',
    'TCS': 'TCS.NS',
    'HDFC BANK': 'HDFCBANK.NS',
    'ICICI BANK': 'ICICIBANK.NS',
    'HUL': 'HINDUNILVR.NS',
    'INFOSYS': 'INFY.NS',
    'ITC': 'ITC.NS',
    'SBIN': 'SBIN.NS',
    'BHARTI AIRTEL': 'BHARTIARTL.NS',
    'LT': 'LT.NS',
    'KOTAK BANK': 'KOTAKBANK.NS',
    'HDFC': 'HDFC.NS',
    'ASIAN PAINT': 'ASIANPAINT.NS',
    'DMART': 'DMART.NS',
    'ULTRACEMCO': 'ULTRACEMCO.NS',
    'BAJFINANCE': 'BAJFINANCE.NS',
    'WIPRO': 'WIPRO.NS',
    'ONGC': 'ONGC.NS',
    'NTPC': 'NTPC.NS',
    'NESTLE': 'NESTLEIND.NS',
    'TITAN': 'TITAN.NS',
    'ADANI PORTS': 'ADANIPORTS.NS',
    'M&M': 'M&M.NS',
    'SUN PHARMA': 'SUNPHARMA.NS',
    'BAJAJ AUTO': 'BAJAJ-AUTO.NS',
    'TATA STEEL': 'TATASTEEL.NS',
    'POWERGRID': 'POWERGRID.NS',
    'JSW STEEL': 'JSWSTEEL.NS',
    'AXIS BANK': 'AXISBANK.NS',
    'TECHM': 'TECHM.NS',
    'HCLTECH': 'HCLTECH.NS',
    'GRASIM': 'GRASIM.NS',
    'BRITANNIA': 'BRITANNIA.NS',
    'EICHERMOT': 'EICHERMOT.NS',
    'DIVISLAB': 'DIVISLAB.NS',
    'DRREDDY': 'DRREDDY.NS',
    'CIPLA': 'CIPLA.NS',
    'UPL': 'UPL.NS',
    'BAJAJFINSV': 'BAJAJFINSV.NS',
    'MARUTI': 'MARUTI.NS',
    'COALINDIA': 'COALINDIA.NS',
    'TATAMOTORS': 'TATAMOTORS.NS',
    'BPCL': 'BPCL.NS',
    'INDUSINDBK': 'INDUSINDBK.NS',
    'HEROMOTOCO': 'HEROMOTOCO.NS',
    'HINDALCO': 'HINDALCO.NS',
    'TATACONSUM': 'TATACONSUM.NS',
    'SHREECEM': 'SHREECEM.NS',
    'SBILIFE': 'SBILIFE.NS',
    'HDFCLIFE': 'HDFCLIFE.NS'
}

def format_number(value, decimal_places=2, is_percent=False, is_currency=False):
    """Format numbers with specified decimal places"""
    try:
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, float)):
            if is_percent:
                return f"{value:.{decimal_places}f}%"
            if is_currency:
                return f"₹ {value:,.{decimal_places}f}"
            return f"{value:,.{decimal_places}f}"
        return str(value)
    except:
        return str(value)

def get_stock_details(symbol):
    """Get comprehensive stock details from Yahoo Finance"""
    try:
        stock = yf.Ticker(symbol)
        info = stock.info
        hist = stock.history(period="1y")
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        cashflow = stock.cashflow
        recommendations = stock.recommendations
        major_holders = stock.major_holders
        institutional_holders = stock.institutional_holders
        news = stock.news
        
        return {
            'info': info,
            'hist': hist,
            'financials': financials,
            'balance_sheet': balance_sheet,
            'cashflow': cashflow,
            'recommendations': recommendations,
            'major_holders': major_holders,
            'institutional_holders': institutional_holders,
            'news': news
        }
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def display_key_metrics(info):
    """Display key metrics in a structured format"""
    st.markdown("### Key Metrics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(f"**Market Cap:** {format_number(info.get('marketCap', 0)/1e7, is_currency=True)} Cr.")
        st.markdown(f"**Current Price:** {format_number(info.get('currentPrice', 0), is_currency=True)}")
        st.markdown(f"**High / Low:** {format_number(info.get('dayHigh', 0), is_currency=True)} / {format_number(info.get('dayLow', 0), is_currency=True)}")
        st.markdown(f"**Stock P/E:** {format_number(info.get('trailingPE', 0))}")
        st.markdown(f"**Book Value:** {format_number(info.get('bookValue', 0), is_currency=True)}")
        st.markdown(f"**Dividend Yield:** {format_number(info.get('dividendYield', 0), is_percent=True)}")
    
    with col2:
        st.markdown(f"**ROCE:** {format_number(info.get('returnOnCapitalEmployed', 0), is_percent=True)}")
        st.markdown(f"**ROE:** {format_number(info.get('returnOnEquity', 0), is_percent=True)}")
        st.markdown(f"**Face Value:** {format_number(info.get('faceValue', 0), is_currency=True)}")
        st.markdown(f"**Profit Var 5Yrs:** {format_number(44.2, is_percent=True)}")  # Example value
        st.markdown(f"**Return over 5years:** {format_number(37.0, is_percent=True)}")  # Example value
        st.markdown(f"**Industry PE:** {format_number(15.4)}")  # Example value
    
    with col3:
        st.markdown(f"**Price to Earning:** {format_number(info.get('trailingPE', 0))}")
        st.markdown(f"**Return over 3months:** {format_number(17.9, is_percent=True)}")  # Example value
        st.markdown(f"**Return over 6months:** {format_number(-11.2, is_percent=True)}")  # Example value
        st.markdown(f"**Return on equity:** {format_number(info.get('returnOnEquity', 0), is_percent=True)}")
        st.markdown(f"**Qtr Sales Var:** {format_number(-5.61, is_percent=True)}")  # Example value
        st.markdown(f"**Qtr Profit Var:** {format_number(-5.99, is_percent=True)}")  # Example value

def display_company_info():
    """Display company information section"""
    st.markdown("### About")
    st.markdown("""
    Incorporated in 1995, Aditya Birla Money Ltd is a stock broker, capital market products distributor, 
    depository participant and PMS provider.
    """)
    
    st.markdown("### Key Points")
    st.markdown("**Business Overview:**")
    st.markdown("""
    - ABML is a part of Aditya Birla Capital Limited which in turn is a part of Grasim Industries
    - It is registered as a Stock Broker with SEBI and is a member of BSE and NSE in equities and derivatives
    """)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Pros")
        st.markdown("""
        <div class="pros-cons pros">
            <p>✓ Company has delivered good profit growth of 44.2% CAGR over last 5 years</p>
            <p>✓ Company has a good return on equity (ROE) track record: 3 Years ROE 37.7%</p>
            <p>✓ Debtor days have improved from 35.0 to 24.0 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("### Cons")
        st.markdown("""
        <div class="pros-cons cons">
            <p>✗ Stock is trading at 4.05 times its book value</p>
            <p>✗ Though the company is reporting repeated profits, it is not paying out dividend</p>
            <p>✗ Company has low interest coverage ratio</p>
        </div>
        """, unsafe_allow_html=True)

def display_financial_performance():
    """Display financial performance metrics"""
    st.markdown("### Financial Performance")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**Profit after tax:** ₹ 73.2 Cr.")
        st.markdown("**PAT Qtr:** ₹ 15.4 Cr.")
        st.markdown("**Sales growth 3Years:** 24.8%")
    
    with col2:
        st.markdown("**Sales growth 5Years:** 21.6%")
        st.markdown("**Profit Var 3Yrs:** 41.6%")
        st.markdown("**ROE 5Yr:** 38.5%")
    
    with col3:
        st.markdown("**ROE 3Yr:** 37.7%")
        st.markdown("**Return over 1year:** 2.28%")
        st.markdown("**Return over 3years:** [Value]")

def main():
    st.title("📊 Comprehensive Stock Analysis Dashboard")
    
    # Initialize session state
    if 'selected_stock' not in st.session_state:
        st.session_state.selected_stock = 'RELIANCE.NS'
    
    # Search bar
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.selectbox("Search for a stock:", list(NIFTY_50.keys()))
    with col2:
        if st.button("Search"):
            st.session_state.selected_stock = NIFTY_50[search_query]
            st.rerun()
    
    # Get stock data
    stock_data = get_stock_details(st.session_state.selected_stock)
    
    if stock_data:
        info = stock_data['info']
        
        # Display stock header
        st.markdown(f"""
        <div class="stock-header">
            <h2>{info.get('longName', 'N/A')} ({st.session_state.selected_stock})</h2>
            <p>Sector: {info.get('sector', 'N/A')} | Industry: {info.get('industry', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
            "Overview", "Chart", "Analysis", "Financials", "Holders", "News"
        ])
        
        with tab1:
            display_key_metrics(info)
            display_company_info()
            display_financial_performance()
        
        with tab2:
            st.subheader("Price Chart (1 Year)")
            if not stock_data['hist'].empty:
                st.line_chart(stock_data['hist']['Close'])
            else:
                st.warning("No historical data available")
        
        with tab3:
            st.subheader("Technical Analysis")
            st.write("Technical analysis charts and indicators would go here")
        
        with tab4:
            st.subheader("Financial Statements")
            display_financial_performance()
            
            subtab1, subtab2, subtab3 = st.tabs(["Profit & Loss", "Balance Sheet", "Cash Flow"])
            
            with subtab1:
                if not stock_data['financials'].empty:
                    st.dataframe(stock_data['financials'].style.format("{:,.2f}"))
                else:
                    st.warning("No P&L data available")
            
            with subtab2:
                if not stock_data['balance_sheet'].empty:
                    st.dataframe(stock_data['balance_sheet'].style.format("{:,.2f}"))
                else:
                    st.warning("No balance sheet data available")
            
            with subtab3:
                if not stock_data['cashflow'].empty:
                    st.dataframe(stock_data['cashflow'].style.format("{:,.2f}"))
                else:
                    st.warning("No cash flow data available")
            
            st.subheader("Ratios")
            st.write("Financial ratios analysis would go here")
        
        with tab5:
            st.subheader("Shareholding Pattern")
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Major Holders**")
                if not stock_data['major_holders'].empty:
                    st.dataframe(stock_data['major_holders'])
                else:
                    st.warning("No major holders data available")
            
            with col2:
                st.markdown("**Institutional Holders**")
                if not stock_data['institutional_holders'].empty:
                    st.dataframe(stock_data['institutional_holders'])
                else:
                    st.warning("No institutional holders data available")
            
            st.subheader("Investors")
            st.write("Investor information would go here")
        
        with tab6:
            st.subheader("Latest News")
            if stock_data['news']:
                for item in stock_data['news'][:5]:
                    title = item.get('title', 'No title available')
                    link = item.get('link', '#')
                    publisher = item.get('publisher', 'Unknown source')
                    
                    publish_time = item.get('providerPublishTime')
                    if publish_time:
                        try:
                            publish_time = datetime.fromtimestamp(publish_time).strftime('%Y-%m-%d %H:%M')
                        except:
                            publish_time = 'N/A'
                    else:
                        publish_time = 'N/A'
                    
                    st.markdown(f"""
                    <div class="news-card">
                        <h4>{title}</h4>
                        <p>Published: {publish_time}</p>
                        <p>Source: {publisher}</p>
                        <a href="{link}" target="_blank">Read more</a>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.warning("No news available")
            
            st.subheader("Documents")
            st.write("Company documents would be listed here")

if __name__ == "__main__":
    main()