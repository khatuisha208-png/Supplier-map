import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Supply Chain Dashboard", layout="wide")

# EXACT filename on your GitHub
FILE_NAME = '17030125283_Isha Khatu_procurement_assignment.xlsx'

st.title("🌍 Global Procurement Map")

@st.cache_data
def load_and_clean_data(file):
    # 1. Load the Excel File
    xl = pd.ExcelFile(file)
    sheet_names = xl.sheet_names
    
    # 2. Find the right sheets even if names vary slightly
    s1 = [s for s in sheet_names if 'Tier-1' in s or 'Tier 1' in s][0]
    s2 = [s for s in sheet_names if 'Tier-2' in s or 'Tier 2' in s][0]
    s3 = [s for s in sheet_names if 'Tier-3' in s or 'Tier 3' in s][0]

    # 3. Read sheets and find the header automatically
    # We look for the row that contains 'Ticker' or 'Company'
    def read_clean_sheet(s_name):
        df_raw = pd.read_excel(file, sheet_name=s_name)
        # Find header row
        for i, row in df_raw.iterrows():
            if 'Ticker' in row.values or 'Company Name' in row.values:
                df_raw.columns = row
                df_raw = df_raw.iloc[i+1:].reset_index(drop=True)
                break
        return df_raw

    df1 = read_clean_sheet(s1)
    df2 = read_clean_sheet(s2)
    df3 = read_clean_sheet(s3)

    # 4. Standardize Country Mapping
    mapping = {'US': 'USA', 'UK': 'United Kingdom', 'England': 'United Kingdom', 'TT': 'Taiwan', 'KS': 'South Korea'}

    def fix_country(row):
        # For Tier 1 & 2 use 'Country' column
        if 'Country' in row and pd.notna(row['Country']):
            return mapping.get(str(row['Country']).strip(), str(row['Country']).strip())
        # For Tier 3 derive from Ticker
        if 'Ticker' in row and pd.notna(row['Ticker']):
            parts = str(row['Ticker']).split(' ')
            if len(parts) > 1:
                return mapping.get(parts[1], parts[1])
        return "Unknown"

    df1['Final_Country'] = df1.apply(fix_country, axis=1)
    df2['Final_Country'] = df2.apply(fix_country, axis=1)
    df3['Final_Country'] = df3.apply(fix_country, axis=1)

    # 5. Combine and Numeric Conversion
    combined = pd.concat([df1, df2, df3])
    val_col = 'Relationship Value (Q) (Mln) (USD)'
    combined[val_col] = pd.to_numeric(combined[val_col], errors='coerce')
    
    return combined.dropna(subset=[val_col])

try:
    data = load_and_clean_data(FILE_NAME)
    
    # Create Map Data
    map_df = data.groupby('Final_Country')['Relationship Value (Q) (Mln) (USD)'].sum().reset_index()

    # Visualization
    fig = px.choropleth(map_df, 
                        locations="Final_Country", 
                        locationmode='country names',
                        color="Relationship Value (Q) (Mln) (USD)",
                        hover_name="Final_Country",
                        color_continuous_scale="Viridis")
    
    st.plotly_chart(fig, use_container_width=True)
    st.dataframe(map_df.sort_values(by="Relationship Value (Q) (Mln) (USD)", ascending=False))

except Exception as e:
    st.error(f"Critical Error: {e}")
    st.info("Check if your file name on GitHub is exactly: " + FILE_NAME)
