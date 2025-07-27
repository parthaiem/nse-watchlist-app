import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
from streamlit_autorefresh import st_autorefresh
import plotly.graph_objs as go

# Custom CSS for styling
st.markdown("""
    <style>
        a.view-charts {
            background-color: #4CAF50;
            color: white;
            padding: 4px 8px;
            text-align: center;
            text-decoration: none;
            display: inline-block;
            border-radius: 4px;
            font-size: 14px;
        }
        a.view-charts:hover {
            background-color: #45a049;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px 4px 0px 0px;
        }
        .stTabs [aria-selected="true"] {
            background-color: #f0f2f6;
        }
        .stock-card {
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 12px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .remove-btn {
            background-color: #ff4444 !important;
            color: white !important;
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

# Stock dictionary
stock_dict = {
    "TCS.NS": "TATA CONSULTANCY SERVICES",
    "INFY.NS": "INFOSYS",
    "WIPRO.NS": "WIPRO",
    "HCLTECH.NS": "HCL TECHNOLOGIES",
    "RELIANCE.NS": "RELIANCE INDUSTRIES",
    "SBIN.NS": "STATE BANK OF INDIA",
    "ICICIBANK.NS": "ICICI BANK",
    "TECHM.NS": "TECH MAHINDRA",
    "HDFCBANK.NS": "HDFC BANK",
    "BHARTIARTL.NS": "BHARTI AIRTEL",
    "ITC.NS": "ITC LIMITED",
    "LT.NS": "LARSEN & TOUBRO",
    "KOTAKBANK.NS": "KOTAK MAHINDRA BANK",
    "ASIANPAINT.NS": "ASIAN PAINTS",
    "BAJFINANCE.NS": "BAJAJ FINANCE"
}

name_to_symbol = {v: k for k, v in stock_dict.items()}
all_names = list(name_to_symbol.keys())

# Initialize session state and page config
st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="datarefresh")

# --- Top bar layout ---
top_col1, top_col2, top_col3 = st.columns([1, 4, 2])

with top_col1:
    st.image("logo.jpg", width=100)

with top_col2:
    st.markdown("<h1 style='padding-top: 10px;'>📈 NSE Stock Watchlist</h1>", unsafe_allow_html=True)

with top_col3:
    if "user" in st.session_state:
        st.markdown(f"<p style='text-align:right; padding-top: 25px;'>👤 Logged in as <strong>{st.session_state.user}</strong></p>", unsafe_allow_html=True)
        if st.button("Logout", key="logout_btn"):
            st.session_state.clear()
            st.rerun()
    else:
        username = st.text_input("Enter your name to continue:", key="login_input")
        if st.button("Login", key="login_btn"):
            if username:
                st.session_state.user = username
                st.rerun()
            else:
                st.warning("Please enter a name to login.")
        st.stop()

# --- Market Snapshot Section ---
index_symbols = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "CRUDE OIL": "CL=F"
}

@st.cache_data(ttl=600)
def get_index_data():
    index_data = []
    for name, symbol in index_symbols.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            current = hist["Close"][-1]
            previous = hist["Close"][-2]
            day_change = ((current - previous) / previous) * 100
            week_change = ((hist["Close"][-1] - hist["Close"][-5]) / hist["Close"][-5]) * 100 if len(hist) >= 5 else 0
            month_change = ((hist["Close"][-1] - hist["Close"][0]) / hist["Close"][0]) * 100 if len(hist) > 0 else 0
            index_data.append({
                "Index": name,
                "Current Price": f"{current:.2f}",
                "Day Change (%)": f"{day_change:+.2f}%",
                "1-Week Change (%)": f"{week_change:+.2f}%",
                "1-Month Change (%)": f"{month_change:+.2f}%"
            })
        except Exception as e:
            st.warning(f"Could not load {name}: {e}")
    return index_data

st.subheader("🌐 Global & Commodity Market Snapshot")
st.dataframe(pd.DataFrame(get_index_data()).style.applymap(color_percent, subset=[
    "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
]), use_container_width=True)

# --- Watchlist Management ---
user = st.session_state.user
watchlist = get_watchlist(user)

st.subheader("📌 Add to Watchlist")
add_col1, add_col2 = st.columns([3, 1])
with add_col1:
    add_name = st.selectbox("Select stock to add", all_names, label_visibility="collapsed")
with add_col2:
    if st.button("➕ Add"):
        symbol = name_to_symbol[add_name]
        if symbol not in watchlist:
            add_to_watchlist(user, symbol)
            st.success(f"{add_name} added!")
            st.rerun()

st.subheader("📉 Your Watchlist")

if not watchlist:
    st.info("Your watchlist is empty.")
else:
    @st.cache_data(ttl=300)
    def get_watchlist_data(watchlist):
        data_rows = []
        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)
                hist_1mo = stock.history(period="1mo")
                hist_1wk = stock.history(period="7d")
                hist_1y = stock.history(period="1y")

                current_price = hist_1mo["Close"][-1]
                previous_close = hist_1mo["Close"][-2]
                day_change = ((current_price - previous_close) / previous_close) * 100
                week_change = ((hist_1wk["Close"][-1] - hist_1wk["Close"][0]) / hist_1wk["Close"][0]) * 100
                month_change = ((hist_1mo["Close"][-1] - hist_1mo["Close"][0]) / hist_1mo["Close"][0]) * 100

                high_52 = hist_1y["High"].max()
                low_52 = hist_1y["Low"].min()

                company = stock_dict.get(symbol, "Unknown")

                data_rows.append({
                    "Symbol": symbol,
                    "Company": company,
                    "Current Price": round(current_price, 2),
                    "Day Change (%)": f"{day_change:+.2f}%",
                    "1-Week Change (%)": f"{week_change:+.2f}%",
                    "1-Month Change (%)": f"{month_change:+.2f}%",
                    "52-Week High": f"{high_52:.2f}",
                    "52-Week Low": f"{low_52:.2f}",
                })
            except Exception as e:
                st.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame(data_rows)

    df = get_watchlist_data(watchlist)
    st.dataframe(df.style.applymap(color_percent, subset=[
        "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
    ]), use_container_width=True)

    # Action buttons for each stock
    st.subheader("Stock Actions")
    cols = st.columns(4)  # 4 columns for better mobile responsiveness
    
    for i, symbol in enumerate(watchlist):
        company = stock_dict.get(symbol, symbol)
        col = cols[i % 4]
        
        with col:
            st.markdown(f"**{company}**")
            
            # View Charts button
            st.markdown(
                f"<a class='view-charts' href='?stock={symbol}'>📊 View Charts</a>",
                unsafe_allow_html=True
            )
            
            # Remove button with confirmation
            if st.button(f"🗑️ Remove {company.split()[0]}", key=f"remove_{symbol}", 
                        help=f"Remove {company} from watchlist"):
                remove_from_watchlist(user, symbol)
                st.success(f"{company} removed from watchlist!")
                st.rerun()

    csv = df.to_csv(index=False)
    st.download_button("📥 Export to CSV", csv, file_name="watchlist.csv", mime="text/csv")

# --- Technical Analysis Section ---
if "stock" in st.query_params:
    selected_stock = st.query_params["stock"]
    company_name = stock_dict.get(selected_stock, selected_stock)
    
    st.subheader(f"📈 Technical Analysis: {company_name}")
    
    # Fetch detailed historical data
    @st.cache_data(ttl=300)
    def get_stock_history(symbol):
        stock = yf.Ticker(symbol)
        return stock.history(period="1y")
    
    hist = get_stock_history(selected_stock)
    
    # Create tabs for different analysis types
    ta_tab1, ta_tab2, ta_tab3, ta_tab4 = st.tabs(["Price Trend", "Moving Averages", "Volume Analysis", "Technical Indicators"])
    
    with ta_tab1:
        # Price Trend Chart
        fig = go.Figure()
        fig.add_trace(go.Candlestick(
            x=hist.index,
            open=hist['Open'],
            high=hist['High'],
            low=hist['Low'],
            close=hist['Close'],
            name='Candlesticks'
        ))
        fig.update_layout(
            title=f'{company_name} Price Trend',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            xaxis_rangeslider_visible=False,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with ta_tab2:
        # Moving Averages Chart
        hist['MA20'] = hist['Close'].rolling(window=20).mean()
        hist['MA50'] = hist['Close'].rolling(window=50).mean()
        hist['MA200'] = hist['Close'].rolling(window=200).mean()
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['Close'], 
            name='Close Price',
            line=dict(color='blue', width=1)
        ))
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['MA20'], 
            name='20-Day MA',
            line=dict(color='orange', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['MA50'], 
            name='50-Day MA',
            line=dict(color='green', width=2)
        ))
        fig.add_trace(go.Scatter(
            x=hist.index, 
            y=hist['MA200'], 
            name='200-Day MA',
            line=dict(color='purple', width=2)
        ))
        fig.update_layout(
            title=f'{company_name} Moving Averages',
            xaxis_title='Date',
            yaxis_title='Price (₹)',
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with ta_tab3:
        # Volume Analysis Chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=hist.index,
            y=hist['Volume'],
            name='Volume',
            marker_color='rgba(55, 128, 191, 0.7)'
        ))
        fig.add_trace(go.Scatter(
            x=hist.index,
            y=hist['Close'],
            name='Close Price',
            yaxis='y2',
            line=dict(color='orange', width=2)
        ))
        fig.update_layout(
            title=f'{company_name} Volume and Price Correlation',
            xaxis_title='Date',
            yaxis_title='Volume',
            yaxis2=dict(
                title='Price (₹)',
                overlaying='y',
                side='right'
            ),
            showlegend=True,
            height=600
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with ta_tab4:
        # Technical Indicators
        col1, col2 = st.columns(2)
        
        with col1:
            # RSI
            delta = hist['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            hist['RSI'] = 100 - (100 / (1 + rs))
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['RSI'], 
                name='RSI',
                line=dict(color='blue', width=2))
            )
            fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Overbought")
            fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Oversold")
            fig.update_layout(
                title='Relative Strength Index (14-day)',
                xaxis_title='Date',
                yaxis_title='RSI Value',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # MACD
            exp12 = hist['Close'].ewm(span=12, adjust=False).mean()
            exp26 = hist['Close'].ewm(span=26, adjust=False).mean()
            hist['MACD'] = exp12 - exp26
            hist['Signal'] = hist['MACD'].ewm(span=9, adjust=False).mean()
            hist['Histogram'] = hist['MACD'] - hist['Signal']
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['MACD'], 
                name='MACD',
                line=dict(color='blue', width=2))
            )
            fig.add_trace(go.Scatter(
                x=hist.index, 
                y=hist['Signal'], 
                name='Signal Line',
                line=dict(color='orange', width=2))
            )
            fig.add_trace(go.Bar(
                x=hist.index,
                y=hist['Histogram'],
                name='Histogram',
                marker_color=np.where(hist['Histogram'] < 0, 'red', 'green')
            ))
            fig.update_layout(
                title='Moving Average Convergence Divergence',
                xaxis_title='Date',
                yaxis_title='MACD Value',
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Add a back button
    if st.button("← Back to Watchlist"):
        st.query_params.clear()
        st.rerun()

# --- Footer ---
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