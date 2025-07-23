import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="FusionFlow", page_icon=":chart_with_upwards_trend:", layout="wide")

st.title("🚀 FusionFlow - Order Tracking")

# Test API connection
try:
    response = requests.get("http://localhost:8000/orders")
    orders = response.json()

    st.success("Connected to API")

    # Display orders as table
    df = pd.DataFrame(orders)
    st.dataframe(df, use_container_width=True)

except:
    st.error("Cannot connect to API. Make sure FastAPI is running.")

# Quick stats
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Total Orders", len(orders))
with col2:
    st.metric("In Transit", len([o for o in orders if o["status"] == "In Transit"]))
with col3:
    st.metric("Delivered", len([o for o in orders if o["status"] == "Delivered"]))

# Order status distribution
status_counts = pd.Series([o["status"] for o in orders]).value_counts()
st.bar_chart(status_counts)

# TODO: Add a filter for supplier, project type, status, etc.