from indicators import calculate_sma, calculate_rsi


def quant_agent_decision(df):

    if df is None or df.empty:
        return {
            "action": "NO DATA",
            "predicted_price": None
        }

    df["SMA"] = calculate_sma(df)
    df["RSI"] = calculate_rsi(df)

    df = df.dropna()

    if df.empty:
        return {
            "action": "INSUFFICIENT DATA",
            "predicted_price": None
        }

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
        "predicted_price": round(float(last_sma), 2)
    }
