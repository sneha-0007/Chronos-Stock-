import os
from dotenv import load_dotenv
from fyers_apiv3 import fyersModel

load_dotenv()

def get_fyers_client():
    """
    FYERS client ONLY for:
    - Authentication
    - Profile
    - Orders (future)
    """
    client_id = os.getenv("FYERS_CLIENT_ID")
    access_token = os.getenv("FYERS_ACCESS_TOKEN")

    if not client_id or not access_token:
        raise ValueError("FYERS credentials missing")

    fyers = fyersModel.FyersModel(
        client_id=client_id,
        token=access_token,
        log_path=""
    )
    return fyers
