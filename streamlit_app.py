import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Stable Production VSEC Engine (Cloud Safe)")

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# -----------------------------
# SAFE REQUEST (CRITICAL FIX)
# -----------------------------
def fetch(symbol, interval="1d", limit=200):

    url = "https://api.binance.com/api/v3/klines"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        r = requests.get(url, params=params, headers=headers, timeout=10)

        # HARD VALIDATION
        if r.status_code != 200:
            return None

        data = r.json()

        if not isinstance(data, list):
            return None

        if len(data) < 100:
            return None

        df = pd.DataFrame(data, columns=[
            "time","open","high","low","close","volume",
            "_1","_2","_3","_4","_5","_6"
        ])

        df = df[["open","high","low","close"]].astype(float)

        return df

    except Exception:
        return None


# -----------------------------
# CHOCH ENGINE
# -----------------------------
def choch(df):
    if df is None or len(df) < 50:
        return "NO DATA"

    zone = df.iloc[-80:-20]

    swing_high = zone["high"].max()
    swing_low = zone["low"].min()

    close = df["close"].iloc[-1]

    if close > swing_high:
        return "BULLISH CHOCH"
    elif close < swing_low:
        return "BEARISH CHOCH"
    else:
        return "NO CHOCH"


# -----------------------------
# SCANNER (WITH DELAY SAFETY)
# -----------------------------
results = []

for symbol in symbols:

    df = fetch(symbol)

    signal = choch(df)

    results.append([symbol, signal])

    time.sleep(0.5)  # prevents rate blocking


# -----------------------------
# OUTPUT
# -----------------------------
df_out = pd.DataFrame(results, columns=["PAIR", "VSEC SIGNAL"])

st.dataframe(df_out, use_container_width=True)
