from fyers_apiv3 import fyersModel
import webbrowser

CLIENT_ID = "BX4VU41YBS-100"     # App ID, not login ID
REDIRECT_URI = "https://127.0.0.1:5000/callback"
STATE = "fyers_auth"

session = fyersModel.SessionModel(
    client_id=CLIENT_ID,
    redirect_uri=REDIRECT_URI,
    response_type="code",
    state=STATE
)

auth_url = session.generate_authcode()

print("Open this URL in browser:")
print(auth_url)

# Automatically open browser
webbrowser.open(auth_url)
