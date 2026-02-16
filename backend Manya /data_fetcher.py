import yfinance as yf


def fetch_stock_data(symbol):
    """
    Fetch 1 year of daily stock data using yfinance.
    """

    try:
        df = yf.download(
            symbol,
            period="1y",
            interval="1d",
            progress=False
        )

        if df.empty:
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

    except Exception:
        return None
