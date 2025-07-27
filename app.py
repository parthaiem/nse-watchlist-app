import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objs as go
from datetime import datetime

# Custom CSS for styling
st.markdown("""
    <style>
        .market-snapshot {
            display: flex;
            overflow-x: auto;
            gap: 15px;
            padding: 10px 0;
            margin-bottom: 20px;
        }
        .index-card {
            min-width: 180px;
            border: 1px solid #e0e0e0;
            border-radius: 8px;
            padding: 12px;
            text-align: center;
        }
        .positive {
            color: green;
        }
        .negative {
            color: red;
        }
        .index-name {
            font-weight: bold;
            margin-bottom: 5px;
        }
        .index-price {
            font-size: 1.2rem;
            margin: 5px 0;
        }
        .index-change {
            font-size: 0.9rem;
        }
    </style>
""", unsafe_allow_html=True)

# Market indices to display
market_indices = {
    "NIFTY 50": "^NSEI",
    "SENSEX": "^BSESN",
    "NASDAQ": "^IXIC",
    "DOW JONES": "^DJI",
    "GOLD": "GC=F",
    "SILVER": "SI=F",
    "CRUDE OIL": "CL=F"
}

@st.cache_data(ttl=600)  # Cache for 10 minutes
def get_index_data():
    index_data = {}
    for name, symbol in market_indices.items():
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1d")
            
            if len(hist) > 0:
                current = hist["Close"][-1]
                prev_close = hist["Close"][0] if len(hist) > 1 else current
                change = ((current - prev_close) / prev_close) * 100
                
                index_data[name] = {
                    "price": current,
                    "change": change,
                    "symbol": symbol
                }
        except Exception as e:
            st.error(f"Error fetching {name}: {e}")
    return index_data

# Display market snapshot
st.subheader("🌐 Global & Commodity Market Snapshot")
index_data = get_index_data()

# Create a horizontal scrollable container
st.markdown('<div class="market-snapshot">', unsafe_allow_html=True)

for name, data in index_data.items():
    change = data["change"]
    change_class = "positive" if change >= 0 else "negative"
    change_arrow = "▲" if change >= 0 else "▼"
    
    st.markdown(f"""
        <div class="index-card">
            <div class="index-name">{name}</div>
            <div class="index-price">{data['price']:.2f}</div>
            <div class="index-change {change_class}">
                {change_arrow} {abs(change):.2f}%
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Rest of your app code...
# [Include the rest of your existing code here]