import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Supply Chain Map", layout="wide")

# 1. SET FILENAME
FILE_NAME = '17030125283_Isha Khatu_procurement_assignment.xlsx'

st.title("🌍 Procurement Map Debugger")

# Check if file exists
if not os.path.exists(FILE_NAME):
    st.error(f"❌ File Not Found! GitHub cannot find '{FILE_NAME}'")
    st.info(f"Files currently in your GitHub folder: {os.listdir('.')}")
else:
    st.success(f"✅ Found {FILE_NAME}!")

    @st.cache_data
    def load_data(path):
        # We wrap this in a try-except to catch sheet name errors
        try:
            # Read sheets
            t1 = pd.read_excel(path, sheet_name='Tier-1', skiprows=3)
            t2 = pd.read_excel(path, sheet_name='Tier-2', skiprows=3)
            t3 = pd.read_excel(path, sheet_name='Tier-3', skiprows=2)
            
            # Basic cleaning for mapping
            t1 = t1[['Country', 'Relationship Value (Q) (Mln) (USD)']].copy()
            t2 = t2[['Country', 'Relationship Value (Q) (Mln) (USD)']].copy()
            
            # Combine them
            combined = pd.concat([t1, t2])
            combined['Relationship Value (Q) (Mln) (USD)'] = pd.to_numeric(combined['Relationship Value (Q) (Mln) (USD)'], errors='coerce')
            return combined.dropna()
        except Exception as e:
            st.error(f"Error reading sheets: {e}")
            return None

    df = load_data(FILE_NAME)

    if df is not None:
        stats = df.groupby('Country')['Relationship Value (Q) (Mln) (USD)'].sum().reset_index()
        fig = px.choropleth(stats, locations="Country", locationmode='country names', 
                            color="Relationship Value (Q) (Mln) (USD)", title="Supplier Map")
        st.plotly_chart(fig, use_container_width=True)
        st.write(stats)
