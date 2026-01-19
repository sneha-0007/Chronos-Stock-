from .indicators import calculate_sma, calculate_rsi
import pandas as pd
import numpy as np
import talib  # optional, keep if installed


def quant_agent_decision(df):
    df = df.copy()

    # Indicators
    df['sma'] = calculate_sma(df)
    df['rsi'] = calculate_rsi(df)

    try:
        macd, signal, _ = talib.MACD(df['close'])
        df['macd'] = macd
    except Exception:
        df['macd'] = 0  # fallback if TA-Lib fails

    last_close = df['close'].iloc[-1]
    last_sma = df['sma'].iloc[-1]
    last_rsi = df['rsi'].iloc[-1]
    last_macd = df['macd'].iloc[-1]

    if last_rsi < 30 and last_close > last_sma and last_macd > 0:
        action = "BUY"
        pred_price = last_close * 1.02
    elif last_rsi > 70 and last_close < last_sma and last_macd < 0:
        action = "SELL"
        pred_price = last_close * 0.98
    else:
        action = "HOLD"
        pred_price = last_sma

    return {
        "action": action,
        "predicted_price": round(float(pred_price), 2)
    }
