import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Plant Intranet Inventory", layout="wide", page_icon="🏭")

# 2. Password Protection (Keeping your working auth logic)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Plant Intranet Inventory Access")
    user_password = st.text_input("Enter Password", type="password")
    if user_password:
        # Define your CORRECT_PASSWORD somewhere or replace below
        CORRECT_PASSWORD = "0203" 
        if user_password == CORRECT_PASSWORD:
            st.session_state["password_correct"] = True
            st.sidebar.success("🔓 Access Granted")
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")
    return False

if check_password():
    st.header("📋 Live Instrumentation Spares & Field Status")
    st.write("Fetching live data directly from Google Forms Response Sheet Maintained by A. Jangra.")

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

    try:
        # Cache-buster to get fresh live values on refresh
        live_url = f"{google_sheet_url}&t={int(time.time())}"
        df = pd.read_csv(live_url)
        
        # Clean column names (removes accidental spaces)
        df.columns = df.columns.str.strip()
        
        # Drop completely empty rows where Instrument Name is missing
        df = df.dropna(subset=["Instrument Name"])

        # Updated Columns matching your new "item.jpg" excel layout
        NAME_COL = "Instrument Name"
        SPECS_COL = "Specs"
        FIELD_COL = "Existing Instrument on Field"
        SPARES_M7_COL = "Remaining Spares in M7"
        SPARES_SHOP_COL = "Remaining Spares in Shop-Floor"
        TOTAL_SPARES_COL = "Total Spares"
        
        # --- SIDEBAR FILTER ---
        st.sidebar.header("🔍 Filter Options")
        all_instruments = ["All"] + list(df[NAME_COL].dropna().unique())
        selected_instrument = st.sidebar.selectbox("Filter by Instrument Type:", all_instruments)
        st.markdown("---")

        # --- DYNAMIC DATA LOOPING ---
        for index, row in df.iterrows():
            inst_name = str(row[NAME_COL]).strip()

            # Sidebar Filter Logic
            if selected_instrument != "All" and inst_name != selected_instrument:
                continue
                
            # Safely extract values from row
            full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
            
            # Convert numeric values safely to integers
            field_count = int(float(row[FIELD_COL])) if pd.notna(row[FIELD_COL]) else 0
            spares_m7 = int(float(row[SPARES_M7_COL])) if pd.notna(row[SPARES_M7_COL]) else 0
            spares_shop = int(float(row[SPARES_SHOP_COL])) if pd.notna(row[SPARES_SHOP_COL]) else 0
            total_spares = int(float(row[TOTAL_SPARES_COL])) if pd.notna(row[TOTAL_SPARES_COL]) else 0
            
            # Clean technical specs string formatting markers
            cleaned_spec = full_spec.replace('•', '').strip()

            # Responsive Layout Container
            with st.container():
                # Adjusted column ratios to beautifully accommodate 3 distinct spare tracking metrics
                col_name, col_specs, col_field, col_m7, col_shop, col_total = st.columns([2, 3, 1.5, 1.5, 1.5, 1.5])
                
                with col_name:
                    st.subheader(inst_name)
                
                with col_specs:
                    st.markdown("**Technical Specs:**")
                    st.info(cleaned_spec)
                
                with col_field:
                    st.metric(label="On Field  installed", value=f"{field_count} Nos")
                
                with col_m7:
                    st.metric(label="📦 M7 Spares", value=f"{spares_m7} Nos")
                
                with col_shop:
                    st.metric(label="⚙️ Shop-floor Spares", value=f"{spares_shop} Nos")
                
                with col_total:
                    # Low stock warning based on total combined stock
                    if total_spares <= 1:
                        st.metric(label="⚠️ Total Spares", value=f"{total_spares} Left", delta="Low Stock!", delta_color="inverse")
                    else:
                        st.metric(label="📊 Total Spares", value=f"{total_spares} Avail")
            
            st.markdown("---")

    except Exception as e:
        st.error(f"Error reading live Google Sheet: {e}")

    # Sidebar Navigation/Utility Buttons
    if st.sidebar.button("🔒 Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    if st.sidebar.button("🔄 Refresh Inventory Data"):
        st.cache_data.clear()
        st.rerun()
