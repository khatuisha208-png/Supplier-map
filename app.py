import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

# This must match your filename on GitHub exactly
FILE_NAME = '17030125283_Isha Khatu_procurement_assignment.xlsx'

st.title("🌍 Global Supplier Procurement Map")

@st.cache_data
def load_data(file_path):
    try:
        xl = pd.ExcelFile(file_path)
        all_sheets = xl.sheet_names
        
        # Helper to find sheets even with slight name differences
        def find_sheet(keyword):
            for name in all_sheets:
                if keyword.lower() in name.lower():
                    return name
            return None

        sheet1 = find_sheet("Tier-1") or find_sheet("Tier 1")
        sheet2 = find_sheet("Tier-2") or find_sheet("Tier 2")
        sheet3 = find_sheet("Tier-3") or find_sheet("Tier 3")

        if not sheet1 or not sheet2:
            st.error(f"Could not find Tier sheets. Available sheets: {all_sheets}")
            return None

        # Load sheets (skipping metadata rows)
        t1 = pd.read_excel(file_path, sheet_name=sheet1, skiprows=3)
        t2 = pd.read_excel(file_path, sheet_name=sheet2, skiprows=3)
        t3 = pd.read_excel(file_path, sheet_name=sheet3, skiprows=2)

        # Mapping for cleaner visualization
        country_fix = {'US': 'United States', 'UK': 'United Kingdom', 'TT': 'Taiwan', 'KS': 'South Korea'}

        # Process Tier 1 & 2 (they have a Country column)
        t1_2 = pd.concat([t1, t2])
        t1_2['Final_Country'] = t1_2['Country'].str.strip().replace(country_fix)

        # Process Tier 3 (extract from Ticker like 'AMD US Equity')
        def get_country_t3(ticker):
            if pd.isna(ticker): return "Unknown"
            parts = str(ticker).split(' ')
            if len(parts) > 1:
                return country_fix.get(parts[1], parts[1])
            return "Unknown"
        
        t3['Final_Country'] = t3['Ticker'].apply(get_country_t3)

        # Combine everything
        combined = pd.concat([t1_2, t3])
        val_col = 'Relationship Value (Q) (Mln) (USD)'
        combined[val_col] = pd.to_numeric(combined[val_col], errors='coerce')
        
        return combined.dropna(subset=[val_col])

    except Exception as e:
        st.error(f"Error reading file: {e}")
        return None

# Execution
if FILE_NAME in [f for f in import_os_list := __import__('os').listdir('.')]:
    df = load_data(FILE_NAME)
    if df is not None:
        stats = df.groupby('Final_Country')['Relationship Value (Q) (Mln) (USD)'].sum().reset_index()
        
        # Plotly Map
        fig = px.choropleth(stats, 
                            locations="Final_Country", 
                            locationmode='country names',
                            color="Relationship Value (Q) (Mln) (USD)",
                            hover_name="Final_Country",
                            color_continuous_scale="Reds")
        
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("Data Summary")
        st.dataframe(stats.sort_values(by='Relationship Value (Q) (Mln) (USD)', ascending=False))
else:
    st.warning(f"File '{FILE_NAME}' not found in GitHub repository. Please check the spelling.")
