import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Plant Instrumentation Inventory", layout="wide", page_icon="🏭")

# Helper function to render rows using fallback display wrapper
def render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True):
    inst_name = str(row[NAME_COL]).strip()
    full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
    
    field_count = safe_int(row[FIELD_COL])
    spares_m7 = safe_int(row[SPARES_M7_COL])
    spares_shop = safe_int(row[SPARES_SHOP_FLOOR_COL if 'SPARES_SHOP_FLOOR_COL' in globals() else SPARES_SHOP_COL])
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

    if shortfall_excess < 0:
        status_html = f'<div class="status-badge status-shortfall">🚨 Shortfall ({shortfall_excess})</div>'
    elif shortfall_excess > 0:
        status_html = f'<div class="status-badge status-surplus">✅ Surplus (+{shortfall_excess})</div>'
    else:
        status_html = '<div class="status-badge status-balanced">👌 Balanced (0)</div>'

    card_html = f"""
    <div class="inventory-card">
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: sans-serif;">
            <div style="flex: 2; min-width: 180px;">
                <h4 style="margin:0; color:#0f172a; font-size:18px;">{inst_name if show_name else ""}</h4>
            </div>
            <div style="flex: 2.5; min-width: 220px;">
                <div class="specs-box"><b>Specs:</b> {cleaned_spec}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">On Field</div><div class="metric-val">{field_count}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">M7 store</div><div class="metric-val">{spares_m7}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">Shopfloor</div><div class="metric-val">{spares_shop}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">Total</div><div class="metric-val">{total_spares}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">AI Target</div><div class="metric-val">{healthy_stock}</div>
            </div>
            <div style="flex: 1.5; min-width: 130px; text-align: center;">
                {status_html}
            </div>
        </div>
    </div>
    """
    st.components.v1.html(card_html, height=110, scrolling=False)

# --- FIXED LOGIC: Injection directly through safe config placeholders ---
def inject_custom_css():
    css = """
    <style>
    .stApp {
        background-color: #f8fafc; 
    }
    h1, h2, h3 {
        color: #1e293b !important; 
        font-family: sans-serif; 
    }
    .inventory-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    .metric-box {
        text-align: center; 
        padding: 10px; 
        background-color: #f1f5f9; 
        border-radius: 6px; 
    }
    .metric-val {
        font-size: 20px; 
        font-weight: 700; 
        color: #0f172a; 
    }
    .metric-lbl {
        font-size: 11px; 
        text-transform: uppercase; 
        color: #64748b; 
        margin-bottom: 4px;
    }
    .status-badge {
        display: inline-block; 
        padding: 6px 12px; 
        border-radius: 20px; 
        font-size: 13px;
        font-weight: 600; 
        text-align: center; 
        width: 100%; 
    }
    .status-shortfall { background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }
    .status-surplus { background-color: #dcfce7; color: #16a34a; border: 1px solid #86efac; }
    .status-balanced { background-color: #e0f2fe; color: #0284c7; border: 1px solid #7dd3fc; }
    .specs-box {
        background-color: #f8fafc; 
        border-left: 4px solid #475569; 
        padding: 10px;
        border-radius: 4px; 
        font-size: 13px; 
        color: #334155; 
    }
    /* Shift Roster Styling */
    .shift-container {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 8px;
        border: 1px solid #cbd5e1;
        margin-bottom: 20px;
        font-family: sans-serif;
    }
    .shift-title {
        font-size: 14px;
        font-weight: 700;
        color: #1e293b;
        margin-bottom: 12px;
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 6px;
    }
    .shift-row {
        font-size: 13.5px;
        margin-bottom: 8px;
        color: #334155;
        line-height: 1.4;
    }
    .emp-names {
        font-weight: 700 !important;
        color: #0f172a !important;
    }
    </style>
    """
    st.components.v1.html(css, height=0, width=0)

# Password Protection
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

# Roster Parsing Engine
def get_today_shifts(timestamp):
    shift_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=564394831&single=true&output=csv"
    try:
        shift_df = pd.read_csv(f"{shift_csv_url}&t={timestamp}", header=None)
        
        if shift_df.empty:
            return None, "Database Link returned empty data."
            
        shift_df = shift_df.fillna("").astype(str).map(lambda x: x.strip())
        
        name_col_idx = None
        header_row_idx = None
        
        for r_idx in range(min(6, len(shift_df))):
            row_vals = list(shift_df.iloc[r_idx])
            if "Name" in row_vals:
                name_col_idx = row_vals.index("Name")
                header_row_idx = r_idx
                break
                
        if name_col_idx is None:
            name_col_idx = 0
            header_row_idx = 0
            
        day_str = str(datetime.now().day)
        target_col_idx = None
        
        for r_idx in range(min(4, len(shift_df))):
            row_vals = list(shift_df.iloc[r_idx])
            if day_str in row_vals:
                target_col_idx = row_vals.index(day_str)
                break
                
        if target_col_idx is None:
            sample_cols = list(shift_df.iloc[header_row_idx])[:6]
            return None, f"Day '{day_str}' not found. Sample Header: {sample_cols}"
            
        shifts = {"A": [], "B": [], "C": [], "O": []}
        
        start_row = header_row_idx + 1
        for i in range(start_row, len(shift_df)):
            emp_name = shift_df.iloc[i, name_col_idx]
            if not emp_name or emp_name.lower() in ["name", "nan", ""]:
                continue
                
            duty_code = shift_df.iloc[i, target_col_idx].upper()
            if duty_code in shifts:
                shifts[duty_code].append(emp_name)
                
        return shifts, None
    except Exception as e:
        return None, f"System Error: {str(e)}"

# Main Application Entry
if check_password():
    inject_custom_css()
    
    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    # --- SIDEBAR ROSTER ENGINE (WITH BOLD NAMES CSS) ---
    st.sidebar.markdown('<div class="shift-container">', unsafe_allow_html=True)
    st.sidebar.markdown(f'<div class="shift-title">⏰ Today\'s Shift Schedule ({datetime.now().strftime("%d-%b")})</div>', unsafe_allow_html=True)
    
    roster_data, err_msg = get_today_shifts(st.session_state["data_timestamp"])
    
    if err_msg:
        st.sidebar.error(err_msg)
    elif roster_data:
        shift_a = ", ".join(roster_data["A"]) if roster_data["A"] else "None Assigned"
        shift_b = ", ".join(roster_data["B"]) if roster_data["B"] else "None Assigned"
        shift_c = ", ".join(roster_data["C"]) if roster_data["C"] else "None Assigned"
        shift_o = ", ".join(roster_data["O"]) if roster_data["O"] else "None Assigned"
        
        # Wrapped employee variables inside 'emp-names' span for bold text styling
        st.sidebar.markdown(f'<div class="shift-row">🟢 <b>A-Shift:</b> <span class="emp-names">{shift_a}</span></div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div class="shift-row">🔵 <b>B-Shift:</b> <span class="emp-names">{shift_b}</span></div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div class="shift-row">🟡 <b>C-Shift:</b> <span class="emp-names">{shift_c}</span></div>', unsafe_allow_html=True)
        st.sidebar.markdown(f'<div class="shift-row">🔴 <b>Weekly Off:</b> <span class="emp-names">{shift_o}</span></div>', unsafe_allow_html=True)
    st.sidebar.markdown('</div>', unsafe_allow_html=True)

    # Styled Dashboard Header Panel
    st.components.v1.html("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); 
                    padding: 22px 25px; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 15px rgba(0,0,0,0.06); 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h1 style="color: #ffffff !important; margin: 0; font-size: 26px; font-weight: 700; letter-spacing: -0.5px;">
                🏭 Area 02/03 Instrumentation Inventory Dashboard
            </h1>
            <p style="color: #94a3b8 !important; margin: 6px 0 0 0; font-size: 13px; font-weight: 400; letter-spacing: 0.2px;">
                Live Instrumentation Spares Tracking Sheet &bull; Managed by <span style="color: #38bdf8; font-weight: 600;">Amit Jangra</span>
            </p>
        </div>
    """, height=105)
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    google_sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"

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
        
        st.sidebar.header("🔍 Filter Controls")
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
            else:
                total_current_spares = sum(safe_int(r[TOTAL_SPARES_COL]) for _, r in sub_df.iterrows())
                
                st.markdown(f"""
                <div style="background-color: #e2e8f0; padding: 10px 14px; border-radius: 6px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 16px !important; font-weight: 800 !important; color: #0f172a !important; font-family: sans-serif;">
                        📂 {current_name} — ({entry_count} Variants Grouped) | Combined Stock: {total_current_spares}
                    </span>
                    <span style="font-size: 12px; color: #475569; font-weight: bold; margin-right: 5px;">▼</span>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(" "):
                    for idx, row in sub_df.iterrows():
                        render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=False)

    except Exception as e:
        st.error(f"Error accessing Google Sheets Database: {e}")

    if st.sidebar.button("🔒 Secure Log Out"):
        st.session_state["password_correct"] = False
        st.rerun()

    if st.sidebar.button("🔄 Sync Live Data Now"):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
