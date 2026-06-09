# 1. Write the Streamlit app code into a file inside Colab

import streamlit as st
import pandas as pd

st.set_page_config(page_title="Plant Intranet Inventory", layout="wide", page_icon="🏭")
st.title("🏭 Plant Intranet - Instrumentation Inventory Tracker (02/03 Area)")
st.markdown("---")

# Aapka public link
google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

try:
    df = pd.read_csv(google_sheet_url)
    df.columns = df.columns.str.strip()

    NAME_COL = "Instrument Name"
    SPECS_COL = "Specs"
    FIELD_COL = "Existing Instrument on Field"
    SPARES_COL = "Remaining Spares"

    target_instruments = [
        {"name": "Belt Weigher Transmitter", "spec_keywords": "Siemens"},
        {"name": "Conductivity Transmitter", "spec_keywords": "Power Supply"},
        {"name": "Flow Transmitter", "spec_keywords": "YOKOGAWA"},
        {"name": "Flow Transmitter", "spec_keywords": "KROHNE"},
        {"name": "Level Transmitter", "spec_keywords": "Ultrasonic"},
        {"name": "Level Transmitter", "spec_keywords": "Radar"}
    ]

    st.header("📋 Live Instrumentation Spares & Field Status")
    st.write("Fetching live data directly from Google Forms Response Sheet Maintained by A. Jangra.")
    st.markdown(" ")

    for inst in target_instruments:
        matched_row = df[
            (df[NAME_COL].str.strip() == inst["name"]) & 
            (df[SPECS_COL].str.contains(inst["spec_keywords"], case=False, na=False))
        ]
        
        if not matched_row.empty:
            full_spec = matched_row[SPECS_COL].values[0]
            field_count = matched_row[FIELD_COL].values[0]
            spares_count = matched_row[SPARES_COL].values[0]
            
            field_count = int(float(field_count)) if pd.notna(field_count) else 0
            spares_count = int(float(spares_count)) if pd.notna(spares_count) else 0

            with st.container():
                col_name, col_specs, col_field, col_spares = st.columns([2.5, 3.5, 2, 2])
                with col_name:
                    st.subheader(inst["name"])
                with col_specs:
                    st.markdown("**Technical Specs:**")
                    st.info(f"{full_spec}")
                with col_field:
                    st.metric(label="Deployed on Field", value=f"{field_count} Nos")
                with col_spares:
                    if spares_count <= 1:
                        st.metric(label="⚠️ Workshop Spares", value=f"{spares_count} Left", delta="Low Stock!", delta_color="inverse")
                    else:
                        st.metric(label="✅ Workshop Spares", value=f"{spares_count} Available")
            st.markdown("---")

except Exception as e:
    st.error(f"Error reading live Google Sheet: {e}")

st.button("🔄 Refresh Inventory Data")
