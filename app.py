import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Master Instrumentation Portal", layout="wide", page_icon="🏭")

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

# Helper function to render rows using simplified metric columns (On Field, Store-Room Stock, AI Target, Status)
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
                <h4 style="margin:0; color:#f8fafc; font-size:16px; font-weight:700;">{inst_name if show_name_flag else ""}</h4>
                <div style="font-size: 11px; color: #38bdf8; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code}</div>
            </div>
            <div style="flex: 2.5; min-width: 200px;">
                <div class="specs-box"><b style="color: #38bdf8;">Specs:</b> {cleaned_spec}</div>
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
    .stApp { background-color: #0f172a; color: #f8fafc; }
    h1, h2, h3 { color: #f8fafc !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }
    .inventory-card { 
        background-color: #1e293b; 
        border-radius: 12px; 
        padding: 14px 18px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.2); 
        border: 1px solid #334155; 
        margin-bottom: 15px; 
        transition: all 0.3s ease-in-out;
    }
    .inventory-card:hover {
        border-color: #38bdf8;
        box-shadow: 0 8px 20px rgba(56, 189, 248, 0.15);
        transform: translateY(-2px);
    }
    .metric-box { 
        text-align: center; 
        padding: 6px; 
        background-color: #0f172a; 
        border-radius: 8px; 
        border: 1px solid #334155;
    }
    .metric-val { 
        font-size: 17px; 
        font-weight: 700; 
        color: #f8fafc; 
    }
    .metric-lbl { 
        font-size: 10px; 
        text-transform: uppercase; 
        color: #94a3b8; 
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
    .status-shortfall { background-color: rgba(239, 68, 68, 0.15); color: #f87171; border: 1px solid rgba(239, 68, 68, 0.3); }
    .status-surplus { background-color: rgba(34, 197, 94, 0.15); color: #4ade80; border: 1px solid rgba(34, 197, 94, 0.3); }
    .status-balanced { background-color: rgba(14, 165, 233, 0.15); color: #38bdf8; border: 1px solid rgba(14, 165, 233, 0.3); }
    .specs-box { 
        background-color: #0f172a; 
        border-left: 3px solid #38bdf8; 
        padding: 6px 10px; 
        border-radius: 6px; 
        font-size: 11.5px; 
        color: #cbd5e1; 
    }
    /* Customizing Streamlit Buttons */
    div.stButton > button {
        background-color: #0284c7;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1rem;
        font-weight: 600;
        width: 100%;
        transition: all 0.2s ease;
    }
    div.stButton > button:hover {
        background-color: #0ea5e9;
        color: white;
        border: none;
        box-shadow: 0 0 12px rgba(14, 165, 233, 0.4);
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
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 30px; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: center; margin-bottom: 25px;">
            <h1 style="color: #38bdf8 !important; margin: 0; font-size: 28px; font-weight: 800;">🔢 Exact Material Code Locator</h1>
            <p style="color: #94a3b8 !important; margin-top: 8px; font-size: 14px;">Enter the exact material code number to precisely scan which area holds it and check its live stock quantities.</p>
        </div>
    """, unsafe_allow_html=True)

    sample_code_hint = "e.g., 86501873151"
    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    for area_key, area_cfg in AREA_CONFIGS.items():
        if "YOUR_" in area_cfg["sheet_url"]:
            continue
        try:
            df_sample = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
            df_sample.columns = df_sample.columns.str.strip()
            mapping = resolve_columns(df_sample)
            valid_codes = df_sample[mapping["material"]].dropna().apply(clean_material_code)
            valid_codes = valid_codes[valid_codes != "N/A"]
            if not valid_codes.empty:
                sample_code_hint = f"e.g., {valid_codes.iloc[0]}"
                break
        except Exception:
            pass

    search_code = st.text_input(f"Enter Exact Material Code ({sample_code_hint}):", "").strip()

    if search_code:
        all_results = []
        
        for area_key, area_cfg in AREA_CONFIGS.items():
            if "YOUR_" in area_cfg["sheet_url"]:
                continue
            try:
                df_area = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
                df_area.columns = df_area.columns.str.strip()
                mapping = resolve_columns(df_area)
                mat_col = mapping["material"]
                
                if mat_col in df_area.columns:
                    cleaned_codes = df_area[mat_col].apply(clean_material_code)
                    mask = cleaned_codes == search_code
                    matched_rows = df_area[mask]
                    for _, r in matched_rows.iterrows():
                        r_dict = r.to_dict()
                        r_dict["Area_Name"] = area_key
                        r_dict["Resolved_Mapping"] = mapping
                        all_results.append(r_dict)
            except Exception as e:
                pass

        if all_results:
            res_df = pd.DataFrame(all_results)
            st.success(f"Found match for material code **{search_code}** in {len(res_df)} location(s) across the plant!")
            
            for _, row in res_df.iterrows():
                area_tag = row["Area_Name"]
                mapping = row["Resolved_Mapping"]
                mapping["show_name"] = True
                
                inst_name = str(row[mapping["name"]]).strip() if mapping["name"] in row and pd.notna(row[mapping["name"]]) else "No Name"
                mat_code_val = clean_material_code(row[mapping["material"]])
                full_spec = str(row[mapping["specs"]]).strip() if mapping["specs"] in row and pd.notna(row[mapping["specs"]]) else "No Specs Added"
                
                field_count = safe_int(row[mapping["field"]]) if mapping["field"] in row else 0
                spares_store = safe_int(row[mapping["store"]]) if mapping["store"] in row else 0
                
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

                card_html = f"""
                <div class="inventory-card">
                    <div style="font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 6px;">📍 Plant Area: {area_tag}</div>
                    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        <div style="flex: 2; min-width: 180px;">
                            <h4 style="margin:0; color:#f8fafc; font-size:16px; font-weight:700;">{inst_name}</h4>
                            <div style="font-size: 11px; color: #38bdf8; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code_val}</div>
                        </div>
                        <div style="flex: 2.5; min-width: 200px;">
                            <div class="specs-box"><b style="color: #38bdf8;">Specs:</b> {cleaned_spec}</div>
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
                st.components.v1.html(card_html, height=125, scrolling=False)
        else:
            st.info(f"No item with exact material code '{search_code}' found across the connected areas.")
    else:
        st.info(f"💡 Type an exact material code above to instantly locate it across all plant areas ({sample_code_hint}).")

# --- HOD LANDING PAGE (Dynamic 3-Column Block Grid for all 8 areas) ---
elif st.session_state["selected_area"] is None:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 35px; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.3); text-align: center; margin-bottom: 35px;">
            <h1 style="color: #38bdf8 !important; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px;">🏭 Master Instrumentation Portal</h1>
            <p style="color: #94a3b8 !important; margin-top: 10px; font-size: 15px; font-weight: 500;">Select an operational area block below to access live inventory metrics</p>
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
                        <div style="background: #1e293b; padding: 22px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 6px rgba(0,0,0,0.2); margin-bottom: 15px; text-align: center;">
                            <h3 style="margin-top: 0; margin-bottom: 8px; color: #f8fafc; font-size: 18px; font-weight: 700;">🎛️ {area_name}</h3>
                            <p style="color: #94a3b8; font-size: 13px; line-height: 1.4; margin: 0; min-height: 38px;">Live instrumentation spares and inventory status tracker.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    if st.button(f"Open {area_name}", use_container_width=True, key=f"btn_{area_name}"):
                        st.session_state["selected_area"] = area_name
                        st.rerun()

# --- ACTIVE AREA DASHBOARD VIEW ---
else:
    current_area = st.session_state["selected_area"]
    config = AREA_CONFIGS[current_area]

    if st.sidebar.button("⬅️ Back to Master Portal Grid"):
        st.session_state["selected_area"] = None
        st.rerun()

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    st.components.v1.html(f"""
        <div style="background: #1e293b; padding: 22px 25px; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 4px 15px rgba(0,0,0,0.2); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h1 style="color: #38bdf8 !important; margin: 0; font-size: 24px; font-weight: 700;">
                🏭 {config['title']}
            </h1>
            <p style="color: #94a3b8 !important; margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">
                Live Spares Tracking Sheet &bull; Managed by <span style="color: #38bdf8; font-weight: 600;">Amit Jangra</span>
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
                mapping["show_name"] = True
                render_row(row, mapping, current_area)
            else:
                total_current_store = sum(safe_int(r[STORE_COL]) for _, r in sub_df.iterrows() if STORE_COL in r)
                
                st.markdown(f"""
                <div style="background-color: #1e293b; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    <span style="font-size: 15px !important; font-weight: 700 !important; color: #f8fafc !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        📂 {current_name} — (<span style="color: #38bdf8;">{entry_count} Variants Grouped</span>) | Combined Store Stock: {total_current_store}
                    </span>
                    <span style="font-size: 12px; color: #94a3b8; font-weight: bold; margin-right: 5px;">▼</span>
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
