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
        CORRECT_PASSWORD = "0203" 
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

# Cached data fetching
@st.cache_data(ttl=60)
def fetch_data(url, timestamp):
    live_url = f"{url}&t={timestamp}"
    df = pd.read_csv(live_url)
    return df

# Helper function to render a single row in the exact original 8-column layout
def render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True):
    inst_name = str(row[NAME_COL]).strip()
    full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
    
    field_count = safe_int(row[FIELD_COL])
    spares_m7 = safe_int(row[SPARES_M7_COL])
    spares_shop = safe_int(row[SPARES_SHOP_COL])
    total_spares = safe_int(row[TOTAL_SPARES_COL])
    
    # AI Inventory Rule Engine
    name_lower = inst_name.lower()
    if "transmitter" in name_lower or "converter" in name_lower:
        healthy_stock = max(2, int(field_count * 0.20))
    elif "element" in name_lower or "switch" in name_lower or "probe" in name_lower:
        healthy_stock = max(3, int(field_count * 0.30))
    else:
        healthy_stock = max(2, int(field_count * 0.15))
    
    shortfall_excess = total_spares - healthy_stock
    cleaned_spec = full_spec.replace('•', '').strip()

    with st.container():
        col_name, col_specs, col_field, col_m7, col_shop, col_total, col_healthy, col_status = st.columns([2, 2.5, 1.2, 1.2, 1.2, 1.2, 1.2, 1.5])
        
        with col_name:
            if show_name:
                st.subheader(inst_name)
            else:
                st.write("") # Grouped entries ke andar baar-baar naam repeat nahi hoga
        
        with col_specs:
            st.markdown("**Technical Specs:**")
            st.info(cleaned_spec)
        
        with col_field:
            st.metric(label="On Field", value=f"{field_count}")
        
        with col_m7:
            st.metric(label="📦 M7 Spares", value=f"{spares_m7}")
        
        with col_shop:
            st.metric(label="⚙️ Shop-Floor Spares", value=f"{spares_shop}")
        
        with col_total:
            st.metric(label="📊 Total Spares", value=f"{total_spares}")

        with col_healthy:
            st.metric(label="🤖 AI Target Stock", value=f"{healthy_stock}")
        
        with col_status:
            if shortfall_excess < 0:
                st.metric(label="🚨 Stock Status", value=f"{shortfall_excess}", delta="Shortfall!", delta_color="inverse")
            elif shortfall_excess > 0:
                st.metric(label="✅ Stock Status", value=f"+{shortfall_excess}", delta="Excess (Surplus)", delta_color="normal")
            else:
                st.metric(label="👌 Stock Status", value="Balanced", delta="Target Met", delta_color="normal")

if check_password():
    st.header("📋 Live Instrumentation Spares")
    st.write("Fetching live data directly from Google Forms Response Sheet Maintained by A. Jangra.")

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    try:
        df = fetch_data(google_sheet_url, st.session_state["data_timestamp"])
        df.columns = df.columns.str.strip()
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

        # Sidebar Filtering DataFrame level par hi apply kar dete hain
        if selected_instrument != "All":
            df = df[df[NAME_COL].str.strip() == selected_instrument]

        # --- DYNAMIC GROUPING LOGIC ---
        # Pata karo ki kis instrument ke kitne entries hain
        name_counts = df[NAME_COL].value_counts()

        # Pure items ko iterate karne ke liye unique names ka order nikalte hain
        unique_names_ordered = df[NAME_COL].unique()

        for current_name in unique_names_ordered:
            sub_df = df[df[NAME_COL] == current_name]
            entry_count = len(sub_df)

            if entry_count == 1:
                # Agar sirf 1 entry h, toh bina scroll/expander ke seedha layout me render karo
                row = sub_df.iloc[0]
                render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True)
                st.markdown("---")
            else:
                # Agar multiple entries hain (same instrument name), toh combine karke expander lagao
                total_current_spares = sum(safe_int(r[TOTAL_SPARES_COL]) for _, r in sub_df.iterrows())
                
                with st.expander(f"📂 {current_name} ({entry_count} Entries Found) | Combined Stock: {total_current_spares}"):
                    st.caption("Multiple models/specs found for this instrument:")
                    for idx, row in sub_df.iterrows():
                        # Expander ke andar same format columns me data dikhega (lekin name blank rahega taaki clean lage)
                        render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=False)
                        st.markdown("<hr style='margin:0.5em 0px; border-style: dashed;'>", unsafe_allowed_code=True)
                st.markdown("---")

    except Exception as e:
        st.error(f"Error reading live Google Sheet: {e}")

    # Sidebar Navigation Buttons
    if st.sidebar.button("🔒 Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    if st.sidebar.button("🔄 Refresh Inventory Data"):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
