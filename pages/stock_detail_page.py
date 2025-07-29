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

def format_number(value, decimal_places=2):
    """Format numbers with specified decimal places"""
    try:
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, float)):
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

def get_market_news():
    """Fetch market news from Moneycontrol"""
    try:
        url = "https://www.moneycontrol.com/news/business/stocks/"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')
        news_items = soup.find_all('li', {'class': 'clearfix'})[:5]
        
        news_list = []
        for item in news_items:
            title = item.find('h2').text.strip() if item.find('h2') else "No title"
            link = item.find('a')['href'] if item.find('a') else "#"
            news_list.append({'title': title, 'link': link})
        
        return news_list
    except Exception as e:
        st.warning(f"Could not fetch news: {str(e)}")
        return []

def display_stock_metrics(info):
    """Display key stock metrics in cards"""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_price = info.get('currentPrice', 0)
        previous_close = info.get('previousClose', 1)
        change_pct = ((current_price - previous_close) / previous_close * 100) if previous_close != 0 else 0
        change_class = "positive" if change_pct >= 0 else "negative"
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Price</h4>
            <h3>₹{format_number(current_price)}</h3>
            <p>Change: <span class="{change_class}">{format_number(change_pct)}%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Valuation</h4>
            <p>PE: {format_number(info.get('trailingPE'))}</p>
            <p>P/B: {format_number(info.get('priceToBook'))}</p>
            <p>P/S: {format_number(info.get('priceToSalesTrailing12Months'))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        market_cap = info.get('marketCap', 0)
        st.markdown(f"""
        <div class="metric-card">
            <h4>Financials</h4>
            <p>Market Cap: ₹{format_number(market_cap/1e7)} Cr</p>
            <p>ROE: {format_number(info.get('returnOnEquity'))}%</p>
            <p>ROA: {format_number(info.get('returnOnAssets'))}%</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Dividend</h4>
            <p>Yield: {format_number(info.get('dividendYield'))}%</p>
            <p>Rate: ₹{format_number(info.get('dividendRate'))}</p>
            <p>Payout: {format_number(info.get('payoutRatio'))}%</p>
        </div>
        """, unsafe_allow_html=True)

def format_financial_data(df):
    """Format financial data with 2 decimal places"""
    return df.style.format("{:,.2f}")

def display_financials(financials, balance_sheet, cashflow):
    """Display financial statements"""
    st.subheader("Financial Statements")
    
    tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
    
    with tab1:
        if not financials.empty:
            st.dataframe(format_financial_data(financials))
        else:
            st.warning("No income statement data available")
    
    with tab2:
        if not balance_sheet.empty:
            st.dataframe(format_financial_data(balance_sheet))
        else:
            st.warning("No balance sheet data available")
    
    with tab3:
        if not cashflow.empty:
            st.dataframe(format_financial_data(cashflow))
        else:
            st.warning("No cash flow data available")

def display_holders(major_holders, institutional_holders):
    """Display shareholder information"""
    st.subheader("Shareholding Pattern")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Major Holders**")
        if not major_holders.empty:
            st.dataframe(major_holders)
        else:
            st.warning("No major holders data available")
    
    with col2:
        st.markdown("**Institutional Holders**")
        if not institutional_holders.empty:
            st.dataframe(institutional_holders)
        else:
            st.warning("No institutional holders data available")

def display_news(news):
    """Display company news"""
    st.subheader("Latest News")
    
    if not news:
        st.warning("No news available")
        return
    
    for item in news[:5]:  # Show only 5 latest news items
        title = item.get('title', 'No title available')
        link = item.get('link', '#')
        publisher = item.get('publisher', 'Unknown source')
        
        # Handle timestamp conversion
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
        
        # Display key metrics
        display_stock_metrics(info)
        
        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs(["Financials", "Holdings", "News", "Charts"])
        
        with tab1:
            display_financials(stock_data['financials'], stock_data['balance_sheet'], stock_data['cashflow'])
        
        with tab2:
            display_holders(stock_data['major_holders'], stock_data['institutional_holders'])
        
        with tab3:
            display_news(stock_data['news'])
        
        with tab4:
            st.subheader("Price Chart (1 Year)")
            if not stock_data['hist'].empty:
                st.line_chart(stock_data['hist']['Close'])
            else:
                st.warning("No historical data available")
    
    # Market news section
    st.markdown("---")
    st.subheader("📰 Latest Market News")
    market_news = get_market_news()
    for news in market_news:
        st.markdown(f"- [{news['title']}]({news['link']})")

if __name__ == "__main__":
    main()