import pandas as pd
import numpy as np
import time
import requests

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame

# ---------------- CONFIG ----------------
SYMBOL = "QQQ"

API_KEY = "PKBP3WBD5CUDNB3ZTEB6XILIU4"
SECRET_KEY = "6C8PieqwKYGFfE5ZSTeChLu1sSPJGWbxrojksiY9ff4H"

TG_TOKEN = "8675620018:AAH09frqqZIkfSnR-oeH7ZXym90WbAgZXXo"
TG_CHAT_ID = "8713694007"

data_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)


# ---------------- TELEGRAM ----------------
def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{TG_TOKEN}/sendMessage"
        requests.post(url, data={"chat_id": TG_CHAT_ID, "text": message}, timeout=10)
        print("Telegram sent:", message)
    except Exception as e:
        print("Telegram error:", e)


# ---------------- GET REAL DATA ----------------
def get_data():
    try:
        request = StockBarsRequest(
            symbol_or_symbols=SYMBOL,
            timeframe=TimeFrame.Minute,
            limit=50
        )

        bars = data_client.get_stock_bars(request)

        df = bars.df.reset_index()
        df = df[df["symbol"] == SYMBOL]

        df = df.rename(columns={
            "close": "Close",
            "volume": "Volume"
        })

        return df[["Close", "Volume"]]

    except Exception as e:
        print("Data error:", e)
        return pd.DataFrame()


# ---------------- INDICATORS ----------------
def calculate_indicators(df):
    if df.empty:
        return df

    df['vwap'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df


# ---------------- SIGNAL ----------------
def check_signal(df):
    if df is None or df.empty or len(df) < 20:
        return None

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    try:
        close = float(latest['Close'])
        prev_close = float(prev['Close'])

        vwap = float(latest['vwap'])
        prev_vwap = float(prev['vwap'])

        rsi = float(latest['rsi'])
        prev_rsi = float(prev['rsi'])

    except:
        return None

    if close > vwap and prev_close < prev_vwap and rsi > prev_rsi:
        return "BUY"

    if close < vwap and prev_close > prev_vwap and rsi < prev_rsi:
        return "SELL"

    return None


# ---------------- MAIN LOOP ----------------
def run_bot():

    print("BOT STARTED (ALPACA MODE)")
    send_telegram("Bot started 🚀 (real Alpaca data)")

    while True:

        df = get_data()

        if df.empty:
            print("No data...")
            time.sleep(30)
            continue

        df = calculate_indicators(df)

        signal = check_signal(df)

        if signal:
            msg = f"{signal} signal on {SYMBOL}"
            print(msg)
            send_telegram(msg)

        time.sleep(60)


# ---------------- ENTRY ----------------
if __name__ == "__main__":
    run_bot()
