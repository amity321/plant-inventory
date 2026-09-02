import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="HOD Master Instrumentation Dashboard", layout="wide", page_icon="🏭")

# --- AREA CONFIGURATIONS (Preserved URLs & Settings) ---
AREA_CONFIGS = {
    "Area 02/03": {
        "title": "Area 02/03 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv",
    },
    "Area 04/05": {
        "title": "Area 04/05 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-YNMY8GAWDYkYoC2zW3riA8rnFhnP2hbFRisXYXlLb3Iv95jXyZEHjPUQsfFI4dFt_Z51N0932jPO/pub?gid=345050306&single=true&output=csv",
    },
    "Area 06/07": {
        "title": "Area 06/07 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_06_07_CSV_URL_HERE",
    },
    "Area 08": {
        "title": "Area 08 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEnzn9n4L_uGO9VkLMe8_ylvyaZkskIZZEFJSTqXDQJJ1uEHevl9FfKWhnpcltGsDlhwsxnIEOflaK/pub?gid=1609301093&single=true&output=csv",
    },
    "Area 09/10": {
        "title": "Area 09/10 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_09_10_CSV_URL_HERE",
    },
    "SPP TG": {
        "title": "SPP TG Instrumentation Inventory",
        "sheet_url": "YOUR_SPP_TG_CSV_URL_HERE",
    },
    "SPP Boiler": {
        "title": "SPP Boiler Instrumentation Inventory",
        "sheet_url": "YOUR_SPP_BOILER_CSV_URL_HERE",
    },
    "C&I Sub Store": {
        "title": "C&I Sub Store Instrumentation Inventory",
        "sheet_url": "YOUR_CNI_SUB_STORE_CSV_URL_HERE",
    }
}

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
    """Dynamically resolve column names across different area sheets with flexible fallbacks."""
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

# Helper function to render rows using dynamic column mappings
def render_row(row, mapping, current_area_name):
    name_key = mapping["name"]
    mat_key = mapping["material"]
    specs_key = mapping["specs"]
    field_key = mapping["field"]
    store_key = mapping["store"]
    shop_key = mapping["shop"]
    total_key = mapping["total"]

    inst_name = str(row[name_key]).strip() if name_key in row and pd.notna(row[name_key]) else "No Name"
    mat_code = clean_material_code(row[mat_key]) if mat_key in row else "N/A"
    full_spec = str(row[specs_key]).strip() if specs_key in row and pd.notna(row[specs_key]) else "No Specs Added"
    
    field_count = safe_int(row[field_key]) if field_key in row else 0
    spares_store = safe_int(row[store_key]) if store_key in row else 0
    spares_shop = safe_int(row[shop_key]) if shop_key in row else 0
    
    # Calculate total based on area logic
    if total_key in row and pd.notna(row[total_key]):
        total_spares = safe_int(row[total_key])
    else:
        # If no total column, sum available columns
        if current_area_name == "Area 02/03":
            total_spares = spares_store + spares_shop
        else:
            total_spares = spares_store # Only main store for other areas
    
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

    show_name_flag = mapping.get("show_name", True)
    
    # Logic to hide Shopfloor column for areas other than 02/03
    shop_header_html = '<div class="metric-lbl">Shopfloor</div>' if current_area_name == "Area 02/03" else ""
    shop_value_html = f'<div class="metric-box" style="flex: 1; min-width: 80px;"><div class="metric-lbl">Shopfloor</div><div class="metric-val">{spares_shop}</div></div>' if current_area_name == "Area 02/03" else ""

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
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">On Field</div><div class="metric-val">{field_count}</div>
            </div>
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">Store-Room</div><div class="metric-val">{spares_store}</div>
            </div>
            {shop_value_html}
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">Total-Stock</div><div class="metric-val">{total_spares}</div>
            </div>
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">AI Target</div><div class="metric-val">{healthy_stock}</div>
            </div>
            <div style="flex: 1.5; min-width: 120px; text-align: center;">
                {status_html}
            </div>
        </div>
    </div>
    """
    st.components.v1.html(card_html, height=125, scrolling=False)

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
        transition: all 0.2s ease-in-out;
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
    st.components.v1.html(css, height=0, width=0)

def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(float(str(val).strip()))
    except ValueError:
        return 0

@st.cache_data(ttl=60)
def fetch_data(url, timestamp):
    live_url = f"{url}&t={timestamp}"
    df = pd.read_csv(live_url, dtype=str)
    return df

# Initialize session state for navigation if not present
if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = None

if "global_search_mode" not in st.session_state:
    st.session_state["global_search_mode"] = False

inject_custom_css()

# --- SIDEBAR NAVIGATION CONTROLS ---
st.sidebar.markdown("### 🧭 Navigation & Tools")
if st.sidebar.button("🔍 Exact Material Code Search", use_container_width=True):
    st.session_state["global_search_mode"] = True
    st.session_state["selected_area"] = None
    st.rerun()

if st.sidebar.button("🏠 Home / Portal Grid", use_container_width=True):
    st.session_state["global_search_mode"] = False
    st.session_state["selected_area"] = None
    st.rerun()

st.sidebar.markdown("---")

# --- GLOBAL EXACT MATERIAL CODE SEARCH MODE ---
if st.session_state["global_search_mode"]:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 30px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 25px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">🔢 Exact Material Code Locator</h1>
            <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Enter the exact material code number to precisely scan which area
