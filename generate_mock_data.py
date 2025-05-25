import pandas as pd
import numpy as np

# Generate 24 hours of 15-min batches (96 rows)
timestamps = pd.date_range(start="2025-05-25", periods=96, freq="15min")
data = {
    "timestamp": timestamps,
    "patient_id": [1] * 96,
    "hrv_mean": np.random.normal(50, 10, 96).clip(20, 80),
    "hrv_variance": np.random.normal(5, 2, 96).clip(1, 10),
    "bp_systolic": np.random.normal(120, 15, 96).clip(90, 140),
    "bp_diastolic": np.random.normal(80, 10, 96).clip(60, 90),
    "steps": np.random.randint(0, 1000, 96)
}
df = pd.DataFrame(data)
df["risk_label"] = ((df["bp_systolic"] > 140) | (df["hrv_mean"] < 30)).astype(int)
df.to_csv("mock_health_data.csv", index=False)
print("Mock data saved to mock_health_data.csv")