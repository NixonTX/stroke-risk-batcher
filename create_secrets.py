from prefect.blocks.system import Secret
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def create_secret_block(name, value):
    secret = Secret(value=value)
    await secret.save(name=name, overwrite=True)

if __name__ == "__main__":
    secrets = [
        ("fitbit-client-id", os.getenv("FITBIT_CLIENT_ID")),
        ("fitbit-client-secret", os.getenv("FITBIT_CLIENT_SECRET")),
        ("fitbit-refresh-token", os.getenv("FITBIT_REFRESH_TOKEN")),
        ("fitbit-access-token", os.getenv("FITBIT_ACCESS_TOKEN")),
        ("db-user", os.getenv("DB_USER")),
        ("db-password", os.getenv("DB_PASSWORD")),
        ("db-host", os.getenv("DB_HOST")),
        ("db-port", os.getenv("DB_PORT"))
    ]
    for name, value in secrets:
        asyncio.run(create_secret_block(name, value))