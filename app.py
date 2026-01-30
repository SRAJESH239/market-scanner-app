import streamlit as st
import pandas as pd
import requests
import database as db
import scanner as scan

# --- TELEGRAM CONFIG ---
# Load secrets from Streamlit
try:
    TOKEN = st.secrets["TELEGRAM_TOKEN"]
    CHAT_ID = st.secrets["TELEGRAM_CHAT_ID"]
except:
    st.error("❌ Error: Telegram Secrets not found. Please add them in App Settings.")
    st.stop()

def send_telegram_msg(message):
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": message})

# --- APP CONFIG ---
st.set_page_config(page_title="Stock Sniper Pro", page_icon="📈", layout="wide")
st.title("📈 Stock Sniper Command Center")

# --- SIDEBAR (CONTROLS) ---
with st.sidebar:
    st.header("⚙️ Scanner Controls")
    scan_limit = st.slider("Stocks to Scan", 50, 3000, 200) # Slider for speed
    st.info("Set to 3000 for full market scan (Takes ~5 mins)")

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs(["🚀 Golden Stocks", "⚓ Bottom Fish", "NIFTY50 OPTIMISED ", "📜 History DB"])

# --- TAB 1: GOLDEN STOCKS ---
with tab1:
    st.header("Breakout Candidates")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔎 Scan Golden Stocks"):
            with st.spinner("Scanning Market... Please wait..."):
                df_gold = scan.run_scan("GOLDEN", limit=scan_limit)
                st.session_state['gold_data'] = df_gold # Save to session
            st.success(f"Scan Complete! Found {len(df_gold)}")

    # Display Data if available
    if 'gold_data' in st.session_state:
        df = st.session_state['gold_data']
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # CONFIRMATION BUTTONS
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Save to Database", key="save_gold"):
                    db.save_scan(df, "Golden")
                    st.toast("Saved to History!")
            with c2:
                if st.button("✈️ Send to Telegram", key="send_gold"):
                    msg = f"🚀 **Golden Stocks Report**\nFound {len(df)} Stocks.\nTop: {df.iloc[0]['Stock']}"
                    send_telegram_msg(msg)
                    st.toast("Sent to Telegram!")
        else:
            st.warning("No stocks found matching criteria.")

# --- TAB 2: BOTTOM FISH ---
with tab2:
    st.header("Support/Value Candidates")
    
    if st.button("🔎 Scan Bottom Stocks"):
        with st.spinner("Scanning Deep Value..."):
            df_bot = scan.run_scan("BOTTOM", limit=scan_limit)
            st.session_state['bot_data'] = df_bot
        st.success(f"Scan Complete! Found {len(df_bot)}")

    if 'bot_data' in st.session_state:
        df = st.session_state['bot_data']
        if not df.empty:
            st.dataframe(df, use_container_width=True)
            
            # ACTIONS
            c1, c2 = st.columns(2)
            with c1:
                if st.button("💾 Save to Database", key="save_bot"):
                    db.save_scan(df, "Bottom")
                    st.toast("Saved to History!")
            with c2:
                if st.button("✈️ Send to Telegram", key="send_bot"):
                    msg = f"⚓ **Bottom Fish Report**\nFound {len(df)} Stocks.\nTop: {df.iloc[0]['Stock']}"
                    send_telegram_msg(msg)
                    st.toast("Sent to Telegram!")
        else:
            st.warning("No stocks found.")

# --- TAB 3: HISTORY DATABASE ---
with tab3:
    st.header("📜 Past Performance")
    if st.button("🔄 Refresh History"):
        st.rerun()
        
    df_hist = db.get_history()
    if not df_hist.empty:
        st.dataframe(df_hist, use_container_width=True)
    else:

        st.info("Database is empty. Run a scan and save results!")


with tab4:
    break
    




