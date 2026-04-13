import pandas as pd
import numpy as np
import yfinance as yf
import time

SYMBOL = "QQQ"
INTERVAL = "1m"

def get_data():
    df = yf.download(tickers=SYMBOL, period="1d", interval=INTERVAL)
    return df

def calculate_indicators(df):
    df['vwap'] = (df['Close'] * df['Volume']).cumsum() / df['Volume'].cumsum()
    
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['rsi'] = 100 - (100 / (1 + rs))
    
    return df
def check_signal(df):

    # 1. Safety check (prevents crashes)
    if df is None or df.empty or len(df) < 20:
        print("Not enough data — skipping")
        return None

    # 2. Get last two rows
    latest = df.iloc[-1]
    prev = df.iloc[-2]

    # 3. Force values into clean numbers (VERY IMPORTANT FIX)
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

    # 4. BUY signal
    if close > vwap and prev_close < prev_vwap and rsi > prev_rsi:
        return "BUY"

    # 5. SELL signal
    if close < vwap and prev_close > prev_vwap and rsi < prev_rsi:
        return "SELL"

    return None

def run_bot():
    print("Bot is running... watching Nasdaq (QQQ)")
    
    while True:
        df = get_data()
        df = calculate_indicators(df)

        signal = check_signal(df)

        if signal:
            print(f"{signal} signal at {df.index[-1]} price: {df['Close'].iloc[-1]}")

        time.sleep(60)

run_bot()
