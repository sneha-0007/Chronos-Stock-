from fyers_apiv3 import fyersModel
from config import CLIENT_ID, ACCESS_TOKEN

def get_fyers_client():
    fyers = fyersModel.FyersModel(
        client_id=CLIENT_ID,
        token=ACCESS_TOKEN,
        log_path=""
    )
    return fyers
