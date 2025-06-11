import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import numpy as np

# Load mock data
df = pd.read_csv("mock_health_data.csv")
features = ["hrv_mean", "hrv_variance", "bp_systolic", "bp_diastolic", "steps"]
risk_scores = []

# Simulate mini-batch processing (15-min intervals)
for i in range(len(df)):
    # Use current batch + last 24 hours (up to 96 rows)
    batch = df.iloc[max(0, i-95):i+1]
    X = batch[features]
    y = batch["risk_label"]
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Predict risk score for current batch
    current_batch = df.iloc[i:i+1][features]
    proba = model.predict_proba(current_batch)
    
    # Handle single-class case
    if proba.shape[1] == 1:  # Only one class in training data
        if model.classes_[0] == 0:
            risk_score = 0.0  # No risk if only class 0 (no stroke risk)
        else:
            risk_score = 100.0  # High risk if only class 1 (stroke risk)
    else:
        risk_score = proba[:, 1][0] * 100  # Convert to 0-100%
    
    risk_scores.append({
        "timestamp": df.iloc[i]["timestamp"],
        "patient_id": df.iloc[i]["patient_id"],
        "risk_score": risk_score
    })

# Save risk scores
pd.DataFrame(risk_scores).to_csv("risk_scores.csv", index=False)
print("Risk scores saved to risk_scores.csv")