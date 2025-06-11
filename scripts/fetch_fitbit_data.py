import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
import time

load_dotenv()

# Fitbit API credentials
access_token = os.getenv("FITBIT_ACCESS_TOKEN")
headers = {"Authorization": f"Bearer {access_token}"}

# Database connection
db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/srb_db"
engine = create_engine(db_url)

# Fetch Fitbit data
def fetch_fitbit_data():
    now = datetime.now()
    start_time = (now - timedelta(minutes=15)).strftime("%Y-%m-%dT%H:%M:%S")
    end_time = now.strftime("%Y-%m-%dT%H:%M:%S")

    # Fetch heart rate
    url = f"https://api.fitbit.com/1/user/-/activities/heart/date/today/1d/1min/time/{start_time[11:]}/{end_time[11:]}.json"
    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        print(f"Heart rate API error: {response.status_code}, {response.json()}")
        heart_data = []
    else:
        heart_data = response.json().get("activities-heart-intraday", {}).get("dataset", [])
    print("Heart data:", heart_data)

    # Fetch steps
    url_steps = f"https://api.fitbit.com/1/user/-/activities/steps/date/today/1d/1min/time/{start_time[11:]}/{end_time[11:]}.json"
    response = requests.get(url_steps, headers=headers)
    if response.status_code != 200:
        print(f"Steps API error: {response.status_code}, {response.json()}")
        steps_data = []
    else:
        steps_data = response.json().get("activities-steps-intraday", {}).get("dataset", [])
    print("Steps data:", steps_data)

    # Simulate realistic data if Fitbit data is unavailable
    heart_rates = [d["value"] for d in heart_data]
    steps = sum(d["value"] for d in steps_data) if steps_data else 0
    
    # Simulate HRV with daily pattern (higher during sleep, lower during activity)
    hour = now.hour
    base_hrv = 50 + 20 * np.sin(2 * np.pi * hour / 24)  # Daily cycle
    hrv_mean = np.mean(heart_rates) if heart_rates else np.clip(np.random.normal(base_hrv, 10), 20, 80)
    hrv_variance = np.var(heart_rates) if heart_rates else np.clip(np.random.normal(5, 2), 1, 10)
    
    # Simulate steps (higher during active hours, e.g., 9 AM to 9 PM)
    if 9 <= hour <= 21:
        steps = np.random.poisson(50)  # Average 50 steps per 15-min window
    else:
        steps = np.random.poisson(5)   # Fewer steps during sleep
    
    bp_systolic = np.clip(np.random.normal(120, 20), 90, 160)
    bp_diastolic = np.clip(np.random.normal(80, 10), 60, 90)
    
    # Adjust risk_label for balance
    risk_label = 1 if hrv_mean < 40 or bp_systolic > 130 or steps > 100 else 0

    batch = {
        "timestamp": now,
        "patient_id": 1,
        "hrv_mean": hrv_mean,
        "hrv_variance": hrv_variance,
        "bp_systolic": bp_systolic,
        "bp_diastolic": bp_diastolic,
        "steps": steps,
        "risk_label": risk_label
    }

    df = pd.DataFrame([batch])
    df.to_sql("health_data", engine, if_exists="append", index=False)
    print("Batch saved to database:", batch)

# Simulate multiple data points for testing
if __name__ == "__main__":
    for _ in range(5):  # Simulate 5 batches
        fetch_fitbit_data()
        time.sleep(60)  # Wait 1 minute between batches