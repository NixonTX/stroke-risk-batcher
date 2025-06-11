import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta

load_dotenv()

# Database connection
db_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/srb_db"
engine = create_engine(db_url)

# Load data (last 24 hours)
time_threshold = datetime.now() - timedelta(hours=24)
data = pd.read_sql("SELECT * FROM health_data WHERE patient_id = 1 AND timestamp >= %s ORDER BY timestamp", engine, params=(time_threshold,))
risk_scores = pd.read_sql("SELECT * FROM risk_scores WHERE patient_id = 1 AND timestamp >= %s ORDER BY timestamp", engine, params=(time_threshold,))

# Debug output
st.write("Health Data:", data[["timestamp", "hrv_mean", "bp_systolic", "steps", "risk_label"]])
st.write("Risk Scores:", risk_scores[["timestamp", "risk_score"]])

# Dashboard
st.title("Wearable Health Monitoring Dashboard")
st.subheader("HRV Trend (Last 24 Hours)")
if len(data) > 1:
    fig_hrv = px.line(data, x="timestamp", y="hrv_mean", title="HRV Mean Over Time", markers=True)
    fig_hrv.update_yaxes(range=[min(data["hrv_mean"]) - 5, max(data["hrv_mean"]) + 5])
    fig_hrv.update_xaxes(range=[time_threshold, datetime.now()])
    st.plotly_chart(fig_hrv)
elif len(data) == 1:
    st.write("Only one HRV data point; need more for line graph")
else:
    st.write("No HRV data available")

st.subheader("Stroke Risk Score (Last 24 Hours)")
if len(risk_scores) > 1:
    fig_risk = px.line(risk_scores, x="timestamp", y="risk_score", title="Stroke Risk Score Over Time", markers=True)
    fig_risk.update_yaxes(range=[min(risk_scores["risk_score"]) - 10, max(risk_scores["risk_score"]) + 10])
    fig_risk.update_xaxes(range=[time_threshold, datetime.now()])
    st.plotly_chart(fig_risk)
elif len(risk_scores) == 1:
    st.write("Only one risk score; need more for line graph")
else:
    st.write("No risk scores available")