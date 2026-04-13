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

    if df is None or df.empty or len(df) < 2:
        print("Not enough data — skipping")
        return None

    latest = df.iloc[-1]
    prev = df.iloc[-2]

    if (
        latest['Close'] > latest['vwap'] and
        prev['Close'] < prev['vwap'] and
        latest['rsi'] > prev['rsi']
    ):
        return "BUY"

    if (
        latest['Close'] < latest['vwap'] and
        prev['Close'] > prev['vwap'] and
        latest['rsi'] < prev['rsi']
    ):
        return "SELL"

    return None


    if (
        latest['Close'] > latest['vwap'] and
        prev['Close'] < prev['vwap'] and
        latest['rsi'] > prev['rsi']
    ):
        return "BUY"

    if (
        latest['Close'] < latest['vwap'] and
        prev['Close'] > prev['vwap'] and
        latest['rsi'] < prev['rsi']
    ):
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
