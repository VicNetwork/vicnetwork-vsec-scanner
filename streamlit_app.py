import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Multi-Timeframe VSEC Structure Engine")

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# -----------------------------
# BINANCE DATA FETCH
# -----------------------------
def get_data(symbol, interval):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": interval,
        "limit": 100
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
# STRUCTURE LOGIC (COMMON CORE)
# -----------------------------
def structure(df):
    if df is None:
        return None, None, None

    zone = df.iloc[-60:-15]

    return (
        zone["high"].max(),
        zone["low"].min(),
        df["close"].iloc[-1]
    )


# -----------------------------
# CHOCH CHECK
# -----------------------------
def choch(df):
    high, low, close = structure(df)

    if high is None:
        return "NO DATA"

    if close > high:
        return "BULLISH CHOCH"
    elif close < low:
        return "BEARISH CHOCH"
    else:
        return "NO CHOCH"


# -----------------------------
# VSEC ENGINE
# -----------------------------
results = []

for symbol in symbols:

    weekly = get_data(symbol, "1w")
    monthly = get_data(symbol, "1M")
    h4 = get_data(symbol, "4h")
    daily = get_data(symbol, "1d")

    weekly_signal = choch(weekly)
    monthly_signal = choch(monthly)
    h4_signal = choch(h4)
    daily_signal = choch(daily)

    # -------------------------
    # VSEC LOGIC (YOUR FRAMEWORK)
    # -------------------------

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
# DISPLAY
# -----------------------------
df_out = pd.DataFrame(results, columns=[
    "PAIR",
    "WEEKLY",
    "MONTHLY",
    "4H",
    "DAILY",
    "VSEC STATUS"
])

st.dataframe(df_out, use_container_width=True)
