from fyers_auth import get_fyers_client

fyers = get_fyers_client()

data = {
    "symbol": "NSE:SBIN-EQ",
    "resolution": "D",
    "date_format": 1,
    "range_from": "2024-01-01",
    "range_to": "2024-12-31",
    "contflag": "1"
}

response = fyers.history(data)
print(response)
