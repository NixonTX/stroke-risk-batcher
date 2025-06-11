import requests
from dotenv import load_dotenv, set_key
import os
import base64

load_dotenv()

client_id = os.getenv("FITBIT_CLIENT_ID")
client_secret = os.getenv("FITBIT_CLIENT_SECRET")
token_uri = os.getenv("FITBIT_TOKEN_URI")
refresh_token = os.getenv("FITBIT_REFRESH_TOKEN")

if not refresh_token or refresh_token == "your_refresh_tokenX":
    print("Refresh token missing or invalid in .env. Run get_fitbit_token.py to generate new tokens.")
    exit(1)

auth_string = f"{client_id}:{client_secret}"
auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

response = requests.post(token_uri, headers={
    "Authorization": auth_header,
    "Content-Type": "application/x-www-form-urlencoded"
}, data={
    "grant_type": "refresh_token",
    "refresh_token": refresh_token
})

token_data = response.json()
if "access_token" in token_data:
    set_key(".env", "FITBIT_ACCESS_TOKEN", token_data["access_token"])
    set_key(".env", "FITBIT_REFRESH_TOKEN", token_data["refresh_token"])
    print("New access token and refresh token saved to .env")
else:
    print("Failed to refresh token:", token_data)
    print("Run get_fitbit_token.py to re-authenticate.")