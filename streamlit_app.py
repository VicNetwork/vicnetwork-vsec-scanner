import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Live Market Structure Scanner (Stable V1)")

# -----------------------------
# WATCHLIST (expand later to 100+)
# -----------------------------
symbols = [
    "BTCUSDT",
    "ETHUSDT",
    "BNBUSDT"
]

# -----------------------------
# FETCH BINANCE DATA
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
# VSEC CHOCH LOGIC (IMPROVED STABLE VERSION)
# -----------------------------
def detect_choch(df):
    if df is None or len(df) < 40:
        return "NO DATA"

    # Previous structure zone (exclude recent candles to avoid noise)
    structure_window = df.iloc[-40:-10]

    swing_high = structure_window["high"].max()
    swing_low = structure_window["low"].min()

    last_close = df["close"].iloc[-1]

    # Break of structure logic
    if last_close > swing_high:
        return "BULLISH CHOCH"
    elif last_close < swing_low:
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
# DISPLAY TABLE
# -----------------------------
st.subheader("Market Structure Results")

table = pd.DataFrame(results, columns=["PAIR", "VSEC SIGNAL"])

st.dataframe(table, use_container_width=True)
