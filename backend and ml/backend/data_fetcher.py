import pandas as pd
from datetime import datetime, timedelta
from fyers_auth import get_fyers_client


def fetch_stock_data(symbol: str):
    fyers = get_fyers_client()

    end_date = datetime.now()
    from_date = end_date - timedelta(days=365)

    data = {
        "symbol": f"NSE:{symbol.upper()}-EQ",
        "resolution": "D",
        "date_format": 1,
        "range_from": from_date.strftime("%Y-%m-%d"),
        "range_to": end_date.strftime("%Y-%m-%d"),
        "contflag": "1"
    }

    response = fyers.history(data)

    # ✅ SAFE CHECK
    if response.get("s") != "ok" or not response.get("candles"):
        print(f"FYERS history failed: {response}")
        return None

    df = pd.DataFrame(
        response["candles"],
        columns=["timestamp", "open", "high", "low", "close", "volume"]
    )

    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    df.set_index("timestamp", inplace=True)
    df.columns = [c.lower() for c in df.columns]

    return df
