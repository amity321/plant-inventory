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

if check_password():
    st.header("📋 Live Instrumentation Spares & Field Status")
    st.write("Fetching live data directly from Google Forms Response Sheet Maintained by A. Jangra.")

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

    try:
        # Cache-buster to get fresh live values on page refresh
        live_url = f"{google_sheet_url}&t={int(time.time())}"
        df = pd.read_csv(live_url)
        
        # Clean column names (removes accidental whitespaces)
        df.columns = df.columns.str.strip()
        
        # Drop completely empty rows where Instrument Name is missing
        df = df.dropna(subset=["Instrument Name"])

        # Column Layout Mapping (Matching your updated Google Sheet)
        NAME_COL = "Instrument Name"
        SPECS_COL = "Specs"
        FIELD_COL = "Existing Instrument on Field"
        SPARES_M7_COL = "Remaining Spares in M7"
        SPARES_SHOP_COL = "Remaining Spares in Shop-Floor"
        TOTAL_SPARES_COL = "Total Spares"
        HEALTHY_STOCK_COL = "Healthy Stock"
        SHORTFALL_EXCESS_COL = "Shortfall / Excess"
        
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
            healthy_stock = int(float(row[HEALTHY_STOCK_COL])) if pd.notna(row[HEALTHY_STOCK_COL]) else 0
            shortfall_excess = int(float(row[SHORTFALL_EXCESS_COL])) if pd.notna(row[SHORTFALL_EXCESS_COL]) else 0
            
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
                    st.metric(label="🎯 Healthy Stock", value=f"{healthy_stock} Nos")
                
                with col_status:
                    # SMART COLOR LOGIC: Negative turns RED (Inverse), Positive turns GREEN (Normal)
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
