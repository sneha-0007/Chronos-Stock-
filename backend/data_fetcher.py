from fyers_auth import get_fyers_client
import pandas as pd

def fetch_stock_data(symbol):
    fyers = get_fyers_client()

    data = {
        "symbol": symbol,
        "resolution": "D",
        "date_format": "1",
        "range_from": "2023-01-01",
        "range_to": "2024-01-01",
        "cont_flag": "1"
    }

    response = fyers.history(data)

    if response["s"] != "ok":
        return None

    df = pd.DataFrame(
        response["candles"],
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )
    return df
