import requests
from prefect.blocks.system import Secret
import asyncio
import base64

async def get_secret(name):
    secret = await Secret.load(name)
    return secret.get()

async def get_credentials():
    return {
        "client_id": await get_secret("fitbit-client-id"),
        "client_secret": await get_secret("fitbit-client-secret"),
        "token_uri": "https://api.fitbit.com/oauth2/token",
        "refresh_token": await get_secret("fitbit-refresh-token")
    }

def refresh_fitbit_token():
    creds = asyncio.run(get_credentials())
    if not creds["refresh_token"] or creds["refresh_token"] == "your_refresh_tokenX":
        print("Refresh token missing or invalid. Run get_fitbit_token.py to generate new tokens.")
        return

    auth_string = f"{creds['client_id']}:{creds['client_secret']}"
    auth_header = f"Basic {base64.b64encode(auth_string.encode()).decode()}"

    response = requests.post(creds["token_uri"], headers={
        "Authorization": auth_header,
        "Content-Type": "application/x-www-form-urlencoded"
    }, data={
        "grant_type": "refresh_token",
        "refresh_token": creds["refresh_token"]
    })

    token_data = response.json()
    if "access_token" in token_data:
        async def save_secrets():
            await Secret(value=token_data["access_token"]).save("fitbit-access-token", overwrite=True)
            await Secret(value=token_data["refresh_token"]).save("fitbit-refresh-token", overwrite=True)
        asyncio.run(save_secrets())
        print("New access token and refresh token saved to Prefect Secret blocks")
    else:
        print("Failed to refresh token:", token_data)
        print("Run get_fitbit_token.py to re-authenticate.")

if __name__ == "__main__":
    refresh_fitbit_token()