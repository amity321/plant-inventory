import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Plant Intranet Inventory", layout="wide", page_icon="🏭")

# --- FIXED FOR PYTHON 3.14: Native Streamlit HTML injection without markdown wrappers ---
st.html("""
    <style>
    div[data-testid="stAppViewContainer"] {
        background-color: #f1f5f9 !important;
    }
    div[data-testid="stMetricContainer"] {
        background-color: #ffffff !important; 
        border: 1px solid #cbd5e1 !important; 
        border-radius: 8px !important; 
        padding: 12px !important; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.04) !important;
    }
    </style>
""")

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

# Safe conversion function
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

# Helper function to render rows
def render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True):
    inst_name = str(row[NAME_COL]).strip()
    full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
    
    field_count = safe_int(row[FIELD_COL])
    spares_m7 = safe_int(row[SPARES_M7_COL])
    spares_shop = safe_int(row[SPARES_SHOP_COL])
    total_spares = safe_int(row[TOTAL_SPARES_COL])
    
    name_lower = inst_name.lower()
    if "transmitter" in name_lower or "converter" in name_lower:
        healthy_stock = max(2, int(field_count * 0.20))
    elif "element" in name_lower or "switch" in name_lower or "probe" in name_lower:
        healthy_stock = max(3, int(field_count * 0.30))
    else:
        healthy_stock = max(2, int(field_count * 0.15))
    
    shortfall_excess = total_spares - healthy_stock
    cleaned_spec = full_spec.replace('•', '').strip()

    # Dynamic status indicators using metrics mapping
    if shortfall_excess < 0:
        status_lbl = "🚨 SHORTFALL"
        status_val = f"{shortfall_excess} Spares"
        delta_msg = "Action Needed!"
        d_color = "inverse"
    elif shortfall_excess > 0:
        status_lbl = "✅ SURPLUS"
        status_val = f"+{shortfall_excess} Stock"
        delta_msg = "Safe Level"
        d_color = "normal"
    else:
        status_lbl = "👌 BALANCED"
        status_val = "Perfect"
        delta_msg = "Target Met"
        d_color = "normal"

    with st.container():
        col_name, col_specs, col_field, col_m7, col_shop, col_total, col_healthy, col_status = st.columns([1.8, 2.2, 1.1, 1.1, 1.1, 1.1, 1.1, 1.4])
        
        with col_name:
            if show_name:
                st.markdown(f"<div style='padding-top:15px;'><h3 style='color:#0f172a; margin:0;'>{inst_name}</h3></div>", unsafe_allowed_html=True)
            else:
                st.write("")
        
        with col_specs:
            st.markdown(f"<div style='background-color:#f8fafc; padding:10px; border-radius:6px; border-left:4px solid #64748b; font-size:13px; margin-top:8px;'><b>Specs:</b><br>{cleaned_spec}</div>", unsafe_allowed_html=True)
        
        with col_field:
            st.metric(label="On Field", value=str(field_count))
        
        with col_m7:
            st.metric(label="📦 M7 Store", value=str(spares_m7))
        
        with col_shop:
            st.metric(label="⚙️ Floor", value=str(spares_shop))
        
        with col_total:
            st.metric(label="📊 Total", value=str(total_spares))

        with col_healthy:
            st.metric(label="🤖 Target", value=str(healthy_stock))
        
        with col_status:
            st.metric(label=status_lbl, value=status_val, delta=delta_msg, delta_color=d_color)

# Main Application Entry
if check_password():
    # Styled Dashboard Header Panel (Industrial Theme Banner via Safe st.html alternative)
    st.html("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); font-family: sans-serif;">
            <h1 style="color: #ffffff !important; margin: 0; font-size: 28px; letter-spacing: 0.5px;">🏭 Plant Instrumentation Live Inventory</h1>
            <p style="color: #94a3b8 !important; margin: 5px 0 0 0; font-size: 14px;">Real-time automated control loop buffer tracking matrix • Maintained by A. Jangra</p>
        </div>
    """)

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    try:
        df = fetch_data(google_sheet_url, st.session_state["data_timestamp"])
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Instrument Name"])

        NAME_COL = "Instrument Name"
        SPECS_COL = "Specs"
        FIELD_COL = "Existing Instrument on Field"
        SPARES_M7_COL = "Remaining Spares in M7"
        SPARES_SHOP_COL = "Remaining Spares in Shop-Floor"
        TOTAL_SPARES_COL = "Total Spares"
        
        st.sidebar.header("🔍 Control Filters")
        all_instruments = ["All System Data"] + list(df[NAME_COL].dropna().unique())
        selected_instrument = st.sidebar.selectbox("Select Instrument Category:", all_instruments)
        st.sidebar.markdown("---")

        if selected_instrument != "All System Data":
            df = df[df[NAME_COL].str.strip() == selected_instrument]

        unique_names_ordered = df[NAME_COL].unique()

        for current_name in unique_names_ordered:
            sub_df = df[df[NAME_COL] == current_name]
            entry_count = len(sub_df)

            if entry_count == 1:
                row = sub_df.iloc[0]
                render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True)
                st.html("<div style='margin: 15px 0;'></div>")
            else:
                total_current_spares = sum(safe_int(r[TOTAL_SPARES_COL]) for _, r in sub_df.iterrows())
                
                with st.expander(f"📂 {current_name} — ({entry_count} Variants Grouped) | Combined Stock: {total_current_spares}"):
                    st.html("<div style='padding: 10px 0;'>")
                    for idx, row in sub_df.iterrows():
                        render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=False)
                        if idx != sub_df.index[-1]:
                            st.html("<hr style='border: 0; border-top: 1px dashed #cbd5e1; margin: 15px 0;'>")
                    st.html("</div>")
                st.html("<div style='margin: 15px 0;'></div>")

    except Exception as e:
        st.error(f"Error accessing Google Sheets Database: {e}")

    # Sidebar Options
    if st.sidebar.button("🔒 Secure Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    if st.sidebar.button("🔄 Sync Live Data Now"):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
