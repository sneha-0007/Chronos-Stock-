import yfinance as yf

def get_historical_data(symbol, period="5d", interval="5m"):
    """
    Yahoo Finance used because FYERS User App
    does NOT allow historical data access.
    """
    ticker = yf.Ticker(symbol + ".NS")
    df = ticker.history(period=period, interval=interval)

    if df.empty:
        raise ValueError("Yahoo Finance returned no data")

    df.reset_index(inplace=True)

    return df[["Datetime", "Open", "High", "Low", "Close", "Volume"]]
