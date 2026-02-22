import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Global Supplier Map", layout="wide")

st.title("🌍 Global Supplier Procurement Dashboard")
st.markdown("Reading data directly from the multi-sheet Excel file.")

# Change this if you rename your file in GitHub
FILE_NAME = '17030125283_Isha Khatu_procurement_assignment.xlsx'

@st.cache_data
def load_and_clean_data(file_path):
    # Mapping for ticker codes and country cleaning
    country_map = {
        'US': 'United States', 'USA': 'United States',
        'FP': 'France', 'France ': 'France',
        'SS': 'Sweden', 'LN': 'United Kingdom', 'England': 'United Kingdom',
        'GR': 'Germany', 'TT': 'Taiwan', 'KS': 'South Korea',
        'CH': 'China', 'CN': 'China', 'JP': 'Japan',
        'IN': 'India', 'SP': 'Spain', 'AU': 'Australia',
        'HK': 'Hong Kong', 'BB': 'Belgium', 'SW': 'Switzerland',
        'Canda': 'Canada', 'Canada': 'Canada', 'Netherlands': 'Netherlands'
    }

    def get_country_from_ticker(ticker):
        if pd.isna(ticker): return "Unknown"
        parts = str(ticker).split(' ')
        if len(parts) >= 2:
            code = parts[1]
            return country_map.get(code, code)
        return "Unknown"

    # --- READ SHEETS ---
    # We use the skip-rows logic identified during data inspection
    t1 = pd.read_excel(file_path, sheet_name='Tier-1', skiprows=3)
    t2 = pd.read_excel(file_path, sheet_name='Tier-2', skiprows=3)
    t3 = pd.read_excel(file_path, sheet_name='Tier-3', skiprows=2)

    # --- CLEAN TIER 1 & 2 ---
    t1['Country'] = t1['Country'].str.strip().replace(country_map)
    t2['Country'] = t2['Country'].str.strip().replace(country_map)
    
    # --- CLEAN TIER 3 ---
    # T3 doesn't have a country column, so we derive it from the Ticker
    t3 = t3[t3['Ticker'].str.contains(' Equity', na=False)].copy()
    t3['Country'] = t3['Ticker'].apply(get_country_from_ticker)

    # --- COMBINE ---
    cols = ['Country', 'Relationship Value (Q) (Mln) (USD)']
    combined = pd.concat([t1[cols], t2[cols], t3[cols]])
    
    # Ensure values are numbers
    combined['Relationship Value (Q) (Mln) (USD)'] = pd.to_numeric(
        combined['Relationship Value (Q) (Mln) (USD)'], errors='coerce'
    )
    
    return combined.dropna()

try:
    df = load_and_clean_data(FILE_NAME)
    
    # Group by Country
    stats = df.groupby('Country')['Relationship Value (Q) (Mln) (USD)'].sum().reset_index()
    stats = stats.sort_values(by='Relationship Value (Q) (Mln) (USD)', ascending=False)

    # Metrics
    total_val = stats['Relationship Value (Q) (Mln) (USD)'].sum()
    st.metric("Total Relationship Value", f"${total_val:,.2f} Million")

    # Map
    fig = px.choropleth(
        stats,
        locations="Country",
        locationmode='country names',
        color="Relationship Value (Q) (Mln) (USD)",
        hover_name="Country",
        color_continuous_scale='Reds',
        title="Global Procurement Spend"
    )
    fig.update_layout(height=600)
    st.plotly_chart(fig, use_container_width=True)

    # Data Table
    st.subheader("Spend by Country")
    st.dataframe(stats, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Waiting for file... Please ensure '{FILE_NAME}' is uploaded to GitHub.")
    st.info("Technical Error: " + str(e))
