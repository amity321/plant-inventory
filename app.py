import streamlit as st
import pandas as pd
pd.set_option('display.max_rows', None)
import time
from datetime import datetime, timedelta
import hashlib
import requests

# 1. Page Configuration
st.set_page_config(page_title="Master Instrumentation Dashboard", layout="wide", page_icon="🏭")

# --- GOOGLE APPS SCRIPT AUTH WEBHOOK URL ---
AUTH_API_URL = "https://script.google.com/macros/s/AKfycbwnf2s_JeEKydIm4xZE5Lc4MTj3D_A30hKIDOBqJa-ykjDbhgCkvL6YaTqG4myn2I52/exec"

def hash_pass(pwd: str) -> str:
    return hashlib.sha256(pwd.strip().encode()).hexdigest()

DEFAULT_HASH = hash_pass("nalco123")

def fetch_passwords_from_sheet():
    try:
        res = requests.get(AUTH_API_URL, timeout=6)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}

def update_password_in_sheet(area_key, new_password_hash):
    try:
        payload = {
            "area": area_key,
            "new_hash": new_password_hash
        }
        res = requests.post(AUTH_API_URL, json=payload, timeout=8)
        if res.status_code == 200 and "OK" in res.text:
            return True, "Success"
        return False, f"API Response: {res.text}"
    except Exception as e:
        return False, str(e)

# --- AREA CONFIGURATIONS ---
AREA_CONFIGS = {
    "Area 02/03": {
        "title": "Area 02/03 Instrumentation Inventory",
        "manager": "Er. Amit Jangra | P.No. 10372",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=1345118798&single=true&output=csv"
    },
    "Area 04/05": {
        "title": "Area 04/05 Instrumentation Inventory",
        "manager": "Er D.C. Mishra | P.No. 09074",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSZopDMRgkBThhmBF8NAXoBERx24tj7Ae2y6HlvimEHUhahXEWY8tmXoNDSM_MNlkDB7TfGpHB9I2H_/pub?gid=1836901304&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSZopDMRgkBThhmBF8NAXoBERx24tj7Ae2y6HlvimEHUhahXEWY8tmXoNDSM_MNlkDB7TfGpHB9I2H_/pub?gid=1951924870&single=true&output=csv"
    },
    "Area 06/07": {
        "title": "Area 06/07 Instrumentation Inventory",
        "manager": "Er R. Swarup | P.No. 10565",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vStPdBa-nm7i9eHjSxpyrIOyyu5VJZo77E4KF3tk2R9ewp0hK58RDVYBKiW5UsRD2DxBTrafX-CfJry/pub?gid=175582315&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vStPdBa-nm7i9eHjSxpyrIOyyu5VJZo77E4KF3tk2R9ewp0hK58RDVYBKiW5UsRD2DxBTrafX-CfJry/pub?gid=1371227319&single=true&output=csv"
    },
    "Area 08": {
        "title": "Area 08 Instrumentation Inventory",
        "manager": "Er P. Bagde | P.No. 09644",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMj_W_6-T0duFQ_XS8Yf9xTQPQvguuQP9P_aUwkKuiOZeT8BXSkAHeQspMlhXebcmz0ff-VZRdya-M/pub?gid=664188260&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMj_W_6-T0duFQ_XS8Yf9xTQPQvguuQP9P_aUwkKuiOZeT8BXSkAHeQspMlhXebcmz0ff-VZRdya-M/pub?gid=260669801&single=true&output=csv"
    },
    "Area 09/10": {
        "title": "Area 09/10 Instrumentation Inventory",
        "manager": "Er K. Kumar | P.No. 09643",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS7NvVXAcew2ZWcA_kSTmCQJk6OVq3RQfqGqCZ08jGKosNmTYWprvR4JUMC3-vXI28wF6HJ1B_Wk1uo/pub?gid=87821600&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS7NvVXAcew2ZWcA_kSTmCQJk6OVq3RQfqGqCZ08jGKosNmTYWprvR4JUMC3-vXI28wF6HJ1B_Wk1uo/pub?gid=1187023151&single=true&output=csv"
    },
    "SPP TG": {
        "title": "SPP TG Instrumentation Inventory",
        "manager": "Er H.S. Mallick | P.No. 10873",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPmgZl9jEQaGMQbxeOu0Xr_GtQ2P4_twAx2qNxUOjoYSvSW27vJsUgRtQB7XtIcU-bcCulPJLX3PLA/pub?gid=974689106&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPmgZl9jEQaGMQbxeOu0Xr_GtQ2P4_twAx2qNxUOjoYSvSW27vJsUgRtQB7XtIcU-bcCulPJLX3PLA/pub?gid=900388666&single=true&output=csv"
    },
    "SPP Boiler": {
        "title": "SPP Boiler Instrumentation Inventory",
        "manager": "Er Sachin Ray | P.No. 10913",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVTH56rybWjsWYThgCiTWzafjabniWhqHUUuXoVdqexuWIjrmvh65AtimfDlFNB5V4StSi5G4BWuKf/pub?gid=1937643350&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVTH56rybWjsWYThgCiTWzafjabniWhqHUUuXoVdqexuWIjrmvh65AtimfDlFNB5V4StSi5G4BWuKf/pub?gid=223018013&single=true&output=csv"
    },
    "C&I Sub Store": {
        "title": "C&I Sub Store Instrumentation Inventory",
        "manager": "Er Astha Singh | P.No. 10567",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbJUMrlU1bWLUsOt0tL-4xsBpsO2kt70Rq4am-OpMb7hsZZxe69JzLwBqT1EOLZtuU-PGkY-mx4EuZ/pub?gid=2014684236&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbJUMrlU1bWLUsOt0tL-4xsBpsO2kt70Rq4am-OpMb7hsZZxe69JzLwBqT1EOLZtuU-PGkY-mx4EuZ/pub?gid=158170506&single=true&output=csv"
    }
}

STOCK_MATRIX_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=868142398&single=true&output=csv"

# --- SESSION STATE INITIALIZATION ---
if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = {}

# --- MODAL: CHANGE PASSWORD (DIRECT TO GOOGLE SHEET) ---
@st.dialog("🔑 Change Area Password")
def change_password_dialog(area_key):
    st.markdown(f"**Area:** `{area_key}`")
    curr_pass = st.text_input("Current Password", type="password", key="curr_pwd_input")
    new_pass = st.text_input("New Password", type="password", key="new_pwd_input")
    confirm_pass = st.text_input("Confirm New Password", type="password", key="conf_pwd_input")
    
    if st.button("Update Password", use_container_width=True, type="primary"):
        c_curr = curr_pass.strip()
        c_new = new_pass.strip()
        c_conf = confirm_pass.strip()

        db = fetch_passwords_from_sheet()
        stored_val = str(db.get(area_key, "")).strip()

        # Matches against raw password in sheet, hashed password in sheet, or default nalco123
        is_curr_valid = (
            c_curr == stored_val or 
            hash_pass(c_curr) == stored_val or 
            c_curr == "nalco123" or 
            hash_pass(c_curr) == DEFAULT_HASH
        )

        if not is_curr_valid:
            st.error("❌ Current password is incorrect!")
        elif len(c_new) < 4:
            st.error("⚠️ New password must be at least 4 characters long.")
        elif c_new != c_conf:
            st.error("❌ New passwords do not match!")
        else:
            with st.spinner("Updating password in Google Sheet..."):
                success, msg = update_password_in_sheet(area_key, hash_pass(c_new))
                if success:
                    st.success("✅ Password successfully updated in Google Sheet!")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update password in Google Sheet: {msg}")

# --- LOGIN PROMPT SCREEN ---
def check_authentication(area_key):
    if st.session_state.get("auth_status", {}).get(area_key, False):
        return True

    st.markdown(f"""
        <div style="max-width: 480px; margin: 40px auto; background: #ffffff; padding: 30px; border-radius: 14px; border: 1.5px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.04); text-align: center;">
            <div style="font-size: 36px; margin-bottom: 8px;">🔒</div>
            <h2 style="color: #0f172a; margin: 0; font-size: 22px; font-weight: 700;">Protected Area Access</h2>
            <p style="color: #64748b; font-size: 13.5px; margin-top: 6px;">Enter password to view <b>{area_key}</b> data.</p>
        </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        pwd = st.text_input("Password", type="password", key=f"login_{area_key}", placeholder="Enter password...")
        if st.button("Unlock Portal 🔓", use_container_width=True, type="primary"):
            c_pwd = pwd.strip()
            db = fetch_passwords_from_sheet()
            stored_val = str(db.get(area_key, "")).strip()

            is_valid = (
                c_pwd == stored_val or 
                hash_pass(c_pwd) == stored_val or 
                c_pwd == "nalco123" or 
                hash_pass(c_pwd) == DEFAULT_HASH
            )

            if is_valid:
                if "auth_status" not in st.session_state:
                    st.session_state["auth_status"] = {}
                st.session_state["auth_status"][area_key] = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password. Contact C&I Admin.")
    return False

def clean_material_code(val):
    if pd.isna(val):
        return "N/A"
    s_val = str(val).strip()
    if s_val == "" or s_val.lower() == "nan":
        return "N/A"
    if s_val.endswith(".0"):
        s_val = s_val[:-2]
    return s_val

def resolve_columns(df):
    cols = df.columns
    mat_col, field_col, store_col, shop_col, total_col, specs_col, name_col = None, None, None, None, None, None, None
    for col in cols:
        c_low = col.lower()
        if not mat_col and ("code" in c_low or "mat" in c_low):
            mat_col = col
        elif not field_col and ("field" in c_low or "existing" in c_low):
            field_col = col
        elif not store_col and ("store" in c_low or "m7" in c_low or ("room" in c_low and "shop" not in c_low)):
            store_col = col
        elif not shop_col and ("shop" in c_low or "floor" in c_low):
            shop_col = col
        elif not total_col and "total" in c_low:
            total_col = col
        elif not specs_col and "spec" in c_low:
            specs_col = col
        elif not name_col and ("instrument" in c_low or "name" in c_low):
            name_col = col

    return {
        "name": name_col or "Instrument Name",
        "material": mat_col or "Material Code",
        "specs": specs_col or "Specs",
        "field": field_col or "Existing Instrument on Field",
        "store": store_col or "Remaining Spares in Store-Room",
        "shop": shop_col or "Remaining Spares in Shop-Floor",
        "total": total_col or "Total Spares"
    }

def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(float(str(val).strip()))
    except ValueError:
        return 0

def render_row(row, mapping, current_area_name):
    name_key = mapping["name"]
    mat_key = mapping["material"]
    specs_key = mapping["specs"]
    field_key = mapping["field"]
    store_key = mapping["store"]

    inst_name = str(row[name_key]).strip() if name_key in row and pd.notna(row[name_key]) else "No Name"
    mat_code = clean_material_code(row[mat_key]) if mat_key in row else "N/A"
    full_spec = str(row[specs_key]).strip() if specs_key in row and pd.notna(row[specs_key]) else "No Specs Added"
    
    field_count = safe_int(row[field_key]) if field_key in row else 0
    spares_store = safe_int(row[store_key]) if store_key in row else 0
    
    name_lower = inst_name.lower()
    if "transmitter" in name_lower or "converter" in name_lower:
        healthy_stock = max(2, int(field_count * 0.20))
    elif "element" in name_lower or "switch" in name_lower or "probe" in name_lower:
        healthy_stock = max(3, int(field_count * 0.30))
    else:
        healthy_stock = max(2, int(field_count * 0.15))
    
    shortfall_excess = spares_store - healthy_stock
    cleaned_spec = full_spec.replace('•', '').strip()

    if shortfall_excess < 0:
        status_html = f'<div class="status-badge status-shortfall">🚨 Shortfall ({shortfall_excess})</div>'
    elif shortfall_excess > 0:
        status_html = f'<div class="status-badge status-surplus">✅ Surplus (+{shortfall_excess})</div>'
    else:
        status_html = '<div class="status-badge status-balanced">👌 Balanced (0)</div>'

    show_name_flag = mapping.get("show_name", True)

    card_html = f"""
    <div class="inventory-card">
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="flex: 2; min-width: 180px;">
                <h4 style="margin:0; color:#0f172a; font-size:16px; font-weight:700;">{inst_name if show_name_flag else ""}</h4>
                <div style="font-size: 11px; color: #0284c7; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code}</div>
            </div>
            <div style="flex: 2.5; min-width: 200px;">
                <div class="specs-box"><b>Specs:</b> {cleaned_spec}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">On Field</div><div class="metric-val">{field_count}</div>
            </div>
            <div style="flex: 1; min-width: 110px;" class="metric-box">
                <div class="metric-lbl">Store-Room Stock</div><div class="metric-val">{spares_store}</div>
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
    st.components.v1.html(card_html, height=115, scrolling=False)

def inject_custom_css():
    css = """
    <style>
    .stApp { background-color: #f8fafc; }
    h1, h2, h3 { color: #1e293b !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    
    .inventory-card { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 14px 18px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
        border: 1px solid #e2e8f0; 
        margin-bottom: 15px; 
    }
    .metric-box { 
        text-align: center; 
        padding: 6px; 
        background-color: #f8fafc; 
        border-radius: 8px; 
        border: 1px solid #f1f5f9; 
    }
    .metric-val { 
        font-size: 17px; 
        font-weight: 700; 
        color: #0f172a; 
    }
    .metric-lbl { 
        font-size: 10px; 
        text-transform: uppercase; 
        color: #64748b; 
        font-weight: 600; 
        margin-bottom: 2px; 
    }
    .status-badge { 
        display: inline-block; 
        padding: 6px 10px; 
        border-radius: 20px; 
        font-size: 12px; 
        font-weight: 600; 
        text-align: center; 
        width: 100%; 
    }
    .status-shortfall { background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }
    .status-surplus { background-color: #dcfce7; color: #16a34a; border: 1px solid #86efac; }
    .status-balanced { background-color: #e0f2fe; color: #0284c7; border: 1px solid #7dd3fc; }
    .specs-box { 
        background-color: #f8fafc; 
        border-left: 3px solid #0284c7; 
        padding: 6px 10px; 
        border-radius: 6px; 
        font-size: 11.5px; 
        color: #334155; 
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_data(url, timestamp):
    live_url = f"{url}&t={timestamp}"
    df = pd.read_csv(live_url, dtype=str)
    return df

def calculate_real_consumption_from_log(target_material_code, removal_df, analysis_months=12):
    if removal_df is None or removal_df.empty:
        return 0.0, 0.0, 0
    try:
        df_log = removal_df.copy()
        df_log.columns = df_log.columns.str.strip()
        
        mat_col = next((c for c in df_log.columns if "material" in c.lower() or "code" in c.lower()), None)
        type_col = next((c for c in df_log.columns if "transaction" in c.lower() or "type" in c.lower()), None)
        time_col = next((c for c in df_log.columns if "timestamp" in c.lower() or "date" in c.lower()), None)
        
        if not mat_col or not time_col:
            return 0.0, 0.0, 0
            
        df_log["clean_mat"] = df_log[mat_col].apply(clean_material_code)
        item_log = df_log[df_log["clean_mat"] == str(target_material_code)].copy()
        
        if type_col:
            removal_keywords = ["remov", "issu", "withdraw", "consum"]
            mask = item_log[type_col].astype(str).str.lower().apply(lambda x: any(k in x for k in removal_keywords))
            item_log = item_log[mask]
            
        if item_log.empty:
            return 0.0, 0.0, 0
            
        item_log["Parsed_Date"] = pd.to_datetime(item_log[time_col], errors='coerce')
        item_log = item_log.dropna(subset=["Parsed_Date"])
        
        if item_log.empty:
            return 0.0, 0.0, 0
            
        cutoff_date = datetime.now() - timedelta(days=analysis_months * 30)
        recent_log = item_log[item_log["Parsed_Date"] >= cutoff_date]
        
        total_removals = len(recent_log)
        if total_removals == 0:
            return 0.0, 0.0, 0
            
        monthly_consumption = round(float(total_removals) / float(analysis_months), 2)
        replacement_cycle = round(1.0 / monthly_consumption, 1) if monthly_consumption > 0 else 0.0
        
        return monthly_consumption, replacement_cycle, total_removals
    except Exception:
        return 0.0, 0.0, 0

# --- URL QUERY PARAMETERS & ROUTING ---
query_params = st.query_params
url_area = query_params.get("area", None)
url_view = query_params.get("view", None)
url_pr_area = query_params.get("pr_area", None)

is_area_direct_mode = bool(url_area and url_area in AREA_CONFIGS)

if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = url_area if is_area_direct_mode else None

if "smart_intelligence_mode" not in st.session_state:
    st.session_state["smart_intelligence_mode"] = (url_view == "pr")

if "stock_matrix_mode" not in st.session_state:
    st.session_state["stock_matrix_mode"] = (url_view == "stock_matrix")

if "pr_selected_view" not in st.session_state:
    if is_area_direct_mode and st.session_state["smart_intelligence_mode"]:
        st.session_state["pr_selected_view"] = url_area
    else:
        st.session_state["pr_selected_view"] = url_pr_area

if "data_timestamp" not in st.session_state:
    st.session_state["data_timestamp"] = int(time.time())

inject_custom_css()

# --- SIDEBAR NAVIGATION CONTROLS ---
st.sidebar.markdown("### 🧭 Navigation & Security")

if is_area_direct_mode:
    if not st.session_state["smart_intelligence_mode"]:
        if st.sidebar.button("📈 Predictive PR Date", use_container_width=True):
            st.session_state["smart_intelligence_mode"] = True
            st.session_state["pr_selected_view"] = url_area
            st.query_params["area"] = url_area
            st.query_params["view"] = "pr"
            st.rerun()
    else:
        if st.sidebar.button("📦 Back to Area Stock", use_container_width=True):
            st.session_state["smart_intelligence_mode"] = False
            st.session_state["pr_selected_view"] = None
            st.query_params["area"] = url_area
            if "view" in st.query_params:
                del st.query_params["view"]
            st.rerun()
else:
    if st.sidebar.button("🏠 Home", use_container_width=True):
        st.session_state["smart_intelligence_mode"] = False
        st.session_state["stock_matrix_mode"] = False
        st.session_state["selected_area"] = None
        st.session_state["pr_selected_view"] = None
        st.query_params.clear()
        st.rerun()
        
    if st.sidebar.button("📈 Predictive PR Date", use_container_width=True):
        st.session_state["smart_intelligence_mode"] = True
        st.session_state["stock_matrix_mode"] = False
        st.session_state["selected_area"] = None
        st.session_state["pr_selected_view"] = None
        st.query_params["view"] = "pr"
        st.rerun()

    if st.sidebar.button("📊 Areawise Stock", use_container_width=True):
        st.session_state["stock_matrix_mode"] = True
        st.session_state["smart_intelligence_mode"] = False
        st.session_state["selected_area"] = None
        st.session_state["pr_selected_view"] = None
        st.query_params["view"] = "stock_matrix"
        st.rerun()

st.sidebar.markdown("---")

# --- AREAWISE STOCK MATRIX VIEWER ---
if st.session_state["stock_matrix_mode"] and not is_area_direct_mode:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 30px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 25px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">📊 Areawise Stock Matrix</h1>
            <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Live centralized stock overview across all operating areas.</p>
        </div>
    """, unsafe_allow_html=True)

    try:
        df_matrix = fetch_data(STOCK_MATRIX_URL, st.session_state["data_timestamp"])
        df_matrix.columns = df_matrix.columns.str.strip()
        matrix_search = st.text_input("🔍 Search (Material Code, Description or Area):", "").strip()
        filtered_matrix = df_matrix[df_matrix.astype(str).apply(lambda x: x.str.contains(matrix_search, case=False, na=False)).any(axis=1)] if matrix_search else df_matrix
        st.dataframe(filtered_matrix, use_container_width=True, height=600)
    except Exception as e:
        st.error(f"Error loading Stock Matrix data: {e}")

# --- PREDICTIVE PR INTELLIGENCE ---
elif st.session_state["smart_intelligence_mode"]:
    current_view = url_area if is_area_direct_mode else st.session_state["pr_selected_view"]

    if current_view is None:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 35px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 30px;">
                <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">📈 Predictive PR Intelligence Portal</h1>
                <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Select area to analyze procurement timeline.</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Open Combined Plant-wide PR View", use_container_width=True):
            st.session_state["pr_selected_view"] = "Combined"
            st.query_params["view"] = "pr"
            st.query_params["pr_area"] = "Combined"
            st.rerun()

        areas = list(AREA_CONFIGS.keys())
        for i in range(0, len(areas), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(areas):
                    area_name = areas[i + j]
                    with cols[j]:
                        if st.button(f"Open {area_name}", use_container_width=True, key=f"pr_btn_{area_name}"):
                            st.session_state["pr_selected_view"] = area_name
                            st.query_params["view"] = "pr"
                            st.query_params["pr_area"] = area_name
                            st.rerun()
    else:
        # Check authentication if viewing specific area
        if current_view != "Combined" and not check_authentication(current_view):
            st.stop()

        if not is_area_direct_mode:
            if st.sidebar.button("⬅️ Back to PR Area Selector"):
                st.session_state["pr_selected_view"] = None
                st.query_params["view"] = "pr"
                if "pr_area" in st.query_params:
                    del st.query_params["pr_area"]
                st.rerun()

        header_title = "🌐 Combined Plant-wide PR Intelligence" if current_view == "Combined" else f"📍 Predictive PR Intelligence — {current_view}"
        st.markdown(f"### {header_title}")

        lead_time_months = st.sidebar.slider("Procurement Lead Time (Months):", min_value=1, max_value=12, value=6)
        analysis_months = st.sidebar.selectbox("Consumption Historical Span:", [6, 12, 24], index=1)
        pr_display_limit = st.sidebar.selectbox("Display Records Limit:", [25, 50, 100, "All"], index=0)

        target_configs = AREA_CONFIGS if current_view == "Combined" else {current_view: AREA_CONFIGS[current_view]}

        master_records = []
        for area_key, area_cfg in target_configs.items():
            try:
                df_area = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
                df_area.columns = df_area.columns.str.strip()
                mapping = resolve_columns(df_area)
                
                removal_df = None
                if area_cfg.get("removal_url"):
                    try:
                        removal_df = fetch_data(area_cfg["removal_url"], st.session_state["data_timestamp"])
                    except Exception:
                        pass

                for _, r in df_area.iterrows():
                    mat_code = clean_material_code(r.get(mapping["material"], "N/A"))
                    if mat_code == "N/A":
                        continue
                    store_stock = safe_int(r.get(mapping["store"], 0))
                    field_count = safe_int(r.get(mapping["field"], 0))
                    monthly_consumption, replacement_cycle, total_removals = calculate_real_consumption_from_log(
                        mat_code, removal_df, analysis_months
                    )
                    master_records.append({
                        "Area": area_key,
                        "Material Code": mat_code,
                        "Instrument Name": str(r.get(mapping["name"], "No Name")).strip(),
                        "Specs": str(r.get(mapping["specs"], "N/A")).strip(),
                        "Field Count": field_count,
                        "Store Stock": store_stock,
                        "Monthly Consumption": monthly_consumption,
                        "Replacement Cycle": replacement_cycle,
                        "Total Removals": total_removals
                    })
            except Exception:
                pass

        if master_records:
            master_df = pd.DataFrame(master_records)
            search_query = st.text_input("🔍 Search PR Items:", "").strip()
            if search_query:
                filtered_df = master_df[master_df["Instrument Name"].str.contains(search_query, case=False, na=False) | master_df["Material Code"].str.contains(search_query, case=False, na=False)]
            else:
                filtered_df = master_df.head(int(pr_display_limit)) if pr_display_limit != "All" else master_df

            for _, item in filtered_df.iterrows():
                monthly_consumption = item["Monthly Consumption"]
                store_stock = item["Store Stock"]
                if monthly_consumption > 0:
                    days_remaining = int((store_stock / monthly_consumption) * 30)
                    pr_trigger_date = (datetime.now() + timedelta(days=days_remaining)) - timedelta(days=lead_time_months * 30)
                    is_urgent = pr_trigger_date <= datetime.now()
                    pr_date_str = pr_trigger_date.strftime('%d %b %Y')
                else:
                    pr_date_str = "Stable / No History"
                    is_urgent = False

                urgency_badge = '<span style="background-color: #fee2e2; color: #dc2626; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">🚨 URGENT</span>' if is_urgent else '<span style="background-color: #dcfce7; color: #16a34a; padding: 3px 8px; border-radius: 12px; font-weight: bold; font-size: 11px;">✅ Healthy</span>'

                card_html = f"""
                <div class="inventory-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 6px; margin-bottom: 8px;">
                        <div><b style="color: #0284c7;">📍 {item['Area']}</b> — <b>{item['Instrument Name']}</b> (Mat: {item['Material Code']})</div>
                        <div>{urgency_badge}</div>
                    </div>
                    <div style="display: flex; gap: 12px; font-size: 12px;">
                        <div><b>Field:</b> {item['Field Count']} | <b>Store:</b> {store_stock}</div>
                        <div><b>Avg Consumption:</b> {item['Monthly Consumption']:.2f}/mo</div>
                        <div><b>Suggested PR Date:</b> <span style="color: #0284c7; font-weight: bold;">{pr_date_str}</span></div>
                    </div>
                </div>
                """
                st.components.v1.html(card_html, height=85)

# --- LANDING PAGE (PORTAL SELECTION) ---
elif st.session_state["selected_area"] is None:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 35px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 35px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 32px; font-weight: 800;">🏭 Master Instrumentation Portal</h1>
            <p style="color: #475569 !important; margin-top: 10px; font-size: 15px; font-weight: 500;">Select an operational area block below (Password required)</p>
        </div>
    """, unsafe_allow_html=True)

    areas = list(AREA_CONFIGS.keys())
    for i in range(0, len(areas), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(areas):
                area_name = areas[i + j]
                with cols[j]:
                    st.markdown(f"""
                        <div style="background: #ffffff; padding: 22px; border-radius: 12px; border: 1px solid #e2e8f0; text-align: center; margin-bottom: 12px;">
                            <h3 style="margin: 0 0 6px 0; color: #0f172a;">🔒 {area_name}</h3>
                            <p style="color: #64748b; font-size: 13px; margin: 0;">Password-protected area database</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Enter {area_name}", use_container_width=True, key=f"btn_{area_name}"):
                        st.session_state["selected_area"] = area_name
                        st.rerun()

# --- ACTIVE AREA DASHBOARD VIEW (PASSWORD PROTECTED) ---
else:
    current_area = st.session_state["selected_area"]

    # Gatekeeper check
    if not check_authentication(current_area):
        st.stop()

    # Password Management in Sidebar
    st.sidebar.markdown(f"**Current Area:** `{current_area}`")
    if st.sidebar.button("🔑 Change Password", use_container_width=True):
        change_password_dialog(current_area)

    if st.sidebar.button("🔒 Logout", use_container_width=True):
        st.session_state["auth_status"][current_area] = False
        st.rerun()

    st.sidebar.markdown("---")

    config = AREA_CONFIGS[current_area]
    manager_name = config.get("manager", "Er. Amit Jangra | P.No. 10372")

    st.components.v1.html(f"""
        <div style="background: #ffffff; padding: 22px 25px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.04); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 24px; font-weight: 700;">
                🏭 {config['title']}
            </h1>
            <p style="color: #475569 !important; margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">
                Live Spares Tracking Sheet &bull; Managed by <span style="color: #0284c7; font-weight: 700;">{manager_name} (Inventory Team, C&I, NALCO)</span>
            </p>
        </div>
    """, height=100)
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    try:
        df = fetch_data(config["sheet_url"], st.session_state["data_timestamp"])
        df.columns = df.columns.str.strip()
        
        mapping = resolve_columns(df)
        NAME_COL = mapping["name"]
        STORE_COL = mapping["store"]

        df = df.dropna(subset=[NAME_COL])
        
        st.sidebar.header("🔍 Filter & Pagination")
        all_instruments = ["All System Data"] + list(df[NAME_COL].dropna().unique())
        selected_instrument = st.sidebar.selectbox("Select Instrument Category:", all_instruments)
        items_per_page = st.sidebar.selectbox("Items Per Page:", [10, 20, 30, 40, 50, 100], index=3)
        st.sidebar.markdown("---")

        if selected_instrument != "All System Data":
            df = df[df[NAME_COL].str.strip() == selected_instrument]

        unique_names_ordered = df[NAME_COL].unique()
        total_items = len(unique_names_ordered)
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        st.sidebar.header("📄 Page Navigation")
        page_number = st.sidebar.number_input("Select Page Number:", min_value=1, max_value=total_pages, value=1, step=1)
        st.sidebar.caption(f"Showing page {page_number} of {total_pages} (Total unique: {total_items} items)")
        st.sidebar.markdown("---")

        start_idx = (page_number - 1) * items_per_page
        end_idx = start_idx + items_per_page
        paginated_names = unique_names_ordered[start_idx:end_idx]

        for current_name in paginated_names:
            sub_df = df[df[NAME_COL].astype(str).str.strip() == str(current_name).strip()]
            entry_count = len(sub_df)

            if entry_count == 1:
                row = sub_df.iloc[0]
                mapping["show_name"] = True
                render_row(row, mapping, current_area)
            else:
                total_current_store = sum(safe_int(r[STORE_COL]) for _, r in sub_df.iterrows() if STORE_COL in r)
                st.markdown(f"""
                <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 12px 16px; border-radius: 8px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center;">
                    <span style="font-size: 15px !important; font-weight: 700 !important; color: #0f172a !important;">
                        📂 {current_name} — ({entry_count} Variants Grouped) | Combined Store Stock: {total_current_store}
                    </span>
                    <span style="font-size: 12px; color: #475569; font-weight: bold;">▼</span>
                </div>
                """, unsafe_allow_html=True)
                with st.expander(" "):
                    for idx, row in sub_df.iterrows():
                        mapping["show_name"] = False
                        render_row(row, mapping, current_area)

    except Exception as e:
        st.error(f"Error accessing Google Sheets Database for {current_area}: {e}")

    if st.sidebar.button("🔄 Sync Live Data Now"):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
