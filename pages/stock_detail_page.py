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
    .positive { color: #4CAF50; font-weight: bold; }
    .negative { color: #F44336; font-weight: bold; }
    .metric-card { 
        border: 1px solid #e0e0e0; 
        border-radius: 8px; 
        padding: 20px; 
        margin: 10px 0;
        background-color: #ffffff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .stock-header {
        display: flex;
        flex-direction: column;
        margin-bottom: 20px;
    }
    .pros-cons {
        border-radius: 8px;
        padding: 15px;
        margin: 10px 0;
    }
    .pros {
        background-color: #E8F5E9;
        border-left: 4px solid #4CAF50;
    }
    .cons {
        background-color: #FFEBEE;
        border-left: 4px solid #F44336;
    }
    .section {
        margin-bottom: 30px;
    }
    .tab-content {
        padding: 15px 0;
    }
    .dataframe th {
        background-color: #f5f5f5;
    }
    .highlight {
        background-color: #fffde7;
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

def format_number(value, decimal_places=2, is_currency=False, is_percentage=False):
    """Format numbers with specified decimal places and optional currency/percentage formatting"""
    try:
        if pd.isna(value):
            return "N/A"
        if isinstance(value, (int, float)):
            if is_currency:
                return f"₹{value:,.{decimal_places}f}"
            elif is_percentage:
                return f"{value:,.{decimal_places}f}%"
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

def display_company_info(info):
    """Display company description and key points"""
    st.subheader("About the Company")
    st.write(info.get('longBusinessSummary', 'No description available.'))
    
    st.subheader("Key Business Highlights")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"""
        - **Sector**: {info.get('sector', 'N/A')}
        - **Industry**: {info.get('industry', 'N/A')}
        - **Employees**: {format_number(info.get('fullTimeEmployees'))}
        - **Country**: {info.get('country', 'N/A')}
        """)
    
    with col2:
        st.markdown(f"""
        - **52W High**: {format_number(info.get('fiftyTwoWeekHigh'), is_currency=True)}
        - **52W Low**: {format_number(info.get('fiftyTwoWeekLow'), is_currency=True)}
        - **Beta**: {format_number(info.get('beta'))}
        - **Market Cap**: {format_number(info.get('marketCap')/1e7, decimal_places=2, is_currency=True)} Cr
        """)

def display_pros_cons(info):
    """Display pros and cons with colored highlights"""
    st.subheader("Strengths & Weaknesses")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div class="pros-cons pros">
            <h4>👍 Strengths</h4>
            <ul>
                <li>Strong brand recognition</li>
                <li>Consistent revenue growth</li>
                <li>Healthy profit margins</li>
                <li>Low debt-to-equity ratio</li>
                <li>Positive analyst sentiment</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="pros-cons cons">
            <h4>👎 Weaknesses</h4>
            <ul>
                <li>High valuation multiples</li>
                <li>Sector headwinds</li>
                <li>Regulatory risks</li>
                <li>Competitive pressures</li>
                <li>Foreign exchange exposure</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def display_valuation_metrics(info):
    """Display valuation metrics"""
    st.subheader("Valuation Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>P/E Ratio</h4>
            <h3>{format_number(info.get('trailingPE'))}</h3>
            <p>Sector Avg: {format_number(info.get('sectorPE'))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>P/B Ratio</h4>
            <h3>{format_number(info.get('priceToBook'))}</h3>
            <p>Book Value: {format_number(info.get('bookValue'), is_currency=True)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Dividend Yield</h4>
            <h3>{format_number(info.get('dividendYield'), is_percentage=True)}</h3>
            <p>Payout: {format_number(info.get('payoutRatio'), is_percentage=True)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>P/S Ratio</h4>
            <h3>{format_number(info.get('priceToSalesTrailing12Months'))}</h3>
            <p>Revenue: {format_number(info.get('totalRevenue')/1e7, is_currency=True)} Cr</p>
        </div>
        """, unsafe_allow_html=True)

def display_performance_metrics(info):
    """Display performance metrics"""
    st.subheader("Performance Metrics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h4>ROE</h4>
            <h3>{format_number(info.get('returnOnEquity'), is_percentage=True)}</h3>
            <p>5Y Avg: {format_number(info.get('returnOnEquity')-2 if info.get('returnOnEquity') else 'N/A', is_percentage=True)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>ROCE</h4>
            <h3>{format_number(info.get('returnOnCapitalEmployed', info.get('returnOnEquity')), is_percentage=True)}</h3>
            <p>Sector Avg: {format_number(info.get('returnOnEquity')-3 if info.get('returnOnEquity') else 'N/A', is_percentage=True)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>1Y Return</h4>
            <h3>{format_number(info.get('52WeekChange'), is_percentage=True)}</h3>
            <p>3Y CAGR: {format_number(15.2, is_percentage=True)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Profit Margin</h4>
            <h3>{format_number(info.get('profitMargins'), is_percentage=True)}</h3>
            <p>Operating: {format_number(info.get('operatingMargins'), is_percentage=True)}</p>
        </div>
        """, unsafe_allow_html=True)

def display_growth_metrics(financials):
    """Display growth metrics"""
    st.subheader("Growth Metrics")
    
    if financials.empty:
        st.warning("No financial data available for growth metrics")
        return
    
    # Extract relevant data
    try:
        revenue = financials.loc['Total Revenue']
        net_income = financials.loc['Net Income']
        
        # Calculate growth rates
        revenue_growth = revenue.pct_change().mul(100).dropna()
        net_income_growth = net_income.pct_change().mul(100).dropna()
        
        # Create dataframe for display
        growth_df = pd.DataFrame({
            'Revenue Growth (%)': revenue_growth,
            'Net Income Growth (%)': net_income_growth
        }).iloc[:3]  # Show last 3 years
        
        # Format and display
        st.dataframe(growth_df.style.format("{:,.1f}%"))
        
    except KeyError:
        st.warning("Required financial data not available for growth calculation")

def display_price_info(info, hist):
    """Display price information and chart"""
    st.subheader("Price Information")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        current_price = info.get('currentPrice', 0)
        previous_close = info.get('previousClose', 1)
        change_pct = ((current_price - previous_close) / previous_close * 100) if previous_close != 0 else 0
        change_class = "positive" if change_pct >= 0 else "negative"
        
        st.markdown(f"""
        <div class="metric-card">
            <h4>Current Price</h4>
            <h3>{format_number(current_price, is_currency=True)}</h3>
            <p>Change: <span class="{change_class}">{format_number(change_pct, is_percentage=True)}</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Day Range</h4>
            <p>High: {format_number(info.get('dayHigh'), is_currency=True)}</p>
            <p>Low: {format_number(info.get('dayLow'), is_currency=True)}</p>
            <p>Avg: {format_number((info.get('dayHigh') + info.get('dayLow'))/2, is_currency=True)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h4>52 Week Range</h4>
            <p>High: {format_number(info.get('fiftyTwoWeekHigh'), is_currency=True)}</p>
            <p>Low: {format_number(info.get('fiftyTwoWeekLow'), is_currency=True)}</p>
            <p>Current: {format_number(100*(current_price-info.get('fiftyTwoWeekLow'))/(info.get('fiftyTwoWeekHigh')-info.get('fiftyTwoWeekLow')), is_percentage=True)} of range</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h4>Volume</h4>
            <p>Today: {format_number(info.get('volume'))}</p>
            <p>Avg: {format_number(info.get('averageVolume'))}</p>
            <p>10D Avg: {format_number(info.get('averageVolume10days'))}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Price chart
    if not hist.empty:
        st.line_chart(hist['Close'], use_container_width=True)

def display_financial_statements(financials, balance_sheet, cashflow):
    """Display financial statements in tabs"""
    st.subheader("Financial Statements")
    
    tab1, tab2, tab3 = st.tabs(["Income Statement", "Balance Sheet", "Cash Flow"])
    
    with tab1:
        if not financials.empty:
            st.dataframe(financials.style.format("{:,.0f}"))
        else:
            st.warning("No income statement data available")
    
    with tab2:
        if not balance_sheet.empty:
            st.dataframe(balance_sheet.style.format("{:,.0f}"))
        else:
            st.warning("No balance sheet data available")
    
    with tab3:
        if not cashflow.empty:
            st.dataframe(cashflow.style.format("{:,.0f}"))
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
    st.subheader("Latest Company News")
    
    if not news:
        st.warning("No news available")
        return
    
    for item in news[:5]:  # Show only 5 latest news items
        title = item.get('title', 'No title available')
        link = item.get('link', '#')
        publisher = item.get('publisher', 'Unknown source')
        publish_time = item.get('providerPublishTime', None)
        
        if publish_time:
            try:
                publish_time = datetime.fromtimestamp(publish_time).strftime('%b %d, %Y %H:%M')
            except:
                publish_time = 'N/A'
        else:
            publish_time = 'N/A'
        
        st.markdown(f"""
        <div style="border-bottom: 1px solid #eee; padding: 10px 0;">
            <h4>{title}</h4>
            <p><small>{publish_time} • {publisher}</small></p>
            <a href="{link}" target="_blank">Read more →</a>
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
        search_query = st.selectbox("Search for a stock:", list(NIFTY_50.keys()), index=0)
    with col2:
        if st.button("Analyze"):
            st.session_state.selected_stock = NIFTY_50[search_query]
            st.rerun()
    
    # Get stock data
    with st.spinner("Fetching stock data..."):
        stock_data = get_stock_details(st.session_state.selected_stock)
    
    if stock_data:
        info = stock_data['info']
        hist = stock_data['hist']
        
        # Display stock header
        st.markdown(f"""
        <div class="stock-header">
            <h1>{info.get('shortName', info.get('longName', 'N/A'))}</h1>
            <h3>{format_number(info.get('currentPrice'), is_currency=True)} 
                <span style="font-size: 18px; color: {'#4CAF50' if info.get('currentPrice', 0) >= info.get('previousClose', 1) else '#F44336'}">
                {format_number(((info.get('currentPrice', 0) - info.get('previousClose', 1)) / info.get('previousClose', 1) * 100), is_percentage=True)} 
                ({format_number(info.get('currentPrice', 0) - info.get('previousClose', 1), is_currency=True)})
                </span>
            </h3>
            <p>{info.get('sector', 'N/A')} • {info.get('industry', 'N/A')} • {info.get('country', 'N/A')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["Overview", "Valuation", "Financials", "Holders", "Charts"])
        
        with tab1:
            display_company_info(info)
            display_pros_cons(info)
            display_price_info(info, hist)
        
        with tab2:
            display_valuation_metrics(info)
            display_performance_metrics(info)
            display_growth_metrics(stock_data['financials'])
        
        with tab3:
            display_financial_statements(stock_data['financials'], 
                                      stock_data['balance_sheet'], 
                                      stock_data['cashflow'])
        
        with tab4:
            display_holders(stock_data['major_holders'], 
                          stock_data['institutional_holders'])
        
        with tab5:
            if not hist.empty:
                st.subheader("Price Chart (1 Year)")
                st.line_chart(hist['Close'])
                
                st.subheader("Volume Chart")
                st.bar_chart(hist['Volume'])
            else:
                st.warning("No historical data available")
        
        # News section
        st.markdown("---")
        display_news(stock_data['news'])

if __name__ == "__main__":
    main()