import pandas as pd
import numpy as np
import yfinance as yf
import time
import requests

SYMBOL = "QQQ"
INTERVAL = "1m"


# -------------------- TELEGRAM --------------------
def send_telegram(message):
    token = "8675620018:AAEOcL_6cnS4O8RoY779Rc50XDzKfjshgDI"
    chat_id = "8713694007"

    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        requests.post(url, data={"chat_id": chat_id, "text": message})
    except Exception as e:
        print("Telegram error:", e)


# -------------------- DATA --------------------
def get_data():
    try:
        df = yf.download(tickers=SYMBOL, period="1d", interval=INTERVAL)
        return df
    except Exception as e:
        print("Download error:", e)
        return pd.DataFrame()


# -------------------- INDICATORS --------------------
def calculate_indicators(df):

    if df is None or df.empty:
        return df

    df['vwap'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))

    return df


# -------------------- SIGNAL LOGIC --------------------
def check_signal(df):

    if df is None or df.empty or len(df) < 20:
        print("Not enough data — skipping")
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

    except Exception as e:
        print(f"Data error: {e}")
        return None

    if close > vwap and prev_close < prev_vwap and rsi > prev_rsi:
        return "BUY"

    if close < vwap and prev_close > prev_vwap and rsi < prev_rsi:
        return "SELL"

    return None


# -------------------- BOT LOOP --------------------
def run_bot():

    print("Bot is running... watching Nasdaq (QQQ)")
    send_telegram("Bot started 🚀")

    while True:

        df = get_data()

        if df is None or df.empty:
            print("No data received")
            time.sleep(60)
            continue

        df = calculate_indicators(df)

        signal = check_signal(df)

        if signal:
            msg = f"{signal} signal at {df.index[-1]} price: {df['Close'].iloc[-1]}"
            print(msg)
            send_telegram(msg)

        time.sleep(60)


# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    run_bot()
