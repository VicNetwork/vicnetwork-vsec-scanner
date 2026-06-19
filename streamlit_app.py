import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Stable Multi-Timeframe VSEC Engine (Correct Data Layer)")

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# -----------------------------
# BINANCE DATA (CORRECT WAY)
# -----------------------------
def get_data(symbol, interval, limit=100):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": limit
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()

        if not isinstance(data, list) or len(data) < 50:
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
# CHOCH LOGIC (YOUR STRUCTURE IDEA)
# -----------------------------
def choch(df):
    if df is None:
        return "NO DATA"

    if len(df) < 40:
        return "NO DATA"

    zone = df.iloc[-60:-15]

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
# ENGINE
# -----------------------------
results = []

for symbol in symbols:

    # REAL MULTI-TIMEFRAME DATA (NO RESAMPLE)
    weekly = get_data(symbol, "1w", 100)
    monthly = get_data(symbol, "1M", 100)
    daily = get_data(symbol, "1d", 100)
    h4 = get_data(symbol, "4h", 100)

    weekly_signal = choch(weekly)
    monthly_signal = choch(monthly)
    daily_signal = choch(daily)
    h4_signal = choch(h4)

    # VSEC LOGIC (UNCHANGED STRUCTURE)
    if weekly_signal == "BULLISH CHOCH" and monthly_signal == "BULLISH CHOCH":
        if h4_signal == "BULLISH CHOCH":
            if daily_signal == "BULLISH CHOCH":
                status = "REVERSAL BUY READY"
            else:
                status = "WAIT DAILY CONFIRMATION"
        else:
            status = "WAIT 4H EXECUTION"

    elif weekly_signal == "BEARISH CHOCH" and monthly_signal == "BEARISH CHOCH":
        if h4_signal == "BEARISH CHOCH":
            if daily_signal == "BEARISH CHOCH":
                status = "REVERSAL SELL READY"
            else:
                status = "WAIT DAILY CONFIRMATION"
        else:
            status = "WAIT 4H EXECUTION"

    else:
        status = "NO STRUCTURE ALIGNMENT"

    results.append([
        symbol,
        weekly_signal,
        monthly_signal,
        h4_signal,
        daily_signal,
        status
    ])


# -----------------------------
# OUTPUT
# -----------------------------
df_out = pd.DataFrame(results, columns=[
    "PAIR","WEEKLY","MONTHLY","4H","DAILY","VSEC STATUS"
])

st.dataframe(df_out, use_container_width=True)
