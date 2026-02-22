import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(page_title="Supply Chain Map", layout="wide")

# This MUST match the name of the file you uploaded to GitHub
FILE_NAME = '17030125283_Isha Khatu_procurement_assignment.xlsx'

st.title("🌍 Supplier Network Map")

# --- DEBUGGER SECTION ---
if not os.path.exists(FILE_NAME):
    st.error(f"❌ File Not Found: {FILE_NAME}")
    st.info(f"Files detected in your GitHub: {os.listdir('.')}")
    st.stop()

@st.cache_data
def load_and_map_data(path):
    try:
        xl = pd.ExcelFile(path)
        sheets = xl.sheet_names
        
        # Smart Search for Sheets
        def get_sheet(name):
            match = [s for s in sheets if name.lower() in s.lower()]
            return match[0] if match else None

        s1, s2, s3 = get_sheet("Tier-1"), get_sheet("Tier-2"), get_sheet("Tier-3")
        
        # Load Tier 1 & 2
        t1 = pd.read_excel(path, sheet_name=s1, skiprows=3)
        t2 = pd.read_excel(path, sheet_name=s2, skiprows=3)
        
        # Load Tier 3 (Fewer skips usually)
        t3 = pd.read_excel(path, sheet_name=s3, skiprows=2)

        # Standardize Country Names
        c_fix = {'US': 'USA', 'UK': 'United Kingdom', 'TT': 'Taiwan', 'KS': 'South Korea', 'CH': 'China'}

        # Combine T1 and T2
        combined_1_2 = pd.concat([t1, t2])[['Country', 'Relationship Value (Q) (Mln) (USD)']]
        combined_1_2['Country'] = combined_1_2['Country'].str.strip().replace(c_fix)

        # Process Tier 3 (Extract from Ticker)
        def fix_t3(ticker):
            parts = str(ticker).split(' ')
            return c_fix.get(parts[1], parts[1]) if len(parts) > 1 else "Unknown"
        
        t3['Country'] = t3['Ticker'].apply(fix_t3)
        t3_clean = t3[['Country', 'Relationship Value (Q) (Mln) (USD)']]

        # Final Merge
        final = pd.concat([combined_1_2, t3_clean])
        final['Value'] = pd.to_numeric(final['Relationship Value (Q) (Mln) (USD)'], errors='coerce')
        return final.dropna(subset=['Value'])

    except Exception as e:
        st.error(f"Data Processing Error: {e}")
        return None

# --- APP EXECUTION ---
df = load_and_map_data(FILE_NAME)

if df is not None:
    map_data = df.groupby('Country')['Value'].sum().reset_index()
    
    fig = px.choropleth(map_data, 
                        locations="Country", 
                        locationmode='country names',
                        color="Value",
                        hover_name="Country",
                        color_continuous_scale="Viridis",
                        title="Total Procurement Spend by Country")
    
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(map_data.sort_values('Value', ascending=False), hide_index=True)
