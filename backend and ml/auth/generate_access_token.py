from fyers_apiv3 import fyersModel

CLIENT_ID = "BX4VU41YBS-100"
SECRET_KEY = "9LPBWPIB1Y"
REDIRECT_URI = "https://127.0.0.1:5000/callback"

AUTH_CODE = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcHBfaWQiOiJCWDRWVTQxWUJTIiwidXVpZCI6IjdhMzhjM2ZlNjg2ODQ5NzI4YjQ2NWJkMDJjYTQwNWYzIiwiaXBBZGRyIjoiIiwibm9uY2UiOiIiLCJzY29wZSI6IiIsImRpc3BsYXlfbmFtZSI6IkZBRzg4MjQ5Iiwib21zIjoiSzEiLCJoc21fa2V5IjoiNjgwOTA5OGZiMDY5ODI2ZmJhMzUwNTM2Mjk2ZTBjYjg5N2FjZDVjYzAzOTlhODJlZWM1MzM1MTkiLCJpc0RkcGlFbmFibGVkIjoiTiIsImlzTXRmRW5hYmxlZCI6Ik4iLCJhdWQiOiJbXCJkOjFcIixcImQ6MlwiLFwieDowXCIsXCJ4OjFcIixcIng6MlwiXSIsImV4cCI6MTc2ODgyMDYxOSwiaWF0IjoxNzY4NzkwNjE5LCJpc3MiOiJhcGkubG9naW4uZnllcnMuaW4iLCJuYmYiOjE3Njg3OTA2MTksInN1YiI6ImF1dGhfY29kZSJ9.fC6gfu98qmAQNK6CB0R426_GD1hO-iqTSouyFi-vK1U"
session = fyersModel.SessionModel(
    client_id=CLIENT_ID,
    secret_key=SECRET_KEY,
    redirect_uri=REDIRECT_URI,
    response_type="code",
    grant_type="authorization_code"   # ✅ THIS FIXES -441
)

session.set_token(AUTH_CODE)
response = session.generate_token()

print(response)
