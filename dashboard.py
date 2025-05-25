import streamlit as st
import pandas as pd
import plotly.express as px

# Load data
data = pd.read_csv("mock_health_data.csv")
risk_scores = pd.read_csv("risk_scores.csv")

# Dashboard
st.title("Wearable Health Monitoring with 'Mini-Batch Training' Dashboard")
st.subheader("HRV Trend")
fig_hrv = px.line(data, x="timestamp", y="hrv_mean", title="HRV Mean Over Time")
st.plotly_chart(fig_hrv)

st.subheader("Stroke Risk Score")
fig_risk = px.line(risk_scores, x="timestamp", y="risk_score", title="Stroke Risk Score Over Time")
st.plotly_chart(fig_risk)