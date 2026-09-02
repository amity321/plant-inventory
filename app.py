import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="HOD Master Instrumentation Dashboard", layout="wide", page_icon="🏭")

# --- AREA CONFIGURATIONS (Update URLs for all 8 areas here) ---
AREA_CONFIGS = {
    "Area 02/03": {
        "title": "Area 02/03 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv",
    },
    "Area 04/05": {
        "title": "Area 04/05 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_04_05_CSV_URL_HERE",
    },
    "Area 06/07": {
        "title": "Area 06/07 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_06_07_CSV_URL_HERE",
    },
    "Area 08": {
        "title": "Area 08 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_08_CSV_URL_HERE",
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

# Helper function to render rows using fallback display wrapper
def render_row(row, NAME_COL, MATERIAL_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True):
    inst_name = str(row[NAME_COL]).strip() if pd.notna(row[NAME_COL]) else "No Name"
    mat_code = clean_material_code(row[MATERIAL_COL]) if MATERIAL_COL in row else "N/A"
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

    if shortfall_excess < 0:
        status_html = f'<div class="status-badge status-shortfall">🚨 Shortfall ({shortfall_excess})</div>'
    elif shortfall_excess > 0:
        status_html = f'<div class="status-badge status-surplus">✅ Surplus (+{shortfall_excess})</div>'
    else:
        status_html = '<div class="status-badge status-balanced">👌 Balanced (0)</div>'

    card_html = f"""
    <div class="inventory-card">
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="flex: 2; min-width: 180px;">
                <h4 style="margin:0; color:#0f172a; font-size:16px; font-weight:700;">{inst_name if show_name else ""}</h4>
                <div style="font-size: 11px; color: #0284c7; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code}</div>
            </div>
            <div style="flex: 2.5; min-width: 200px;">
                <div class="specs-box"><b>Specs:</b> {cleaned_spec}</div>
            </div>
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">On Field</div><div class="metric-val">{field_count}</div>
            </div>
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">M7 Store</div><div class="metric-val">{spares_m7}</div>
            </div>
            <div style="flex: 1; min-width: 80px;" class="metric-box">
                <div class="metric-lbl">Shopfloor</div><div class="metric-val">{spares_shop}</div>
            </div>
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
            <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Enter the exact material code number to precisely scan which area holds it and check its live stock quantities.</p>
        </div>
    """, unsafe_allow_html=True)

    search_code = st.text_input("Enter Exact Material Code (e.g., 86501873151):", "").strip()

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    if search_code:
        all_results = []
        
        for area_key, area_cfg in AREA_CONFIGS.items():
            if "YOUR_" in area_cfg["sheet_url"]:
                continue
            try:
                df_area = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
                df_area.columns = df_area.columns.str.strip()
                
                mat_col = None
                for col in df_area.columns:
                    if "code" in col.lower() or "mat" in col.lower():
                        mat_col = col
                        break
                
                if mat_col:
                    cleaned_codes = df_area[mat_col].apply(clean_material_code)
                    mask = cleaned_codes == search_code
                    matched_rows = df_area[mask]
                    for _, r in matched_rows.iterrows():
                        r_dict = r.to_dict()
                        r_dict["Area_Name"] = area_key
                        r_dict["Matched_Mat_Col"] = mat_col
                        all_results.append(r_dict)
            except Exception as e:
                pass

        if all_results:
            res_df = pd.DataFrame(all_results)
            st.success(f"Found match for material code **{search_code}** in {len(res_df)} location(s) across the plant!")
            
            NAME_COL = "Instrument Name"
            SPECS_COL = "Specs"
            FIELD_COL = "Existing Instrument on Field"
            SPARES_M7_COL = "Remaining Spares in M7"
            SPARES_SHOP_COL = "Remaining Spares in Shop-Floor"
            TOTAL_SPARES_COL = "Total Spares"

            for _, row in res_df.iterrows():
                area_tag = row["Area_Name"]
                mat_col_used = row["Matched_Mat_Col"]
                inst_name = str(row[NAME_COL]).strip() if pd.notna(row[NAME_COL]) else "No Name"
                mat_code_val = clean_material_code(row[mat_col_used])
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

                if shortfall_excess < 0:
                    status_html = f'<div class="status-badge status-shortfall">🚨 Shortfall ({shortfall_excess})</div>'
                elif shortfall_excess > 0:
                    status_html = f'<div class="status-badge status-surplus">✅ Surplus (+{shortfall_excess})</div>'
                else:
                    status_html = '<div class="status-badge status-balanced">👌 Balanced (0)</div>'

                card_html = f"""
                <div class="inventory-card">
                    <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 6px;">📍 Plant Area: {area_tag}</div>
                    <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        <div style="flex: 2; min-width: 180px;">
                            <h4 style="margin:0; color:#0f172a; font-size:16px; font-weight:700;">{inst_name}</h4>
                            <div style="font-size: 11px; color: #0284c7; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code_val}</div>
                        </div>
                        <div style="flex: 2.5; min-width: 200px;">
                            <div class="specs-box"><b>Specs:</b> {cleaned_spec}</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;" class="metric-box">
                            <div class="metric-lbl">Field</div><div class="metric-val">{field_count}</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;" class="metric-box">
                            <div class="metric-lbl">M7 Store</div><div class="metric-val">{spares_m7}</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;" class="metric-box">
                            <div class="metric-lbl">Shop</div><div class="metric-val">{spares_shop}</div>
                        </div>
                        <div style="flex: 1; min-width: 80px;" class="metric-box">
                            <div class="metric-lbl">Total</div><div class="metric-val">{total_spares}</div>
                        </div>
                        <div style="flex: 1.5; min-width: 120px; text-align: center;">
                            {status_html}
                        </div>
                    </div>
                </div>
                """
                st.components.v1.html(card_html, height=135, scrolling=False)
        else:
            st.info(f"No item with exact material code '{search_code}' found across the connected areas.")
    else:
        st.info("💡 Type an exact material code above to instantly locate it across all plant areas.")

# --- HOD LANDING PAGE (Dynamic 3-Column Block Grid for all 8 areas) ---
elif st.session_state["selected_area"] is None:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 35px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 35px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px;">🏭 Master Instrumentation Portal</h1>
            <p style="color: #475569 !important; margin-top: 10px; font-size: 15px; font-weight: 500;">Select an operational area block below to access live inventory metrics</p>
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
    config = AREA_CONFIGS[current_area]

    if st.sidebar.button("⬅️ Back to Master Portal Grid"):
        st.session_state["selected_area"] = None
        st.rerun()

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    # Styled Dashboard Header Panel
    st.components.v1.html(f"""
        <div style="background: #ffffff; padding: 22px 25px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 15px rgba(0,0,0,0.04); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 24px; font-weight: 700;">
                🏭 {config['title']}
            </h1>
            <p style="color: #475569 !important; margin: 6px 0 0 0; font-size: 13px; font-weight: 500;">
                Live Spares Tracking Sheet &bull; Managed by <span style="color: #0284c7; font-weight: 600;">Amit Jangra</span>
            </p>
        </div>
    """, height=100)
    
    st.markdown("<div style='margin-bottom: 20px;'></div>", unsafe_allow_html=True)

    try:
        df = fetch_data(config["sheet_url"], st.session_state["data_timestamp"])
        df.columns = df.columns.str.strip()
        df = df.dropna(subset=["Instrument Name"])

        NAME_COL = "Instrument Name"
        
        MATERIAL_COL = None
        for col in df.columns:
            if "code" in col.lower() or "mat" in col.lower():
                MATERIAL_COL = col
                break
        if not MATERIAL_COL:
            MATERIAL_COL = "Material Code"

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
                render_row(row, NAME_COL, MATERIAL_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True)
            else:
                total_current_spares = sum(safe_int(r[TOTAL_SPARES_COL]) for _, r in sub_df.iterrows())
                
                st.markdown(f"""
                <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; padding: 12px 16px; border-radius: 8px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                    <span style="font-size: 15px !important; font-weight: 700 !important; color: #0f172a !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        📂 {current_name} — ({entry_count} Variants Grouped) | Combined Stock: {total_current_spares}
                    </span>
                    <span style="font-size: 12px; color: #475569; font-weight: bold; margin-right: 5px;">▼</span>
                </div>
                """, unsafe_allow_html=True)
                
                with st.expander(" "):
                    for idx, row in sub_df.iterrows():
                        render_row(row, NAME_COL, MATERIAL_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=False)

    except Exception as e:
        st.error(f"Error accessing Google Sheets Database for {current_area}: {e}")

    if st.sidebar.button("🔄 Sync Live Data Now"):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
