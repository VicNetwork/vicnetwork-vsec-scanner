import streamlit as st
import ccxt
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Live Market Structure Scanner (CHOCH + BOS)")

# -------------------------
# Exchange Setup
# -------------------------
exchange = ccxt.binance()

# 100+ coins scan list (you can expand later)
symbols = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT",
    "XRP/USDT", "ADA/USDT", "DOGE/USDT", "MATIC/USDT",
    "AVAX/USDT", "DOT/USDT"
]

timeframe = "4h"

# -------------------------
# Get candles
# -------------------------
def get_data(symbol):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe, limit=100)
    df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
    return df

# -------------------------
# Simple structure logic (MVP CHOCH/BOS)
# -------------------------
def detect_structure(df):
    highs = df["high"]
    lows = df["low"]

    recent_high = highs.iloc[-10:].max()
    recent_low = lows.iloc[-10:].min()

    last_close = df["close"].iloc[-1]

    choch_bull = last_close > recent_high
    choch_bear = last_close < recent_low

    return choch_bull, choch_bear

# -------------------------
# Scanner
# -------------------------
results = []

for symbol in symbols:
    df = get_data(symbol)

    bull, bear = detect_structure(df)

    if bull:
        status = "BULLISH CHOCH"
    elif bear:
        status = "BEARISH CHOCH"
    else:
        status = "NO CHOCH"

    results.append([symbol, status])

# -------------------------
# Display
# -------------------------
table = pd.DataFrame(results, columns=["PAIR", "VSEC SIGNAL"])

st.dataframe(table, use_container_width=True)
