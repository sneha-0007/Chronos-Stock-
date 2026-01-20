from fyers_auth import get_fyers_client

try:
    fyers = get_fyers_client()
    print("FYERS client initialized successfully ✅")
except Exception as e:
    print("FYERS auth failed ❌", e)
