import streamlit as st
import pandas as pd
import plotly.express as px

# Set page config
st.set_page_config(page_title="Global Supplier Network Map", layout="wide")

st.title("🌍 Global Supplier Procurement Analysis")
st.markdown("This dashboard visualizes the relationship values across Tier-1, Tier-2, and Tier-3 suppliers.")

@st.cache_data
def load_and_clean_data():
    # File names (Adjust if your file names differ slightly)
    f1 = '17030125283_Isha Khatu_procurement_assignment.xlsx - Tier-1.csv'
    f2 = '17030125283_Isha Khatu_procurement_assignment.xlsx - Tier-2.csv'
    f3 = '17030125283_Isha Khatu_procurement_assignment.xlsx - Tier-3.csv'
    
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

    # Load Tiers
    t1 = pd.read_csv(f1, skiprows=3)
    t2 = pd.read_csv(f2, skiprows=3)
    t3 = pd.read_csv(f3, skiprows=2)

    # Clean and Combine
    t1['Country'] = t1['Country'].str.strip().replace(country_map)
    t2['Country'] = t2['Country'].str.strip().replace(country_map)
    
    # Extract Country from Ticker for Tier 3
    t3 = t3[t3['Ticker'].str.contains(' Equity', na=False)]
    t3['Country'] = t3['Ticker'].apply(get_country_from_ticker)

    # Consolidate
    cols = ['Country', 'Relationship Value (Q) (Mln) (USD)']
    combined = pd.concat([t1[cols], t2[cols], t3[cols]])
    
    # Convert value to numeric
    combined['Relationship Value (Q) (Mln) (USD)'] = pd.to_numeric(
        combined['Relationship Value (Q) (Mln) (USD)'], errors='coerce'
    )
    
    return combined.dropna()

# Load data
try:
    df = load_and_clean_data()
    
    # Aggregate data by country
    country_stats = df.groupby('Country')['Relationship Value (Q) (Mln) (USD)'].sum().reset_index()
    country_stats = country_stats.sort_values(by='Relationship Value (Q) (Mln) (USD)', ascending=False)

    # Top Metrics
    total_val = country_stats['Relationship Value (Q) (Mln) (USD)'].sum()
    num_countries = len(country_stats)
    
    col1, col2 = st.columns(2)
    col1.metric("Total Relationship Value", f"${total_val:,.2f} M")
    col2.metric("Countries Involved", num_countries)

    # --- CHOROPLETH MAP ---
    st.subheader("Interactive Supplier Map (USD Millions)")
    fig_map = px.choropleth(
        country_stats,
        locations="Country",
        locationmode='country names',
        color="Relationship Value (Q) (Mln) (USD)",
        hover_name="Country",
        color_continuous_scale=px.colors.sequential.Plasma,
        title="Supplier Concentration by Country"
    )
    fig_map.update_layout(height=600, margin={"r":0,"t":40,"l":0,"b":0})
    st.plotly_chart(fig_map, use_container_width=True)

    # --- BAR CHART & TABLE ---
    st.subheader("Top Countries by Spend")
    c1, c2 = st.columns([2, 1])
    
    with c1:
        fig_bar = px.bar(
            country_stats.head(15),
            x='Relationship Value (Q) (Mln) (USD)',
            y='Country',
            orientation='h',
            color='Relationship Value (Q) (Mln) (USD)',
            color_continuous_scale='Viridis'
        )
        fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)
        
    with c2:
        st.write("Full Breakdown")
        st.dataframe(country_stats, height=400, hide_index=True)

except FileNotFoundError:
    st.error("Error: CSV files not found. Please ensure the files are in the same directory.")
except Exception as e:
    st.error(f"An unexpected error occurred: {e}")
