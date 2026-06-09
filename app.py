import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Plant Intranet Inventory", layout="wide", page_icon="🏭")

# 2. Simple Password Protection Function
def check_password():
    """Returns True if the user had the correct password."""
    CORRECT_PASSWORD = "0203"  # Jo password tumne choose kiya

    if "password_correct" not in st.session_state:
        st.session_state["password_correct"] = False

    if st.session_state["password_correct"]:
        return True

    st.title("🏭 Plant Intranet - Instrumentation Inventory Tracker")
    st.subheader("🔒 Authorization Required")
    
    user_password = st.text_input("Enter Password to access the 02/03 Area Dashboard:", type="password")
    
    if user_password:
        if user_password == CORRECT_PASSWORD:
            st.session_state["password_correct"] = True
            st.sidebar.success("🔓 Access Granted")
            st.rerun()
        else:
            st.error("❌ Incorrect password. Please try again.")
            return False
    return False

# 3. Main App Execution
if check_password():
    st.title("🏭 Plant Intranet - Instrumentation Inventory Tracker (02/03 Area)")
    
    # --- RED BLINKING DOT CSS EFFECT ---
    st.markdown("""
        <style>
        .live-container {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
        }
        .blink-dot {
            width: 12px;
            height: 12px;
            background-color: #FF4B4B;
            border-radius: 50%;
            display: inline-block;
            animation: blinking 1.5s infinite ease-in-out;
        }
        .live-text {
            font-weight: bold;
            color: #FF4B4B;
            letter-spacing: 1px;
            font-size: 14px;
        }
        @keyframes blinking {
            0% { opacity: 0.2; box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
            50% { opacity: 1; box-shadow: 0 0 10px 4px rgba(255, 75, 75, 0.7); }
            100% { opacity: 0.2; box-shadow: 0 0 0 0 rgba(255, 75, 75, 0.4); }
        }
        </style>
        
        <div class="live-container">
            <span class="blink-dot"></span>
            <span class="live-text">LIVE STREAMING</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

    try:
        # Cache-buster to get fresh live values on refresh
        live_url = f"{google_sheet_url}&t={int(time.time())}"
        df = pd.read_csv(live_url)
        
        # Clean columns and drop completely empty rows
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Instrument Name"])

        NAME_COL = "Instrument Name"
        SPECS_COL = "Specs"
        FIELD_COL = "Existing Instrument on Field"
        SPARES_COL = "Remaining Spares"

        st.header("📋 Live Instrumentation Spares & Field Status")
        st.write("Fetching live data directly from Google Forms Response Sheet Maintained by A. Jangra.")
        
        # --- NEW SIDEBAR FILTER BASED ON INTRANET.PNG ---
        st.sidebar.header("🔍 Filter Options")
        all_instruments = ["All"] + list(df[NAME_COL].dropna().unique())
        selected_instrument = st.sidebar.selectbox("Filter by Instrument Type:", all_instruments)

        st.markdown(" ")

        # Loop dynamically through the dataframe rows based on the image entries
        for index, row in df.iterrows():
            inst_name = str(row[NAME_COL]).strip()
            
            # Sidebar Filter Logic
            if selected_instrument != "All" and inst_name != selected_instrument:
                continue
                
            full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
            field_count = row[FIELD_COL]
            spares_count = row[SPARES_COL]
            
            # Safely handle numbers and float conversions from Excel
            field_count = int(float(field_count)) if pd.notna(field_count) else 0
            spares_count = int(float(spares_count)) if pd.notna(spares_count) else 0

            with st.container():
                col_name, col_specs, col_field, col_spares = st.columns([2.5, 3.5, 2, 2])
                
                with col_name:
                    st.subheader(inst_name)
                
                with col_specs:
                    st.markdown("**Technical Specs:**")
                    # Display specs cleanly even if they have formatting markers
                    st.info(f"{full_spec.replace('•', '').strip()}")
                
                with col_field:
                    st.metric(label="Deployed on Field", value=f"{field_count} Nos")
                
                with col_spares:
                    # Logic matching your low stock threshold
                    if spares_count <= 1:
                        st.metric(label="⚠️ Workshop Spares", value=f"{spares_count} Left", delta="Low Stock!", delta_color="inverse")
                    else:
                        st.metric(label="✅ Workshop Spares", value=f"{spares_count} Available")
            
            st.markdown("---")

    except Exception as e:
        st.error(f"Error reading live Google Sheet: {e}")

    # Sidebar Logout Button
    if st.sidebar.button("🔒 Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    # Manual Data Force Refresh Button
    if st.button("🔄 Refresh Inventory Data"):
        st.rerun()
