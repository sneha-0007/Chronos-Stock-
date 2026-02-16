import yfinance as yf
import pandas as pd


def fetch_stock_data(symbol):
    df = yf.download(
        symbol,
        period="1y",
        interval="1d",
        progress=False
    )

    if df.empty or len(df) < 20:
        return None

    df.reset_index(inplace=True)

    df = df.rename(columns={
        "Open": "open",
        "High": "high",
        "Low": "low",
        "Close": "close",
        "Volume": "volume"
    })

    df = df[["Date", "open", "high", "low", "close", "volume"]]

    return df
