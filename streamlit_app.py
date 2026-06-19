import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Live Market Structure Scanner (Stable Version)")

# -----------------------------
# WATCHLIST (start small, scale later)
# -----------------------------
symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT"
]

# -----------------------------
# GET BINANCE DATA (SAFE VERSION)
# -----------------------------
def get_data(symbol, interval="4h", limit=100):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        response = requests.get(url, params=params, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        df = pd.DataFrame(data, columns=[
            "time", "open", "high", "low", "close", "volume",
            "_1", "_2", "_3", "_4", "_5", "_6"
        ])

        df = df[["open", "high", "low", "close"]].astype(float)

        return df

    except Exception:
        return None


# -----------------------------
# SIMPLE CHOCH LOGIC (MVP)
# -----------------------------
def detect_choch(df):
    if df is None or len(df) < 20:
        return "NO DATA"

    recent_high = df["high"].iloc[-20:].max()
    recent_low = df["low"].iloc[-20:].min()
    last_close = df["close"].iloc[-1]

    if last_close > recent_high:
        return "BULLISH CHOCH"
    elif last_close < recent_low:
        return "BEARISH CHOCH"
    else:
        return "NO CHOCH"


# -----------------------------
# SCANNER ENGINE
# -----------------------------
results = []

for symbol in symbols:
    df = get_data(symbol)

    signal = detect_choch(df)

    results.append([symbol, signal])


# -----------------------------
# DISPLAY DASHBOARD
# -----------------------------
st.subheader("Market Structure Results")

table = pd.DataFrame(results, columns=["PAIR", "VSEC SIGNAL"])

st.dataframe(table, use_container_width=True)
