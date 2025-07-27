import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime

# Custom CSS for styling
st.markdown("""
    <style>
        .stock-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
        }
        .view-charts-btn {
            background-color: #4CAF50;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
        }
        .remove-btn {
            background-color: #ff4444;
            color: white;
            border: none;
            padding: 6px 12px;
            border-radius: 4px;
            cursor: pointer;
        }
        .ta-container {
            margin-top: 20px;
            padding: 15px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
        }
        .add-stock-section {
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
    </style>
""", unsafe_allow_html=True)

def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}'
    except:
        return ''

# Initialize session state
if 'selected_stock' not in st.session_state:
    st.session_state.selected_stock = None
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = ["INFY.NS", "RELIANCE.NS"]  # Default watchlist

# Dynamic stock dictionary loading
@st.cache_data(ttl=86400)  # Cache for 1 day
def load_nse_stocks():
    try:
        # Get top NSE stocks (this is a placeholder - you might need a real API)
        nifty50 = yf.Ticker("^NSEI").components
        stocks = {}
        for symbol in nifty50:
            try:
                ticker = yf.Ticker(f"{symbol}.NS")
                info = ticker.info
                stocks[f"{symbol}.NS"] = info.get('longName', symbol)
            except:
                continue
        return stocks
    except:
        # Fallback to a default list if API fails
        return {
            "TCS.NS": "Tata Consultancy Services",
            "INFY.NS": "Infosys",
            "RELIANCE.NS": "Reliance Industries",
            "HDFCBANK.NS": "HDFC Bank",
            "ICICIBANK.NS": "ICICI Bank",
            "HCLTECH.NS": "HCL Technologies",
            "SBIN.NS": "State Bank of India",
            "BHARTIARTL.NS": "Bharti Airtel",
            "LT.NS": "Larsen & Toubro",
            "KOTAKBANK.NS": "Kotak Mahindra Bank",
            "ITC.NS": "ITC Limited",
            "ASIANPAINT.NS": "Asian Paints",
            "BAJFINANCE.NS": "Bajaj Finance"
        }

# Load stocks dynamically
stock_dict = load_nse_stocks()
name_to_symbol = {v: k for k, v in stock_dict.items()}

# Page layout
st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")

# --- Header with Add to Watchlist ---
col1, col2 = st.columns([3, 2])
with col1:
    st.title("📈 NSE Stock Watchlist")
with col2:
    with st.expander("➕ Add to Watchlist", expanded=False):
        search_term = st.text_input("Search stocks", "")
        
        # Filter stocks based on search
        filtered_stocks = [
            name for name in stock_dict.values() 
            if search_term.lower() in name.lower()
        ]
        
        selected_stock = st.selectbox(
            "Select stock to add",
            filtered_stocks,
            index=0 if not filtered_stocks else None,
            key="add_stock_select"
        )
        
        if st.button("Add to Watchlist"):
            symbol = name_to_symbol[selected_stock]
            if symbol not in st.session_state.watchlist:
                st.session_state.watchlist.append(symbol)
                st.success(f"Added {selected_stock} to watchlist!")
                st.rerun()
            else:
                st.warning(f"{selected_stock} is already in your watchlist")

# --- Watchlist Display ---
st.subheader("📉 Your Watchlist")

if not st.session_state.watchlist:
    st.info("Your watchlist is empty. Add stocks using the 'Add to Watchlist' section above.")
else:
    # Get data for all watchlist stocks
    @st.cache_data(ttl=300)
    def get_watchlist_data(watchlist):
        data = []
        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1mo")
                
                if len(hist) < 2:
                    continue
                    
                current = hist["Close"][-1]
                prev_close = hist["Close"][-2]
                day_change = ((current - prev_close) / prev_close) * 100
                
                data.append({
                    "Symbol": symbol,
                    "Company": stock_dict.get(symbol, symbol),
                    "Price": f"{current:.2f}",
                    "Change (%)": f"{day_change:+.2f}%",
                })
            except Exception as e:
                st.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame(data)
    
    watchlist_df = get_watchlist_data(st.session_state.watchlist)
    
    if not watchlist_df.empty:
        st.dataframe(
            watchlist_df.style.applymap(color_percent, subset=["Change (%)"]),
            use_container_width=True
        )
    
    # Display each stock with actions
    for symbol in st.session_state.watchlist:
        company = stock_dict.get(symbol, symbol)
        
        col1, col2, col3 = st.columns([4, 1, 1])
        with col1:
            st.markdown(f"**{company}** ({symbol})")
        
        with col2:
            # Toggle button for charts
            if st.button(f"📊 Charts", key=f"view_{symbol}"):
                if st.session_state.selected_stock == symbol:
                    st.session_state.selected_stock = None
                else:
                    st.session_state.selected_stock = symbol
        
        with col3:
            # Remove button
            if st.button("🗑️ Remove", key=f"remove_{symbol}"):
                st.session_state.watchlist.remove(symbol)
                if st.session_state.selected_stock == symbol:
                    st.session_state.selected_stock = None
                st.rerun()
        
        # Show technical analysis if this stock is selected
        if st.session_state.selected_stock == symbol:
            with st.container():
                st.markdown(f"### Technical Analysis: {company}")
                
                # Get historical data
                @st.cache_data(ttl=300)
                def get_stock_history(symbol):
                    stock = yf.Ticker(symbol)
                    return stock.history(period="1y")
                
                hist = get_stock_history(symbol)
                
                # Create tabs for different charts
                tab1, tab2, tab3 = st.tabs(["Price Trend", "Moving Averages", "Technical Indicators"])
                
                with tab1:
                    # Price chart
                    fig = go.Figure()
                    fig.add_trace(go.Candlestick(
                        x=hist.index,
                        open=hist['Open'],
                        high=hist['High'],
                        low=hist['Low'],
                        close=hist['Close'],
                        name='Price'
                    ))
                    fig.update_layout(
                        title=f"{company} Price Trend",
                        xaxis_rangeslider_visible=False,
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    # Moving averages
                    hist['MA20'] = hist['Close'].rolling(20).mean()
                    hist['MA50'] = hist['Close'].rolling(50).mean()
                    
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=hist.index, y=hist['Close'], name='Price'
                    ))
                    fig.add_trace(go.Scatter(
                        x=hist.index, y=hist['MA20'], name='20-day MA'
                    ))
                    fig.add_trace(go.Scatter(
                        x=hist.index, y=hist['MA50'], name='50-day MA'
                    ))
                    fig.update_layout(
                        title="Moving Averages",
                        height=500
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    # Technical indicators
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        # RSI
                        delta = hist['Close'].diff()
                        gain = delta.where(delta > 0, 0)
                        loss = -delta.where(delta < 0, 0)
                        avg_gain = gain.rolling(14).mean()
                        avg_loss = loss.rolling(14).mean()
                        rs = avg_gain / avg_loss
                        rsi = 100 - (100 / (1 + rs))
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=rsi.index, y=rsi, name='RSI'
                        ))
                        fig.add_hline(y=70, line_dash="dash", line_color="red")
                        fig.add_hline(y=30, line_dash="dash", line_color="green")
                        fig.update_layout(
                            title="RSI (14-day)",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    with col2:
                        # MACD
                        exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
                        exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
                        macd = exp12 - exp26
                        signal = macd.ewm(span=9, adjust=False).mean()
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(
                            x=macd.index, y=macd, name='MACD'
                        ))
                        fig.add_trace(go.Scatter(
                            x=signal.index, y=signal, name='Signal'
                        ))
                        fig.update_layout(
                            title="MACD",
                            height=400
                        )
                        st.plotly_chart(fig, use_container_width=True)

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <strong>📊 Stock Analysis Platform</strong><br>
        Data provided by Yahoo Finance | Last updated: {date}
    </div>
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)