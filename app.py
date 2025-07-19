import streamlit as st
import yfinance as yf
from datetime import datetime
from supabase_helper import add_to_watchlist, get_watchlist, remove_from_watchlist
import pandas as pd
from streamlit_autorefresh import st_autorefresh

st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")
st_autorefresh(interval=600000, key="datarefresh")  # 10 minutes
st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")

# Show company logo at the top
# st.image("logo.jpg", width=180)
st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")

# Logo at top-left
st.markdown(
    """
    <div style='display: flex; align-items: center; justify-content: flex-start;'>
        <img src='logo.jpg' width='140' style='margin-right: 10px;' />
    </div>
    """,
    unsafe_allow_html=True
)

st.title("📈 NSE Stock Watchlist")

# --- Simple Login ---
if "user" not in st.session_state:
    username = st.text_input("Enter your name to continue:")
    if st.button("Login"):
        if username:
            st.session_state.user = username
            st.rerun()
        else:
            st.warning("Please enter a name to login.")
else:
    user = st.session_state.user
    st.success(f"Logged in as: {user}")
    st.button("Logout", on_click=lambda: st.session_state.clear())

    # --- Watchlist Management ---
    stock_dict = {
        "TCS.NS": "TATA CONSULTANCY SERVICES",
        "INFY.NS": "INFOSYS",
        "WIPRO.NS": "WIPRO",
        "HCLTECH.NS": "HCL TECHNOLOGIES",
        "RELIANCE.NS": "RELIANCE INDUSTRIES",
        "SBIN.NS": "STATE BANK OF INDIA",
        "ICICIBANK.NS": "ICICI BANK",
        "TECHM.NS": "TECH MAHINDRA"
    }

    name_to_symbol = {v: k for k, v in stock_dict.items()}
    all_names = list(name_to_symbol.keys())

    watchlist = get_watchlist(user)

    st.subheader("📌 Add to Watchlist")
    add_name = st.selectbox("Select stock to add", all_names)
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
        data_rows = []

        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)

                # Historical prices
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
                    "Day Change (%)": round(day_change, 2),
                    "1-Week Change (%)": round(week_change, 2),
                    "1-Month Change (%)": round(month_change, 2),
                    "52-Week High": round(high_52, 2),
                    "52-Week Low": round(low_52, 2)
                })

            except Exception as e:
                st.error(f"Error fetching {symbol}: {e}")

        df = pd.DataFrame(data_rows)

        # Display table with color formatting
        def color_negative_red(val):
            if isinstance(val, (float, int)):
                color = 'red' if val < 0 else 'green'
                return f'color: {color}'
            return ''

        st.dataframe(df.style.applymap(color_negative_red, subset=[
            "Day Change (%)", "1-Week Change (%)", "1-Month Change (%)"
        ]), use_container_width=True)

        # Download button
        csv = df.to_csv(index=False)
        st.download_button("📥 Export to CSV", csv, file_name="watchlist.csv", mime="text/csv")

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
