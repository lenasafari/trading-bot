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

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message})
        print("Telegram sent:", message)
    except Exception as e:
        print("Telegram error:", e)


# -------------------- DATA --------------------
def get_data():
    try:
        print("Fetching data...")
        df = yf.download(tickers=SYMBOL, period="1d", interval=INTERVAL)

        if df is None or df.empty:
            print("No data received from Yahoo")
            return pd.DataFrame()

        return df

    except Exception as e:
        print("Download error:", e)
        return pd.DataFrame()


# -------------------- INDICATORS --------------------
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


# -------------------- SIGNAL --------------------
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


# -------------------- MAIN LOOP --------------------
def run_bot():

    print(">>> BOT STARTED <<<")
    send_telegram("Bot started 🚀")

    while True:

        print("Loop running...")

        df = get_data()
        df = calculate_indicators(df)

        signal = check_signal(df)

        if signal:
            msg = f"{signal} signal on {SYMBOL}"
            print(msg)
            send_telegram(msg)

        time.sleep(60)


# -------------------- ENTRY POINT --------------------
if __name__ == "__main__":
    print(">>> ENTRY POINT HIT <<<")
    run_bot()
