from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os

load_dotenv()

# Database connection
db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/srb_db"
engine = create_engine(db_url)

# Create tables
with engine.connect() as conn:
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS patients (
            patient_id SERIAL PRIMARY KEY,
            name VARCHAR(100)
        );
    """))
    conn.execute(text("""
        CREATE TABLE IF NOT EXISTS health_data (
            id SERIAL PRIMARY KEY,
            patient_id INT REFERENCES patients(patient_id),
            timestamp TIMESTAMP,
            hrv_mean FLOAT,
            hrv_variance FLOAT,
            bp_systolic FLOAT,
            bp_diastolic FLOAT,
            steps INT,
            risk_label INT
        );
    """))
    conn.execute(text("INSERT INTO patients (patient_id, name) VALUES (1, 'Test Patient') ON CONFLICT DO NOTHING;"))
    conn.commit()
print("Database initialized")