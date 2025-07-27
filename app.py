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
        .search-results {
            max-height: 300px;
            overflow-y: auto;
            margin-top: 10px;
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
    st.session_state.watchlist = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []

# Page layout
st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")

# --- Header ---
st.title("📈 NSE Stock Watchlist")

# --- Stock Search and Add Section ---
with st.expander("🔍 Search and Add Stocks", expanded=True):
    search_term = st.text_input("Search NSE stocks by company name or symbol", "")
    
    if st.button("Search"):
        if search_term:
            try:
                # Search using yfinance (note: yfinance has limited search capabilities)
                # For better search, consider using a dedicated stock API
                ticker = yf.Ticker(f"{search_term.upper()}.NS")
                info = ticker.info
                
                if info.get('symbol', '').endswith('.NS'):
                    st.session_state.search_results = [{
                        'symbol': info['symbol'],
                        'name': info.get('longName', info['symbol']),
                        'sector': info.get('sector', 'N/A'),
                        'currentPrice': info.get('currentPrice', 'N/A')
                    }]
                else:
                    # Fallback to Nifty 50 components if specific search fails
                    nifty50 = yf.Ticker("^NSEI").components
                    results = []
                    for symbol in nifty50[:10]:  # Limit to first 10 for performance
                        try:
                            ticker = yf.Ticker(f"{symbol}.NS")
                            info = ticker.info
                            if (search_term.lower() in info.get('longName', '').lower() or 
                                search_term.lower() in symbol.lower()):
                                results.append({
                                    'symbol': f"{symbol}.NS",
                                    'name': info.get('longName', symbol),
                                    'sector': info.get('sector', 'N/A'),
                                    'currentPrice': info.get('currentPrice', 'N/A')
                                })
                        except:
                            continue
                    st.session_state.search_results = results
            except Exception as e:
                st.error(f"Search error: {e}")
                st.session_state.search_results = []

    # Display search results
    if st.session_state.search_results:
        st.markdown("### Search Results")
        for result in st.session_state.search_results:
            col1, col2, col3 = st.columns([4, 2, 1])
            with col1:
                st.markdown(f"**{result['name']}** ({result['symbol']})")
                st.caption(f"Sector: {result['sector']}")
            with col2:
                st.markdown(f"Price: {result['currentPrice'] if result['currentPrice'] != 'N/A' else 'N/A'}")
            with col3:
                if st.button("Add", key=f"add_{result['symbol']}"):
                    if result['symbol'] not in st.session_state.watchlist:
                        st.session_state.watchlist.append(result['symbol'])
                        st.success(f"Added {result['name']} to watchlist!")
                        st.rerun()
                    else:
                        st.warning(f"{result['name']} is already in your watchlist")

# --- Watchlist Display ---
st.subheader("📉 Your Watchlist")

if not st.session_state.watchlist:
    st.info("Your watchlist is empty. Search and add stocks above.")
else:
    # Get data for all watchlist stocks
    @st.cache_data(ttl=300)
    def get_watchlist_data(watchlist):
        data = []
        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1mo")
                info = stock.info
                
                if len(hist) < 2:
                    continue
                    
                current = hist["Close"][-1]
                prev_close = hist["Close"][-2]
                day_change = ((current - prev_close) / prev_close) * 100
                
                data.append({
                    "Symbol": symbol,
                    "Company": info.get('longName', symbol),
                    "Price": f"{current:.2f}",
                    "Change (%)": f"{day_change:+.2f}%",
                    "Sector": info.get('sector', 'N/A')
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
        try:
            stock = yf.Ticker(symbol)
            info = stock.info
            company = info.get('longName', symbol)
            sector = info.get('sector', 'N/A')
            
            col1, col2, col3 = st.columns([4, 1, 1])
            with col1:
                st.markdown(f"**{company}** ({symbol})")
                st.caption(f"Sector: {sector}")
            
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
        except Exception as e:
            st.error(f"Error processing {symbol}: {e}")

# --- Footer ---
st.markdown("---")
st.markdown("""
    <div style='text-align: center;'>
        <strong>📊 NSE Stock Watchlist</strong><br>
        Data provided by Yahoo Finance | Last updated: {date}
    </div>
""".format(date=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)