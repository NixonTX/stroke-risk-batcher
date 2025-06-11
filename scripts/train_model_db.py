import pandas as pd
from sqlalchemy import create_engine, text
from sklearn.ensemble import RandomForestClassifier
from datetime import datetime, timedelta
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/srb_db"
engine = create_engine(db_url)

# Create risk_scores table
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS risk_scores (
            id SERIAL PRIMARY KEY,
            patient_id INT REFERENCES patients(patient_id),
            timestamp TIMESTAMP,
            risk_score FLOAT
        );
    """))
    conn.commit()

# Fetch and train
features = ["hrv_mean", "hrv_variance", "bp_systolic", "bp_diastolic", "steps"]
df = pd.read_sql("SELECT * FROM health_data WHERE timestamp >= %s ORDER BY timestamp", engine, params=(datetime.now() - timedelta(hours=24),))
if not df.empty:
    print("Training data:", df[["timestamp", "hrv_mean", "bp_systolic", "steps", "risk_label"]])
    for i in range(len(df)):
        batch = df.iloc[max(0, i-95):i+1]
        X = batch[features]
        y = batch["risk_label"]
        
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X, y)
        
        current_batch = df.iloc[i:i+1][features]
        proba = model.predict_proba(current_batch)
        risk_score = 0.0 if proba.shape[1] == 1 and model.classes_[0] == 0 else (100.0 if proba.shape[1] == 1 else proba[:, 1][0] * 100)
        
        risk_data = [{
            "patient_id": df.iloc[i]["patient_id"],
            "timestamp": df.iloc[i]["timestamp"],
            "risk_score": risk_score
        }]
        pd.DataFrame(risk_data).to_sql("risk_scores", engine, if_exists="append", index=False)
        print(f"Saved risk score for timestamp {df.iloc[i]['timestamp']}: {risk_score}")
else:
    print("No data found in health_data table")