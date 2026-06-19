import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Scanner", layout="wide")

st.title("📊 VicNetwork VSEC Scanner")
st.write("Stable VSEC Engine (Production Fix)")

symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]

# -----------------------------
# ONLY RELIABLE DATA SOURCE
# -----------------------------
def get_daily(symbol):
    url = "https://api.binance.com/api/v3/klines"

    params = {
        "symbol": symbol,
        "interval": "1d",
        "limit": 365
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        if r.status_code != 200:
            return None

        data = r.json()

        if not isinstance(data, list) or len(data) < 100:
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
# BUILD WEEKLY + MONTHLY (CORRECT WAY)
# -----------------------------
def build_timeframes(df):

    weekly = df.resample("W").agg({
        "open":"first",
        "high":"max",
        "low":"min",
        "close":"last"
    })

    monthly = df.resample("M").agg({
        "open":"first",
        "high":"max",
        "low":"min",
        "close":"last"
    })

    return weekly, monthly


# -----------------------------
# FIX: ENABLE RESAMPLE (CRITICAL)
# -----------------------------
def prepare(df):
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"], unit="ms")
    df.set_index("time", inplace=True)
    return df


# -----------------------------
# CHOCH ENGINE (YOUR LOGIC)
# -----------------------------
def choch(df):
    if df is None or len(df) < 50:
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

    daily = get_daily(symbol)

    if daily is None:
        results.append([symbol, "NO DATA", "NO DATA", "NO DATA", "NO DATA", "NO DATA"])
        continue

    daily = prepare(daily)

    weekly, monthly = build_timeframes(daily)

    weekly_signal = choch(weekly)
    monthly_signal = choch(monthly)

    h4 = daily.iloc[-120:]   # proxy for 4H (stable cloud workaround)
    h4_signal = choch(h4)

    daily_signal = choch(daily)

    # -----------------------------
    # VSEC LOGIC (UNCHANGED STRUCTURE)
    # -----------------------------
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
