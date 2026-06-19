import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="VicNetwork VSEC Debug", layout="wide")

st.title("📊 VSEC DEBUG MODE")

symbol = "BTCUSDT"

# -----------------------------
# RAW API TEST (BYBIT)
# -----------------------------
def test_api():
    url = "https://api.bybit.com/v5/market/kline"

    params = {
        "category": "linear",
        "symbol": symbol,
        "interval": "240",
        "limit": 10
    }

    try:
        r = requests.get(url, params=params, timeout=10)

        st.write("STATUS CODE:", r.status_code)

        try:
            data = r.json()
        except:
            st.write("❌ JSON PARSE FAILED")
            st.write(r.text)
            return None

        st.write("RAW RESPONSE:")
        st.json(data)

        return data

    except Exception as e:
        st.write("❌ REQUEST FAILED:", str(e))
        return None


# -----------------------------
# RUN TEST
# -----------------------------
data = test_api()

st.write("DONE")
