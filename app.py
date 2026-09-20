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

@st.cache_data(ttl=300)
def fetch_passwords_from_sheet():
    try:
        res = requests.get(AUTH_API_URL, timeout=8)
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
        res = requests.post(
            AUTH_API_URL, 
            json=payload, 
            timeout=15,
            headers={"Content-Type": "application/json"}
        )
        if res.status_code in [200, 302] and ("OK" in res.text or res.status_code == 200):
            fetch_passwords_from_sheet.clear()
            return True, "Success"
        return False, f"API Response: {res.text}"
    except requests.exceptions.Timeout:
        time.sleep(2)
        fetch_passwords_from_sheet.clear()
        verify_db = fetch_passwords_from_sheet()
        if verify_db.get(area_key) == new_password_hash:
            return True, "Success (Verified from Sheet)"
        return False, "Request timed out. Please try once more."
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

# --- URL QUERY PARAMETERS & ROUTING ---
query_params = st.query_params
url_area = query_params.get("area", None)
url_view = query_params.get("view", None)
url_pr_area = query_params.get("pr_area", None)

is_area_direct_mode = bool(url_area and url_area in AREA_CONFIGS)

if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = {}

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

# --- INVENTORY TEAM HIERARCHY MODAL POPUP ---
@st.dialog("🏢 C&I Inventory & Spares Team Hierarchy", width="large")
def show_team_modal():
    svg_tree = """
    <svg viewBox="0 0 1100 580" xmlns="http://www.w3.org/2000/svg" style="background-color: #f8fafc; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; border-radius: 12px; border: 1px solid #e2e8f0; width: 100%;">
      <defs>
        <filter id="shadow" x="-5%" y="-5%" width="110%" height="115%" filterUnits="userSpaceOnUse">
          <feDropShadow dx="0" dy="4" stdDeviation="4" flood-color="#0f172a" flood-opacity="0.08"/>
        </filter>
      </defs>
      <g transform="translate(365, 20)" filter="url(#shadow)">
        <rect width="370" height="75" rx="10" fill="#0f172a"/>
        <text x="185" y="32" fill="#38bdf8" font-size="12" font-weight="700" text-anchor="middle" letter-spacing="1">🏢 C&amp;I INVENTORY &amp; SPARES TEAM</text>
        <text x="185" y="55" fill="#ffffff" font-size="16" font-weight="700" text-anchor="middle">Er. S.K. Jain | <tspan fill="#38bdf8" font-weight="600">HOD (C&amp;I)</tspan></text>
      </g>
      <path d="M 550 95 L 550 140" stroke="#0284c7" stroke-width="2.5" fill="none"/>
      <path d="M 185 140 L 915 140" stroke="#0284c7" stroke-width="2.5" fill="none"/>
      <path d="M 185 140 L 185 165" stroke="#0284c7" stroke-width="2" fill="none"/>
      <rect x="65" y="165" width="240" height="34" rx="6" fill="#e0f2fe" stroke="#0284c7" stroke-width="1.5"/>
      <text x="185" y="187" fill="#0369a1" font-size="13" font-weight="700" text-anchor="middle">⚙️ Refinery Process Areas</text>
      <path d="M 550 140 L 550 165" stroke="#0284c7" stroke-width="2" fill="none"/>
      <rect x="430" y="165" width="240" height="34" rx="6" fill="#fef3c7" stroke="#d97706" stroke-width="1.5"/>
      <text x="550" y="187" fill="#b45309" font-size="13" font-weight="700" text-anchor="middle">⚡ Steam Power Plant (SPP)</text>
      <path d="M 915 140 L 915 165" stroke="#0284c7" stroke-width="2" fill="none"/>
      <rect x="795" y="165" width="240" height="34" rx="6" fill="#dcfce7" stroke="#16a34a" stroke-width="1.5"/>
      <text x="915" y="187" fill="#15803d" font-size="13" font-weight="700" text-anchor="middle">📦 Inventory Store</text>
      <path d="M 185 199 L 185 220" stroke="#94a3b8" stroke-width="2" fill="none"/>
      <g transform="translate(65, 220)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#0284c7"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">📍 Area 02/03</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er. Amit Jangra | <tspan fill="#0284c7" font-weight="600">P.No. 10372</tspan></text>
      </g>
      <g transform="translate(65, 290)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#0284c7"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">📍 Area 04/05</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er D.C. Mishra | <tspan fill="#0284c7" font-weight="600">P.No. 09074</tspan></text>
      </g>
      <g transform="translate(65, 360)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#0284c7"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">📍 Area 06/07</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er R. Swarup | <tspan fill="#0284c7" font-weight="600">P.No. 10565</tspan></text>
      </g>
      <g transform="translate(65, 430)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#0284c7"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">📍 Area 08</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er P. Bagde | <tspan fill="#0284c7" font-weight="600">P.No. 09644</tspan></text>
      </g>
      <g transform="translate(65, 500)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#0284c7"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">📍 Area 09/10</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er K. Kumar | <tspan fill="#0284c7" font-weight="600">P.No. 09643</tspan></text>
      </g>
      <path d="M 550 199 L 550 220" stroke="#94a3b8" stroke-width="2" fill="none"/>
      <g transform="translate(430, 220)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#d97706"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">⚡ SPP TG</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er H.S. Mallick | <tspan fill="#d97706" font-weight="600">P.No. 10873</tspan></text>
      </g>
      <g transform="translate(430, 290)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#d97706"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">🔥 SPP Boiler</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er Sachin Ray | <tspan fill="#d97706" font-weight="600">P.No. 10913</tspan></text>
      </g>
      <path d="M 915 199 L 915 220" stroke="#94a3b8" stroke-width="2" fill="none"/>
      <g transform="translate(795, 220)" filter="url(#shadow)">
        <rect width="240" height="58" rx="8" fill="#ffffff" stroke="#cbd5e1" stroke-width="1.2"/>
        <rect width="6" height="58" rx="3" fill="#16a34a"/>
        <text x="18" y="22" fill="#0f172a" font-size="13" font-weight="700">📦 C&amp;I Sub Store</text>
        <text x="18" y="42" fill="#475569" font-size="12">Er Astha Singh | <tspan fill="#16a34a" font-weight="600">P.No. 10567</tspan></text>
      </g>
    </svg>
    """
    st.components.v1.html(svg_tree, height=600, scrolling=True)

# --- MODAL: CHANGE PASSWORD ---
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
            with st.spinner("Updating password..."):
                success, msg = update_password_in_sheet(area_key, hash_pass(c_new))
                if success:
                    st.success("✅ Password successfully updated!")
                    time.sleep(1.2)
                    st.rerun()
                else:
                    st.error(f"❌ Failed to update password: {msg}")

def check_authentication(area_key):
    if not is_area_direct_mode or st.session_state.get("auth_status", {}).get(area_key, False):
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
                st.session_state["auth_status"][area_key] = True
                st.rerun()
            else:
                st.error("❌ Incorrect Password. Contact- Amit Jangra, 9742900004.")
    return False

def clean_material_code(val):
    if pd.isna(val):
        return "N/A"
    s_val = str(val).strip()
    if s_val == "" or s_val.lower() == "nan":
        return "N/A"
    if s_val.endswith(".0"):
        s_val = s_val[:-2]
    cleaned = s_val.lstrip('0')
    return cleaned if cleaned != "" else "0"

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
    st.markdown(card_html, unsafe_allow_html=True)

def inject_custom_css():
    css = """
    <style>
    .stApp { background-color: #f8fafc; }
    h1, h2, h3 { color: #1e293b !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    
    .header-pill {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        padding: 8px 16px;
        border-radius: 24px;
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-size: 13.5px;
        font-weight: 700;
        color: #0f172a;
        box-shadow: 0 2px 5px rgba(0,0,0,0.03);
    }

    button[data-testid="baseButton-primary"] {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 2.5px solid #38bdf8 !important;
        border-radius: 30px !important;
        font-weight: 800 !important;
        font-size: 14.5px !important;
        padding: 10px 18px !important;
        box-shadow: 0 0 16px rgba(2, 132, 199, 0.6), 0 4px 12px rgba(15, 23, 42, 0.15) !important;
        transition: all 0.25s ease-in-out !important;
    }

    button[data-testid="baseButton-primary"] p,
    button[data-testid="baseButton-primary"] span {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    button[data-testid="baseButton-primary"]:hover {
        background: linear-gradient(135deg, #0369a1 0%, #0c4a6e 100%) !important;
        border-color: #7dd3fc !important;
        box-shadow: 0 0 24px rgba(56, 189, 248, 0.85) !important;
        transform: translateY(-2px) scale(1.02) !important;
    }

    section[data-testid="stSidebar"] {
        background-color: #f1f5f9 !important;
        border-right: 2px solid #cbd5e1 !important;
    }
    
    .sidebar-section-title {
        font-size: 12px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 15px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"] {
        background: #ffffff !important;
        color: #0f172a !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 14px !important;
        padding: 10px 14px !important;
        box-shadow: 0 3px 6px rgba(0,0,0,0.03) !important;
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-bottom: 6px !important;
    }
    
    section[data-testid="stSidebar"] button[data-testid="baseButton-secondary"]:hover {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border-color: #0284c7 !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 14px rgba(2, 132, 199, 0.25) !important;
    }

    .inventory-card { 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 14px 18px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
        border: 1px solid #e2e8f0; 
        margin-bottom: 12px; 
        transition: all 0.15s ease-in-out;
    }
    .inventory-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 6px 16px rgba(0,0,0,0.05);
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

def render_top_bar(status_text="⚡ Live Spares Telemetry Active"):
    c_left, c_right = st.columns([7.0, 3.0])
    with c_left:
        st.markdown(f"""
            <div class="header-pill">
                <span style="color: #10b981; font-size: 15px;">●</span> {status_text}
            </div>
        """, unsafe_allow_html=True)
    with c_right:
        if st.button("👥 Inventory Team", key="team_btn", type="primary", use_container_width=True):
            show_team_modal()
    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

@st.cache_data(ttl=60)
def fetch_data(url, timestamp):
    live_url = f"{url}&t={timestamp}"
    df = pd.read_csv(live_url, dtype=str)
    return df

# --- BULLETPROOF ENGINE (WITH STRICT ISSUE / REMOVAL FILTERING) ---
@st.cache_data(ttl=60)
def build_consumption_map(removal_url, timestamp, analysis_months=12):
    if not removal_url:
        return {}
    try:
        live_url = f"{removal_url}&t={timestamp}"
        df_log = pd.read_csv(live_url, dtype=str)
        df_log.columns = df_log.columns.str.strip()
        
        if df_log.empty:
            return {}

        # 1. Flexible Material Code Column Matcher
        mat_col = None
        for c in df_log.columns:
            c_l = c.lower()
            if any(k in c_l for k in ["material", "mat code", "item code", "sap code", "code", "mat"]):
                mat_col = c
                break
        
        if not mat_col:
            for c in df_log.columns:
                if not any(k in c.lower() for k in ["time", "date", "timestamp", "user", "name"]):
                    mat_col = c
                    break

        if not mat_col:
            return {}

        # 2. Strict Filter: ONLY Count True "Removals / Issues"
        # If transaction column exists, drop 'Added', 'Return', 'Deposit', etc.
        action_col = None
        for c in df_log.columns:
            c_l = c.lower()
            if any(k in c_l for k in ["action", "transaction", "type", "status", "movement", "nature"]):
                action_col = c
                break

        if action_col:
            removal_keywords = ["remov", "issu", "withdraw", "consum", "breakdown", "out", "use", "damaged", "taken"]
            # Exclude rows that are additions or return to store
            exclusion_keywords = ["add", "deposit", "receiv", "return to store", "stock in", "inward"]
            
            def is_valid_removal(val):
                s = str(val).lower()
                has_removal = any(rk in s for rk in removal_keywords)
                has_exclusion = any(ek in s for ek in exclusion_keywords)
                return has_removal and not has_exclusion

            mask = df_log[action_col].astype(str).apply(is_valid_removal)
            # Only apply filter if there are actually matching rows
            if mask.sum() > 0:
                df_log = df_log[mask]
            else:
                # If all rows were 'Added' or no removal was found, this area has 0 removals
                return {}

        # Strip all formatting from Material Codes
        df_log["clean_mat"] = df_log[mat_col].astype(str).str.replace(r'\.0$', '', regex=True).str.strip().str.lstrip('0')

        # 3. Check Quantity
        qty_col = next((c for c in df_log.columns if any(k in c.lower() for k in ["qty", "quantity", "issued", "nos", "count"])), None)
        if qty_col:
            df_log["clean_qty"] = pd.to_numeric(df_log[qty_col].astype(str).str.extract(r'(\d+)', expand=False), errors='coerce').fillna(1)
        else:
            df_log["clean_qty"] = 1.0

        grouped = df_log.groupby("clean_mat")["clean_qty"].sum().to_dict()

        res = {}
        for m_code, total_removals in grouped.items():
            if m_code and m_code not in ["nan", "none", "n/a", ""]:
                tot = float(total_removals)
                # Only assign consumption if it was actually removed (> 0)
                if tot > 0:
                    m_cons = round(tot / float(analysis_months), 2)
                    if m_cons == 0.0:
                        m_cons = 0.08  # If very low consumption, ensure rate is non-zero
                    repl_cycle = round(1.0 / m_cons, 1) if m_cons > 0 else 0.0
                    res[str(m_code)] = (m_cons, repl_cycle, int(tot))
        return res
    except Exception as e:
        return {}

inject_custom_css()

active_tag = f"📍 Active Area: {st.session_state['selected_area']}" if st.session_state["selected_area"] else "🏭 Master Control Room"
render_top_bar(status_text=active_tag)

# --- SIDEBAR DESIGN ---
st.sidebar.markdown("""
    <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 14px; border-radius: 10px; margin-bottom: 15px; text-align: center; border: 1px solid #334155;">
        <h4 style="margin:0; color:#38bdf8; font-size:15px; font-weight:800; letter-spacing:0.5px;">⚙️ CONTROL PANEL</h4>
        <p style="margin:4px 0 0 0; color:#94a3b8; font-size:11px; font-weight:500;">C&I Instrumentation Suite</p>
    </div>
""", unsafe_allow_html=True)

# 1. DIRECT AREA USER MODE
if is_area_direct_mode:
    st.sidebar.markdown('<div class="sidebar-section-title">📌 Area Dedicated Modules</div>', unsafe_allow_html=True)
    if not st.session_state["smart_intelligence_mode"]:
        if st.sidebar.button("📈  Predictive PR Date", use_container_width=True):
            st.session_state["smart_intelligence_mode"] = True
            st.session_state["pr_selected_view"] = url_area
            st.query_params["area"] = url_area
            st.query_params["view"] = "pr"
            st.rerun()
    else:
        if st.sidebar.button("📦  Back to Area Stock", use_container_width=True):
            st.session_state["smart_intelligence_mode"] = False
            st.session_state["pr_selected_view"] = None
            st.query_params["area"] = url_area
            if "view" in st.query_params:
                del st.query_params["view"]
            st.rerun()

# 2. HOD / MASTER PORTAL MODE
else:
    st.sidebar.markdown('<div class="sidebar-section-title">🧭 Portal Navigation</div>', unsafe_allow_html=True)
    if st.sidebar.button("🏠  Dashboard Home", use_container_width=True):
        st.session_state["smart_intelligence_mode"] = False
        st.session_state["stock_matrix_mode"] = False
        st.session_state["selected_area"] = None
        st.session_state["pr_selected_view"] = None
        st.query_params.clear()
        st.rerun()
        
    if st.sidebar.button("📈  Predictive PR Intelligence", use_container_width=True):
        st.session_state["smart_intelligence_mode"] = True
        st.session_state["stock_matrix_mode"] = False
        st.session_state["selected_area"] = None
        st.session_state["pr_selected_view"] = None
        st.query_params["view"] = "pr"
        st.rerun()

    if st.sidebar.button("📊  Areawise Stock Matrix", use_container_width=True):
        st.session_state["stock_matrix_mode"] = True
        st.session_state["smart_intelligence_mode"] = False
        st.session_state["selected_area"] = None
        st.session_state["pr_selected_view"] = None
        st.query_params["view"] = "stock_matrix"
        st.rerun()

st.sidebar.markdown("<div style='margin: 15px 0; border-top: 1.5px solid #cbd5e1;'></div>", unsafe_allow_html=True)

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
        styled_matrix = filtered_matrix.style.set_table_styles([
            {'selector': 'th', 'props': [('font-weight', 'bold'), ('color', '#000000')]},
            {'selector': 'tr th', 'props': [('font-weight', 'bold'), ('color', '#000000')]}
        ]).set_properties(**{'color': '#000000'})
        st.dataframe(styled_matrix, use_container_width=True, height=600)
    except Exception as e:
        st.error(f"Error loading Stock Matrix data: {e}")

# --- PREDICTIVE PR INTELLIGENCE ---
elif st.session_state["smart_intelligence_mode"]:
    current_view = url_area if is_area_direct_mode else st.session_state["pr_selected_view"]

    if current_view is None:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 35px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 30px;">
                <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">📈 Predictive PR Intelligence & Consumption Portal</h1>
                <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Select a specific plant area or choose <b>Combined Areas</b> for centralized planning cell PR analysis.</p>
            </div>
        """, unsafe_allow_html=True)

        st.markdown("""
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 20px; border-radius: 12px; border: 2px solid #3b82f6; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);">
                <h3 style="margin: 0 0 5px 0; color: #1e3a8a; font-size: 20px; font-weight: 800;">🌐 Combined Areas (Plant-wide / Planning Cell View)</h3>
                <p style="margin: 0; color: #1e40af; font-size: 13px;">Merges identical material codes across all active areas for centralized bulk procurement and unified PR dates.</p>
            </div>
        """, unsafe_allow_html=True)

        if st.button("🚀 Open Combined Plant-wide PR View", use_container_width=True):
            st.session_state["pr_selected_view"] = "Combined"
            st.query_params["view"] = "pr"
            st.query_params["pr_area"] = "Combined"
            st.rerun()

        st.markdown("<div style='margin: 20px 0; border-top: 1px solid #e2e8f0;'></div>", unsafe_allow_html=True)
        st.markdown("<h3 style='color: #0f172a; font-size: 18px; font-weight: 700; margin-bottom: 15px;'>🎛️ Or Select Individual Area Block:</h3>", unsafe_allow_html=True)

        areas = list(AREA_CONFIGS.keys())
        for i in range(0, len(areas), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(areas):
                    area_name = areas[i + j]
                    with cols[j]:
                        st.markdown(f"""
                            <div style="background: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 12px; text-align: center;">
                                <h4 style="margin: 0 0 6px 0; color: #0f172a; font-size: 16px; font-weight: 700;">📍 {area_name}</h4>
                                <p style="color: #64748b; font-size: 12px; margin: 0;">Area-specific stock & PR analyzer.</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"Open {area_name}", use_container_width=True, key=f"pr_btn_{area_name}"):
                            st.session_state["pr_selected_view"] = area_name
                            st.query_params["view"] = "pr"
                            st.query_params["pr_area"] = area_name
                            st.rerun()
    else:
        if current_view != "Combined" and not check_authentication(current_view):
            st.stop()

        if not is_area_direct_mode:
            if st.sidebar.button("⬅️  Back to PR Area Selector", use_container_width=True):
                st.session_state["pr_selected_view"] = None
                st.query_params["view"] = "pr"
                if "pr_area" in st.query_params:
                    del st.query_params["pr_area"]
                st.rerun()

        header_title = "🌐 Combined Plant-wide PR Intelligence (Planning Cell)" if current_view == "Combined" else f"📍 Predictive PR Intelligence — {current_view}"
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 25px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); margin-bottom: 25px;">
                <h1 style="color: #0f172a !important; margin: 0; font-size: 24px; font-weight: 800;">{header_title}</h1>
                <p style="color: #475569 !important; margin-top: 6px; font-size: 13px;">Real-time consumption logs and lead-time-adjusted Purchase Requisition schedules.</p>
            </div>
        """, unsafe_allow_html=True)

        st.sidebar.markdown('<div class="sidebar-section-title">⚙️ Analysis Parameters</div>', unsafe_allow_html=True)
        lead_time_months = st.sidebar.slider("Procurement Lead Time (Months):", min_value=1, max_value=12, value=6)
        analysis_months = st.sidebar.selectbox("Consumption Historical Span:", [6, 12, 24], index=1)

        target_configs = AREA_CONFIGS if current_view == "Combined" else {current_view: AREA_CONFIGS[current_view]}

        master_records = []
        for area_key, area_cfg in target_configs.items():
            try:
                df_area = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
                df_area.columns = df_area.columns.str.strip()
                mapping = resolve_columns(df_area)
                
                # Fetch dictionary of actual removals only
                consumption_map = build_consumption_map(area_cfg.get("removal_url"), st.session_state["data_timestamp"], analysis_months)

                for _, r in df_area.iterrows():
                    raw_mat = r.get(mapping["material"], "N/A")
                    mat_code = clean_material_code(raw_mat)
                    if mat_code == "N/A":
                        continue
                    store_stock = safe_int(r.get(mapping["store"], 0))
                    field_count = safe_int(r.get(mapping["field"], 0))
                    
                    # Direct match: Only >0 if true issue exists
                    monthly_consumption, replacement_cycle, total_removals = consumption_map.get(str(mat_code), (0.0, 0.0, 0))
                    
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
            if current_view == "Combined":
                grouped_records = []
                for mat_code, group in master_df.groupby("Material Code"):
                    combined_area_tag = ", ".join(group["Area"].unique())
                    combined_field = group["Field Count"].sum()
                    combined_store = group["Store Stock"].sum()
                    combined_consumption = round(group["Monthly Consumption"].sum(), 2)
                    combined_removals = group["Total Removals"].sum()
                    combined_name = group["Instrument Name"].iloc[0]
                    combined_specs = group["Specs"].iloc[0]
                    combined_cycle = round(1.0 / combined_consumption, 1) if combined_consumption > 0 else 0.0

                    grouped_records.append({
                        "Area": f"Plant-wide ({combined_area_tag})",
                        "Material Code": mat_code,
                        "Instrument Name": combined_name,
                        "Specs": combined_specs,
                        "Field Count": combined_field,
                        "Store Stock": combined_store,
                        "Monthly Consumption": combined_consumption,
                        "Replacement Cycle": combined_cycle,
                        "Total Removals": combined_removals
                    })
                master_df = pd.DataFrame(grouped_records)

            search_query = st.text_input("🔍 Search (Enter Material Code or Instrument Description):", "").strip()
            if search_query:
                filtered_df = master_df[
                    master_df["Material Code"].str.contains(search_query, case=False, na=False) |
                    master_df["Instrument Name"].str.contains(search_query, case=False, na=False) |
                    master_df["Specs"].str.contains(search_query, case=False, na=False)
                ]
            else:
                filtered_df = master_df

            if not filtered_df.empty:
                st.markdown(f"### 🔎 Analytics Results ({len(filtered_df)} items displayed)")
                for _, item in filtered_df.iterrows():
                    monthly_consumption = item["Monthly Consumption"]
                    store_stock = item["Store Stock"]
                    
                    if monthly_consumption > 0:
                        days_remaining = int((store_stock / monthly_consumption) * 30)
                        exhaustion_date = datetime.now() + timedelta(days=days_remaining)
                        lead_time_days = lead_time_months * 30
                        pr_trigger_date = exhaustion_date - timedelta(days=lead_time_days)
                        is_urgent = pr_trigger_date <= datetime.now()
                        pr_date_str = pr_trigger_date.strftime('%d %b %Y')
                    else:
                        pr_date_str = "No History / Stable"
                        is_urgent = False

                    urgency_badge = '<span style="background-color: #fee2e2; color: #dc2626; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">🚨 URGENT PR REQUIRED</span>' if is_urgent else '<span style="background-color: #dcfce7; color: #16a34a; padding: 4px 10px; border-radius: 12px; font-weight: bold; font-size: 11px;">✅ Stock Healthy</span>'

                    card_html = f"""
                    <div class="inventory-card">
                        <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid #f1f5f9; padding-bottom: 8px; margin-bottom: 10px;">
                            <div>
                                <span style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase;">📍 {item['Area']}</span>
                                <h4 style="margin: 2px 0 0 0; color: #0f172a; font-size: 16px; font-weight: 700;">{item['Instrument Name']}</h4>
                            </div>
                            <div>{urgency_badge}</div>
                        </div>
                        <div style="display: flex; flex-wrap: wrap; gap: 15px; font-size: 13px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                            <div style="flex: 2;"><b>Material Code:</b> <span style="color: #0284c7; font-weight: 600;">{item['Material Code']}</span><br><b>Specs:</b> {item['Specs']}</div>
                            <div style="flex: 1; background: #f8fafc; padding: 6px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; font-weight: bold;">INSTALLED / STORE</div>
                                <div style="font-size: 15px; font-weight: 700; color: #0f172a;">{item['Field Count']} / {store_stock}</div>
                            </div>
                            <div style="flex: 1; background: #f8fafc; padding: 6px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; font-weight: bold;">AVG. CONSUMPTION RATE</div>
                                <div style="font-size: 15px; font-weight: 700; color: #0f172a;">{item['Monthly Consumption']:.2f} / mo</div>
                            </div>
                            <div style="flex: 1; background: #f8fafc; padding: 6px; border-radius: 6px; text-align: center;">
                                <div style="font-size: 10px; color: #64748b; font-weight: bold;">REPLACEMENT CYCLE</div>
                                <div style="font-size: 15px; font-weight: 700; color: #0f172a;">{item['Replacement Cycle']} mos</div>
                            </div>
                            <div style="flex: 1.2; background: #eff6ff; padding: 6px; border-radius: 6px; text-align: center; border: 1px solid #bfdbfe;">
                                <div style="font-size: 10px; color: #1e40af; font-weight: bold;">RECOMMENDED PR DATE</div>
                                <div style="font-size: 14px; font-weight: 800; color: #1e3a8a;">{pr_date_str}</div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                st.info("No matching material codes or instruments found.")
        else:
            st.warning("No inventory records available for this area.")

# --- LANDING PAGE ---
elif st.session_state["selected_area"] is None:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 35px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 35px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px;">🏭 Master Instrumentation Portal</h1>
            <p style="color: #475569 !important; margin-top: 10px; font-size: 15px; font-weight: 500;">Direct access to operational area dashboards and spares analytics</p>
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
                        <div style="background: #ffffff; padding: 22px; border-radius: 12px; border: 1px solid #e2e8f0; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 15px; text-align: center;">
                            <h3 style="margin-top: 0; margin-bottom: 8px; color: #0f172a; font-size: 18px; font-weight: 700;">🎛️ {area_name}</h3>
                            <p style="color: #64748b; font-size: 13px; line-height: 1.4; margin: 0; min-height: 38px;">Live instrumentation spares and inventory status tracker.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Open {area_name}", use_container_width=True, key=f"btn_{area_name}"):
                        st.session_state["selected_area"] = area_name
                        st.rerun()

# --- ACTIVE AREA DASHBOARD VIEW ---
else:
    current_area = st.session_state["selected_area"]

    if not check_authentication(current_area):
        st.stop()

    if is_area_direct_mode:
        st.sidebar.markdown(f"**Current Area:** `{current_area}`")
        if st.sidebar.button("🔑 Change Password", use_container_width=True):
            change_password_dialog(current_area)

        if st.sidebar.button("🔒 Logout", use_container_width=True):
            st.session_state["auth_status"][current_area] = False
            st.rerun()
        st.sidebar.markdown("---")

    config = AREA_CONFIGS[current_area]
    manager_name = config.get("manager", "Er. Amit Jangra | P.No. 10372")

    st.markdown(f"""
        <div style="background: #ffffff; padding: 22px 25px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.04); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin-bottom: 20px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 24px; font-weight: 700;">
                🏭 {config['title']}
            </h1>
            <p style="color: #475569 !important; margin-6px 0 0 0; font-size: 13px; font-weight: 500;">
                Live Spares Tracking Sheet &bull; Managed by <span style="color: #0284c7; font-weight: 700;">{manager_name} (Inventory Team, C&I, NALCO)</span>
            </p>
        </div>
    """, unsafe_allow_html=True)

    try:
        df = fetch_data(config["sheet_url"], st.session_state["data_timestamp"])
        df.columns = df.columns.str.strip()
        
        mapping = resolve_columns(df)
        NAME_COL = mapping["name"]
        STORE_COL = mapping["store"]

        df = df.dropna(subset=[NAME_COL])
        
        st.sidebar.markdown('<div class="sidebar-section-title">🔍 Filter &amp; Search</div>', unsafe_allow_html=True)
        all_instruments = ["All System Data"] + list(df[NAME_COL].dropna().unique())
        selected_instrument = st.sidebar.selectbox("Select Instrument Category:", all_instruments)
        
        items_per_page = st.sidebar.selectbox("Items Per Page:", [10, 20, 30, 40, 50, 100], index=3)
        st.sidebar.markdown("<div style='margin: 15px 0; border-top: 1.5px solid #cbd5e1;'></div>", unsafe_allow_html=True)

        if selected_instrument != "All System Data":
            df = df[df[NAME_COL].str.strip() == selected_instrument]

        unique_names_ordered = df[NAME_COL].unique()
        total_items = len(unique_names_ordered)

        # --- PAGINATION ---
        total_pages = max(1, (total_items + items_per_page - 1) // items_per_page)

        st.sidebar.markdown('<div class="sidebar-section-title">📄 Page Navigation</div>', unsafe_allow_html=True)
        page_number = st.sidebar.number_input("Select Page Number:", min_value=1, max_value=total_pages, value=1, step=1)
        st.sidebar.caption(f"Showing page {page_number} of {total_pages} (Total unique: {total_items} items)")
        st.sidebar.markdown("<div style='margin: 15px 0; border-top: 1.5px solid #cbd5e1;'></div>", unsafe_allow_html=True)

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
                <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 12px 16px; border-radius: 8px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <span style="font-size: 15px !important; font-weight: 700 !important; color: #0f172a !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        📂 {current_name} — ({entry_count} Variants Grouped) | Combined Store Stock: {total_current_store}
                    </span>
                    <span style="font-size: 12px; color: #475569; font-weight: bold; margin-right: 5px;">▼</span>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(" "):
                    for idx, row in sub_df.iterrows():
                        mapping["show_name"] = False
                        render_row(row, mapping, current_area)

    except Exception as e:
        st.error(f"Error accessing Google Sheets Database for {current_area}: {e}")

    st.sidebar.markdown('<div class="sidebar-section-title">🔄 Database Control</div>', unsafe_allow_html=True)
    if st.sidebar.button("🔄  Sync Live Data Now", use_container_width=True):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
