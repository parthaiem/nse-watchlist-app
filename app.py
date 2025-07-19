import streamlit as st
import yfinance as yf
from datetime import datetime, timedelta
from supabase_helper import sign_in, sign_up, add_to_watchlist, get_watchlist, remove_from_watchlist

st.set_page_config(page_title="NSE Stock Watchlist", layout="wide")

st.title("📈 NSE Stock Watchlist")

# --- Auth Section ---
if "user" not in st.session_state:
    tab1, tab2 = st.tabs(["🔐 Login", "🆕 Sign Up"])

    with tab1:
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            res = sign_in(email, password)
            if res.user:
                st.session_state.user = res.user
                st.rerun()
            else:
                st.error("Login failed")

    with tab2:
        email = st.text_input("Email", key="signup_email")
        password = st.text_input("Password", type="password", key="signup_pw")
        if st.button("Sign Up"):
            res = sign_up(email, password)
            if res.user:
                st.success("Account created. Please log in.")
                st.experimental_rerun()
            else:
                st.error("Signup failed")

else:
    user = st.session_state.user
    st.success(f"Logged in as: {user.email}")
    st.button("Logout", on_click=lambda: st.session_state.clear())

    # --- Watchlist Management ---
    stock_dict = {
        "TCS.NS": "Tata Consultancy Services",
        "INFY.NS": "Infosys",
        "WIPRO.NS": "Wipro",
        "HCLTECH.NS": "HCL Technologies",
        "RELIANCE.NS": "Reliance Industries",
        "SBIN.NS": "State Bank of India",
        "ICICIBANK.NS": "ICICI Bank"
    }

    name_to_symbol = {v: k for k, v in stock_dict.items()}
    all_names = list(name_to_symbol.keys())

    watchlist = get_watchlist(user.id)

    st.subheader("📌 Add to Watchlist")
    add_name = st.selectbox("Select stock to add", all_names)
    if st.button("➕ Add"):
        symbol = name_to_symbol[add_name]
        if symbol not in watchlist:
            add_to_watchlist(user.id, symbol)
            st.success(f"{add_name} added!")
            st.rerun()

    st.subheader("📉 Your Watchlist")
    if not watchlist:
        st.info("Your watchlist is empty.")
    else:
        today = datetime.today()
        for symbol in watchlist:
            try:
                stock = yf.Ticker(symbol)
                hist = stock.history(period="1mo")

                current_price = hist["Close"][-1]
                previous_close = hist["Close"][-2]
                change = ((current_price - previous_close) / previous_close) * 100
                high_52 = stock.history(period="1y")["High"].max()
                low_52 = stock.history(period="1y")["Low"].min()

                col1, col2, col3, col4, col5 = st.columns(5)
                col1.markdown(f"**{symbol}**")
                col2.markdown(f"💰 ₹{round(current_price,2)}")
                col3.markdown(f"<span style='color: {'green' if change > 0 else 'red'};'>{round(change,2)}%</span>", unsafe_allow_html=True)
                col4.markdown(f"📈 High: ₹{round(high_52,2)}📉 Low: ₹{round(low_52,2)}")

                if col5.button("❌ Remove", key=symbol):
                    remove_from_watchlist(user.id, symbol)
                    st.rerun()

            except Exception as e:
                st.error(f"Error fetching {symbol}: {e}")

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
