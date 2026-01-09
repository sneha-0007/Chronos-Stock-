from indicators import calculate_sma, calculate_rsi

def quant_agent_decision(df):
    df["SMA"] = calculate_sma(df)
    df["RSI"] = calculate_rsi(df)

    last_close = df["close"].iloc[-1]
    last_sma = df["SMA"].iloc[-1]
    last_rsi = df["RSI"].iloc[-1]

    if last_rsi < 30 and last_close > last_sma:
        action = "BUY"
    elif last_rsi > 70 and last_close < last_sma:
        action = "SELL"
    else:
        action = "HOLD"

    return {
        "action": action,
        "predicted_price": round(last_sma, 2)
    }
