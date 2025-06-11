import requests
import webbrowser
import http.server
import socketserver
import urllib.parse
from dotenv import load_dotenv, set_key
import os
import base64

load_dotenv()

# Fitbit OAuth 2.0 credentials
client_id = os.getenv("FITBIT_CLIENT_ID")
client_secret = os.getenv("FITBIT_CLIENT_SECRET")
redirect_uri = os.getenv("FITBIT_REDIRECT_URL")
auth_uri = os.getenv("FITBIT_AUTH_URI")
token_uri = os.getenv("FITBIT_TOKEN_URI")

# Encode client_id:client_secret for Basic Auth
auth_string = f"{client_id}:{client_secret}"
auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

# Step 1: Open browser for user login
auth_url = f"{auth_uri}?client_id={client_id}&response_type=code&scope=activity+heartrate&redirect_uri={redirect_uri}"
webbrowser.open(auth_url)

# Step 2: Local server to capture authorization code
auth_code = None
class OAuthHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        query = urllib.parse.urlparse(self.path).query
        params = urllib.parse.parse_qs(query)
        if "code" in params:
            auth_code = params["code"][0]
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Authorization complete. You can close this window.")

with socketserver.TCPServer(("", 8080), OAuthHandler) as httpd:
    print("Waiting for authorization code at http://localhost:8080/callback...")
    httpd.handle_request()

# Step 3: Exchange code for access token
if auth_code:
    response = requests.post(token_uri, headers={
        "Authorization": auth_header,
        "Content-Type": "application/x-www-form-urlencoded"
    }, data={
        "client_id": client_id,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri
    })
    token_data = response.json()
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    # Step 4: Save to .env
    if access_token and refresh_token:
        set_key(".env", "FITBIT_ACCESS_TOKEN", access_token)
        set_key(".env", "FITBIT_REFRESH_TOKEN", refresh_token)
        print("Access token and refresh token saved to .env")
    else:
        print("Failed to get tokens:", token_data)
else:
    print("No authorization code received")