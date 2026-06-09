import streamlit as st
import pandas as pd

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
            <span class="live-text">ALWAYS LIVE STREAMING</span>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")

    # Baki ka saara code tumhara same rahega
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

    if st.button("🔄 Refresh Inventory Data"):
        st.cache_data.clear()
        st.rerun()
