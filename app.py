import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Plant Intranet Inventory", layout="wide", page_icon="🏭")

# 2. Password Protection (Authentication Logic)
def check_password():
    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🔒 Plant Intranet Inventory Access")
    user_password = st.text_input("Enter Password", type="password")
    if user_password:
        CORRECT_PASSWORD = "your_actual_password_here" 
        if user_password == CORRECT_PASSWORD:
            st.session_state["password_correct"] = True
            st.sidebar.success("🔓 Access Granted")
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")
    return False

# Safe conversion function to handle text or empty cells gracefully
def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(float(str(val).strip()))
    except ValueError:
        return 0

if check_password():
    st.header("📋 Live Instrumentation Spares & Field Status (AI Rule Engine v1.0)")
    st.write("Fetching live data directly from Google Forms Response Sheet Maintained by A. Jangra.")

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

    try:
        # Cache-buster to get fresh live values on page refresh
        live_url = f"{google_sheet_url}&t={int(time.time())}"
        df = pd.read_csv(live_url)
        
        # Clean column names
        df.columns = df.columns.str.strip()
        
        # Drop completely empty rows where Instrument Name is missing
        df = df.dropna(subset=["Instrument Name"])

        # Column Layout Mapping
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
                
            # Safely extract specs string
            full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
            
            # Safe numeric conversion
            field_count = safe_int(row[FIELD_COL])
            spares_m7 = safe_int(row[SPARES_M7_COL])
            spares_shop = safe_int(row[SPARES_SHOP_COL])
            total_spares = safe_int(row[TOTAL_SPARES_COL])
            
            # --- METHOD 1: SMART AI INVENTORY RULE ENGINE ---
            name_lower = inst_name.lower()
            if "transmitter" in name_lower or "converter" in name_lower:
                # Critical Instruments: 20% of field count, minimum 2 spares
                healthy_stock = max(2, int(field_count * 0.20))
            elif "element" in name_lower or "switch" in name_lower or "probe" in name_lower:
                # Bulk/Consumable Instruments: 30% of field count, minimum 3 spares
                healthy_stock = max(3, int(field_count * 0.30))
            else:
                # Default safety buffer for any other categories
                healthy_stock = max(2, int(field_count * 0.15))
            
            # Dynamic calculation of status
            shortfall_excess = total_spares - healthy_stock
            
            # Clean technical specs string formatting markers
            cleaned_spec = full_spec.replace('•', '').strip()

            # Responsive Layout Container
            with st.container():
                col_name, col_specs, col_field, col_m7, col_shop, col_total, col_healthy, col_status = st.columns([2, 2.5, 1.2, 1.2, 1.2, 1.2, 1.2, 1.5])
                
                with col_name:
                    st.subheader(inst_name)
                
                with col_specs:
                    st.markdown("**Technical Specs:**")
                    st.info(cleaned_spec)
                
                with col_field:
                    st.metric(label="On Field", value=f"{field_count} Nos")
                
                with col_m7:
                    st.metric(label="📦 M7 Spares", value=f"{spares_m7} Nos")
                
                with col_shop:
                    st.metric(label="⚙️ Shop Spares", value=f"{spares_shop} Nos")
                
                with col_total:
                    st.metric(label="📊 Total Spares", value=f"{total_spares} Nos")

                with col_healthy:
                    st.metric(label="🤖 AI Target Stock", value=f"{healthy_stock} Nos")
                
                with col_status:
                    # Dynamic color-coding alert logic
                    if shortfall_excess < 0:
                        st.metric(
                            label="🚨 Stock Status", 
                            value=f"{shortfall_excess} Nos", 
                            delta="Shortfall!", 
                            delta_color="inverse"
                        )
                    elif shortfall_excess > 0:
                        st.metric(
                            label="✅ Stock Status", 
                            value=f"+{shortfall_excess} Nos", 
                            delta="Excess (Surplus)", 
                            delta_color="normal"
                        )
                    else:
                        st.metric(
                            label="👌 Stock Status", 
                            value="Balanced", 
                            delta="Target Met", 
                            delta_color="normal"
                        )
            
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
