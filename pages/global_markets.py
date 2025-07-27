import streamlit as st
import yfinance as yf
import pandas as pd
from datetime import datetime
from supabase_helper import get_watchlist  # Only if you need watchlist functionality

# Initialize session states (if needed)
if 'watchlist' not in st.session_state:
    st.session_state.watchlist = []

# Common header function
def show_header():
    # --- Top bar layout ---
    top_col1, top_col2, top_col3 = st.columns([1, 4, 2])

    with top_col1:
        st.image("logo.jpg", width=100)

    with top_col2:
        st.markdown("<h1 style='padding-top: 10px;'>🌍 Global Market Dashboard</h1>", unsafe_allow_html=True)

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

# Function to style percentage changes
def color_percent(val):
    try:
        val_float = float(val.strip('%+'))
        color = 'green' if val_float >= 0 else 'red'
        return f'color: {color}; font-weight: bold;'
    except:
        return ''

# Function to style prices
def color_price(val):
    try:
        val_float = float(val)
        return 'font-weight: bold;'
    except:
        return ''

# Function to get market data
def get_market_data():
    # Major Global Indices with country flags and full names
    global_indices = {
        "🇮🇳 NIFTY 50 (India)": "^NSEI",
        "🇮🇳 SENSEX (India)": "^BSESN",
        "🇮🇳 NIFTY BANK (India)": "^NSEBANK",
        "🇺🇸 NASDAQ (United States)": "^IXIC",
        "🇺🇸 S&P 500 (United States)": "^GSPC",
        "🇺🇸 DOW JONES (United States)": "^DJI",
        "🇬🇧 FTSE 100 (United Kingdom)": "^FTSE",
        "🇩🇪 DAX (Germany)": "^GDAXI",
        "🇫🇷 CAC 40 (France)": "^FCHI",
        "🇯🇵 NIKKEI 225 (Japan)": "^N225",
        "🇭🇰 HANG SENG (Hong Kong)": "^HSI",
        "🇨🇳 SHANGHAI COMP (China)": "000001.SS",
        "🇦🇺 ASX 200 (Australia)": "^AXJO",
        "🇨🇦 S&P/TSX (Canada)": "^GSPTSE",
        "🇧🇷 BOVESPA (Brazil)": "^BVSP",
        "🇷🇺 MOEX (Russia)": "IMOEX.ME",
        "🇿🇦 JSE TOP 40 (South Africa)": "^JN0U.JO"
    }

    # Commodities with more details
    commodities = {
        "🟡 GOLD (COMEX)": "GC=F",
        "⚪ SILVER (COMEX)": "SI=F",
        "🛢️ CRUDE OIL (WTI)": "CL=F",
        "🛢️ BRENT CRUDE": "BZ=F",
        "💨 NATURAL GAS": "NG=F",
        "🟠 COPPER": "HG=F",
        "🌾 WHEAT": "KE=F",
        "🌽 CORN": "ZC=F",
        "🌰 SOYBEANS": "ZS=F",
        "☕ COFFEE": "KC=F",
        "🍫 COCOA": "CC=F",
        "🍭 SUGAR": "SB=F"
    }

    # Indian Sectoral Indices with more sectors
    indian_sectors = {
        "💻 NIFTY IT": "^CNXIT",
        "🚗 NIFTY AUTO": "^CNXAUTO",
        "🏦 NIFTY BANK": "^CNXBANK",
        "💰 NIFTY FIN SERVICE": "^CNXFIN",
        "🛒 NIFTY FMCG": "^CNXFMCG",
        "🎬 NIFTY MEDIA": "^CNXMEDIA",
        "🏗️ NIFTY METAL": "^CNXMETAL",
        "💊 NIFTY PHARMA": "^CNXPHARMA",
        "🏛️ NIFTY PSU BANK": "^CNXPSUBANK",
        "🏢 NIFTY REALTY": "^CNXREALTY",
        "⚡ NIFTY ENERGY": "^CNXENERGY",
        "🛍️ NIFTY CONSUMPTION": "^CNXCONSUM",
        "🏥 NIFTY HEALTHCARE": "^CNXHEALTH",
        "🏭 NIFTY INFRA": "^CNXINFRA",
        "🛠️ NIFTY MNC": "^CNXMNC"
    }

    # Cryptocurrencies with more coins
    cryptocurrencies = {
        "₿ BITCOIN": "BTC-USD",
        "Ξ ETHEREUM": "ETH-USD",
        "🅱️ BNB": "BNB-USD",
        "✕ XRP": "XRP-USD",
        "◎ SOLANA": "SOL-USD",
        "◉ CARDANO": "ADA-USD",
        "🅰️ AVAX": "AVAX-USD",
        "◈ POLKADOT": "DOT-USD",
        "🅿️ POLYGON": "MATIC-USD",
        "🅳 DOGECOIN": "DOGE-USD"
    }

    # Currency pairs
    currencies = {
        "💵 USD/INR": "INR=X",
        "💶 EUR/INR": "EURINR=X",
        "💷 GBP/INR": "GBPINR=X",
        "💴 JPY/INR": "JPYINR=X",
        "🇺🇸 USD/EUR": "EURUSD=X",
        "🇺🇸 USD/GBP": "GBPUSD=X",
        "🇺🇸 USD/JPY": "JPY=X"
    }

    # Get all data
    all_data = []
    
    def fetch_data(category, items):
        for name, symbol in items.items():
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period="1d")
                if not hist.empty:
                    current = hist["Close"][-1]
                    previous = hist["Open"][0]
                    change = ((current - previous) / previous) * 100
                    
                    # Additional metrics for some categories
                    if category == "Global Indices":
                        day_range = f"{hist['Low'][-1]:.2f}-{hist['High'][-1]:.2f}"
                        year_range = f"{hist['Low'].min():.2f}-{hist['High'].max():.2f}"
                    else:
                        day_range = year_range = ""
                        
                    all_data.append({
                        "Category": category,
                        "Name": name,
                        "Symbol": symbol,
                        "Price": current,
                        "Change (%)": change,
                        "Day Range": day_range,
                        "52W Range": year_range,
                        "Volume": hist["Volume"][-1] if "Volume" in hist.columns else "",
                        "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
            except Exception as e:
                st.warning(f"Could not load {name}: {e}")

    # Fetch all categories
    fetch_data("Global Indices", global_indices)
    fetch_data("Commodities", commodities)
    fetch_data("Indian Sectors", indian_sectors)
    fetch_data("Cryptocurrencies", cryptocurrencies)
    fetch_data("Currencies", currencies)

    return pd.DataFrame(all_data)

# Function to create metric cards
def create_metric_card(title, value, change, delta_color="normal"):
    st.metric(
        label=title,
        value=value,
        delta=f"{change:.2f}%" if not pd.isna(change) else "N/A",
        delta_color=delta_color
    )

# Main page function
def main():
    st.set_page_config(page_title="Global Market Dashboard", layout="wide")
    
    # Show header
    show_header()
    
    # Custom CSS
    st.markdown("""
    <style>
        .big-font {
            font-size:18px !important;
        }
        .metric-box {
            border: 1px solid #ccc;
            border-radius: 5px;
            padding: 10px;
            margin: 5px 0;
            background-color: #f9f9f9;
        }
        .dataframe th, .dataframe td {
            white-space: nowrap;
        }
        .highlight-green {
            background-color: #e6f7e6;
        }
        .highlight-red {
            background-color: #ffebee;
        }
        .country-flag {
            font-size: 1.5em;
            margin-right: 5px;
        }
        .stTabs [data-baseweb="tab-list"] {
            gap: 10px;
        }
        .stTabs [data-baseweb="tab"] {
            padding: 8px 16px;
            border-radius: 4px 4px 0 0;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Current time
    st.markdown(f"<div class='big-font'>Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</div>", 
               unsafe_allow_html=True)
    
    # Get market data
    with st.spinner("Loading market data..."):
        market_data = get_market_data()
    
    # Top Performers Section
    st.subheader("🏆 Top Performers Today")
    top_performers = market_data.sort_values("Change (%)", ascending=False).head(5)
    bottom_performers = market_data.sort_values("Change (%)").head(5)
    
    cols = st.columns(5)
    for i, (_, row) in enumerate(top_performers.iterrows()):
        with cols[i]:
            create_metric_card(
                row["Name"].split("(")[0].strip(),
                f"{row['Price']:,.2f}",
                row["Change (%)"],
                "normal" if row["Change (%)"] >= 0 else "inverse"
            )
    
    st.subheader("📉 Worst Performers Today")
    cols = st.columns(5)
    for i, (_, row) in enumerate(bottom_performers.iterrows()):
        with cols[i]:
            create_metric_card(
                row["Name"].split("(")[0].strip(),
                f"{row['Price']:,.2f}",
                row["Change (%)"],
                "normal" if row["Change (%)"] >= 0 else "inverse"
            )
    
    # Display data in tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌐 Global Indices", 
        "🛢️ Commodities", 
        "🇮🇳 Indian Sectors", 
        "₿ Cryptocurrencies",
        "💱 Currencies"
    ])
    
    with tab1:
        st.subheader("🌐 Global Market Indices")
        global_data = market_data[market_data["Category"] == "Global Indices"].copy()
        
        # Add country flag styling
        def style_country_name(val):
            flag = val.split()[0]
            name = " ".join(val.split()[1:])
            return f'<span class="country-flag">{flag}</span> {name}'
        
        global_data["Styled Name"] = global_data["Name"].apply(style_country_name)
        
        st.dataframe(
            global_data.style.format({
                "Price": "{:,.2f}",
                "Change (%)": "{:+.2f}%",
                "Day Range": "{:,.2f}-{:,.2f}",
                "52W Range": "{:,.2f}-{:,.2f}",
                "Volume": "{:,.0f}"
            })
            .applymap(color_percent, subset=["Change (%)"])
            .applymap(color_price, subset=["Price", "Day Range", "52W Range"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Symbol": None,
                "Name": None,
                "Styled Name": st.column_config.TextColumn("Index", width="large"),
                "Price": st.column_config.NumberColumn("Price", format="%.2f"),
                "Change (%)": st.column_config.TextColumn("Change"),
                "Day Range": st.column_config.TextColumn("Day Range"),
                "52W Range": st.column_config.TextColumn("52W Range"),
                "Volume": st.column_config.NumberColumn("Volume", format="%.0f"),
                "Last Updated": st.column_config.DatetimeColumn("Updated")
            },
            column_order=["Styled Name", "Price", "Change (%)", "Day Range", "52W Range", "Volume", "Last Updated"]
        )
    
    with tab2:
        st.subheader("🛢️ Commodities Market")
        commodities_data = market_data[market_data["Category"] == "Commodities"].copy()
        
        st.dataframe(
            commodities_data.style.format({
                "Price": "{:,.2f}",
                "Change (%)": "{:+.2f}%",
                "Day Range": "{:,.2f}-{:,.2f}",
                "52W Range": "{:,.2f}-{:,.2f}"
            })
            .applymap(color_percent, subset=["Change (%)"])
            .applymap(color_price, subset=["Price", "Day Range", "52W Range"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Symbol": None,
                "Name": st.column_config.TextColumn("Commodity", width="medium"),
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Change (%)": st.column_config.TextColumn("Change"),
                "Day Range": st.column_config.TextColumn("Day Range"),
                "52W Range": st.column_config.TextColumn("52W Range"),
                "Last Updated": st.column_config.DatetimeColumn("Updated")
            }
        )
    
    with tab3:
        st.subheader("🇮🇳 Indian Sectoral Indices")
        sectors_data = market_data[market_data["Category"] == "Indian Sectors"].copy()
        
        st.dataframe(
            sectors_data.style.format({
                "Price": "{:,.2f}",
                "Change (%)": "{:+.2f}%",
                "Day Range": "{:,.2f}-{:,.2f}",
                "52W Range": "{:,.2f}-{:,.2f}"
            })
            .applymap(color_percent, subset=["Change (%)"])
            .applymap(color_price, subset=["Price", "Day Range", "52W Range"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Symbol": None,
                "Name": st.column_config.TextColumn("Sector", width="medium"),
                "Price": st.column_config.NumberColumn("Price", format="₹%.2f"),
                "Change (%)": st.column_config.TextColumn("Change"),
                "Day Range": st.column_config.TextColumn("Day Range"),
                "52W Range": st.column_config.TextColumn("52W Range"),
                "Last Updated": st.column_config.DatetimeColumn("Updated")
            }
        )
    
    with tab4:
        st.subheader("₿ Cryptocurrencies")
        crypto_data = market_data[market_data["Category"] == "Cryptocurrencies"].copy()
        
        st.dataframe(
            crypto_data.style.format({
                "Price": "{:,.2f}",
                "Change (%)": "{:+.2f}%",
                "Day Range": "{:,.2f}-{:,.2f}",
                "52W Range": "{:,.2f}-{:,.2f}"
            })
            .applymap(color_percent, subset=["Change (%)"])
            .applymap(color_price, subset=["Price", "Day Range", "52W Range"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Symbol": None,
                "Name": st.column_config.TextColumn("Crypto", width="medium"),
                "Price": st.column_config.NumberColumn("Price", format="$%.2f"),
                "Change (%)": st.column_config.TextColumn("Change"),
                "Day Range": st.column_config.TextColumn("Day Range"),
                "52W Range": st.column_config.TextColumn("52W Range"),
                "Last Updated": st.column_config.DatetimeColumn("Updated")
            }
        )
    
    with tab5:
        st.subheader("💱 Currency Pairs")
        currency_data = market_data[market_data["Category"] == "Currencies"].copy()
        
        st.dataframe(
            currency_data.style.format({
                "Price": "{:,.4f}",
                "Change (%)": "{:+.2f}%",
                "Day Range": "{:,.4f}-{:,.4f}",
                "52W Range": "{:,.4f}-{:,.4f}"
            })
            .applymap(color_percent, subset=["Change (%)"])
            .applymap(color_price, subset=["Price", "Day Range", "52W Range"]),
            use_container_width=True,
            hide_index=True,
            column_config={
                "Category": None,
                "Symbol": None,
                "Name": st.column_config.TextColumn("Currency Pair", width="medium"),
                "Price": st.column_config.NumberColumn("Price", format="%.4f"),
                "Change (%)": st.column_config.TextColumn("Change"),
                "Day Range": st.column_config.TextColumn("Day Range"),
                "52W Range": st.column_config.TextColumn("52W Range"),
                "Last Updated": st.column_config.DatetimeColumn("Updated")
            }
        )
    
    # Market Summary
    st.markdown("---")
    st.subheader("📊 Market Summary")
    
    summary_col1, summary_col2, summary_col3 = st.columns(3)
    
    with summary_col1:
        st.markdown("**🔺 Top Gainers**")
        top_gainers = market_data[market_data["Change (%)"] > 0].sort_values("Change (%)", ascending=False).head(3)
        for _, row in top_gainers.iterrows():
            st.markdown(f"""
            <div class="metric-box highlight-green">
                <strong>{row['Name'].split('(')[0].strip()}</strong><br>
                Price: {row['Price']:,.2f}<br>
                Change: <span style="color: green;">+{row['Change (%)']:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with summary_col2:
        st.markdown("**🔻 Top Losers**")
        top_losers = market_data[market_data["Change (%)"] < 0].sort_values("Change (%)").head(3)
        for _, row in top_losers.iterrows():
            st.markdown(f"""
            <div class="metric-box highlight-red">
                <strong>{row['Name'].split('(')[0].strip()}</strong><br>
                Price: {row['Price']:,.2f}<br>
                Change: <span style="color: red;">{row['Change (%)']:.2f}%</span>
            </div>
            """, unsafe_allow_html=True)
    
    with summary_col3:
        st.markdown("**📈 Most Active**")
        most_active = market_data.sort_values("Volume", ascending=False).head(3)
        for _, row in most_active.iterrows():
            st.markdown(f"""
            <div class="metric-box">
                <strong>{row['Name'].split('(')[0].strip()}</strong><br>
                Price: {row['Price']:,.2f}<br>
                Volume: {row['Volume']:,.0f}
            </div>
            """, unsafe_allow_html=True)
    
    # Show footer
    show_footer()

if __name__ == "__main__":
    main()