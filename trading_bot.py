import pandas as pd
import numpy as np
import time
import requests
import random

SYMBOL = "QQQ"


# -------------------- TELEGRAM --------------------
def send_telegram(message):
    token = "8675620018:AAEOcL_6cnS4O8RoY779Rc50XDzKfjshgDI"
    chat_id = "8713694007"

    try:
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data={"chat_id": chat_id, "text": message}, timeout=10)
        print("Telegram sent:", message)
    except Exception as e:
        print("Telegram error:", e)


# -------------------- FAKE PRICE DATA --------------------
def get_data():

    # simulate price movement (no Yahoo needed)
    base_price = 450

    prices = []
    for i in range(50):
        base_price += random.uniform(-1, 1)
        prices.append(base_price)

    df = pd.DataFrame({
        "Close": prices,
        "Volume": np.random.randint(100, 1000, size=50)
    })

    return df


# -------------------- INDICATORS --------------------
def calculate_indicators(df):

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

    print("BOT STARTED (NO YAHOO MODE)")
    send_telegram("Bot started 🚀 (no Yahoo mode)")

    while True:

        print("New cycle...")

        df = get_data()
        df = calculate_indicators(df)

        signal = check_signal(df)

        if signal:
            msg = f"{signal} signal detected (simulated QQQ)"
            print(msg)
            send_telegram(msg)

        time.sleep(10)  # fast testing loop


# -------------------- ENTRY --------------------
if __name__ == "__main__":
    run_bot()
