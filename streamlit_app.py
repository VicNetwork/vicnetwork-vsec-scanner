import streamlit as st
import requests
import pandas as pd
import time

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Stable VSEC Engine (Bybit Data Layer)")

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# -----------------------------
# BYBIT DATA FETCH (STABLE)
# -----------------------------
def get_data(symbol, interval="60", limit=200):
    """
    Bybit v5 public kline endpoint
    interval:
    60 = 1H
    240 = 4H
    D = 1D
    """

    url = "https://api.bybit.com/v5/market/kline"

    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()

        if "result" not in data or "list" not in data["result"]:
            return None

        klines = data["result"]["list"]

        if len(klines) < 50:
            return None

        df = pd.DataFrame(klines, columns=[
            "time","open","high","low","close","volume","turnover"
        ])

        df = df[["open","high","low","close"]].astype(float)

        return df

    except Exception:
        return None


# -----------------------------
# CHOCH ENGINE (UNCHANGED LOGIC)
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
# SCANNER ENGINE
# -----------------------------
results = []

for symbol in symbols:

    # Bybit timeframes
    h4 = get_data(symbol, "240")
    h1 = get_data(symbol, "60")
    d1 = get_data(symbol, "D")

    h4_signal = choch(h4)
    h1_signal = choch(h1)
    d1_signal = choch(d1)

    # -----------------------------
    # SIMPLE VSEC ALIGNMENT LOGIC
    # -----------------------------
    if d1_signal == "BULLISH CHOCH" and h4_signal == "BULLISH CHOCH":
        status = "BULLISH STRUCTURE ALIGNMENT"
    elif d1_signal == "BEARISH CHOCH" and h4_signal == "BEARISH CHOCH":
        status = "BEARISH STRUCTURE ALIGNMENT"
    elif h4_signal != "NO DATA":
        status = "WAIT CONFIRMATION"
    else:
        status = "NO STRUCTURE DATA"

    results.append([
        symbol,
        d1_signal,
        h4_signal,
        h1_signal,
        status
    ])

    time.sleep(0.2)


# -----------------------------
# OUTPUT
# -----------------------------
df_out = pd.DataFrame(results, columns=[
    "PAIR", "DAILY", "4H", "1H", "VSEC STATUS"
])

st.dataframe(df_out, use_container_width=True)
