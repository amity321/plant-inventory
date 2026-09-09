import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NALCO Instrumentation Spares Portal",
    page_icon="🎛️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #f8fafc;
    }
    .inventory-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.02);
        transition: all 0.2s ease;
    }
    .inventory-card:hover {
        border-color: #cbd5e1;
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05);
    }
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 11px;
        text-align: center;
        display: inline-block;
    }
    .status-shortfall {
        background-color: #fee2e2;
        color: #dc2626;
        border: 1px solid #fca5a5;
    }
    .status-surplus {
        background-color: #dcfce7;
        color: #16a34a;
        border: 1px solid #86efac;
    }
    .status-balanced {
        background-color: #f1f5f9;
        color: #475569;
        border: 1px solid #cbd5e1;
    }
    .metric-box {
        background: #f8fafc;
        padding: 8px;
        border-radius: 8px;
        text-align: center;
        border: 1px solid #f1f5f9;
    }
    .metric-lbl {
        font-size: 10px;
        color: #64748b;
        font-weight: 700;
        text-transform: uppercase;
    }
    .metric-val {
        font-size: 15px;
        font-weight: 800;
        color: #0f172a;
        margin-top: 2px;
    }
    .specs-box {
        font-size: 12px;
        color: #334155;
        background: #f8fafc;
        padding: 8px 10px;
        border-radius: 6px;
        border-left: 3px solid #0284c7;
    }
    </style>
""", unsafe_allow_html=True)

# --- AREA CONFIGURATIONS ---
AREA_CONFIGS = {
    "Area 01": {
        "title": "Area 01 - Raw Material & Crushing",
        "sheet_url": "https://docs.google.com/spreadsheets/d/1_YOUR_SHEET_ID_AREA_01/export?format=csv"
    },
    "Area 02/03": {
        "title": "Area 02/03 - Digestion & Precipitation",
        "sheet_url": "https://docs.google.com/spreadsheets/d/1_YOUR_SHEET_ID_AREA_02_03/export?format=csv"
    },
    "Area 04": {
        "title": "Area 04 - Calcination & Filtration",
        "sheet_url": "https://docs.google.com/spreadsheets/d/1_YOUR_SHEET_ID_AREA_04/export?format=csv"
    },
    "Utilities": {
        "title": "Utilities & Power Plant Instrumentation",
        "sheet_url": "https://docs.google.com/spreadsheets/d/1_YOUR_SHEET_ID_UTILITIES/export?format=csv"
    },
    "M7 Store-Room": {
        "title": "Central M7 Store-Room Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/1_YOUR_SHEET_ID_M7_STORE/export?format=csv"
    }
}

# --- HELPER FUNCTIONS ---
@st.cache_data(ttl=600)
def fetch_data(url, timestamp):
    try:
        return pd.read_csv(url)
    except Exception as e:
        # Fallback dummy dataframe for demo/testing if URL is unconfigured
        return pd.DataFrame({
            "Material Code": ["86501873151", "86501873152", "86501873153"],
            "Instrument Name": ["VEGAPULS 6X Level Transmitter", "BERTHOLD Density Transmitter", "GEHO Slurry Pump Flow Sensor"],
            "Specs": ["Range 0-10m, 4-20mA HART", "Type LB 444, 2-wire", "High pressure positive displacement"],
            "Field Count": [12, 5, 8],
            "Store Stock": [3, 1, 2],
            "Monthly Consumption": [0.5, 0.2, 0.4],
            "Replacement Cycle": [12, 24, 18],
            "Area": ["Area 02/03", "Area 02/03", "Area 04"]
        })

def clean_material_code(val):
    if pd.isna(val):
        return "N/A"
    s = str(val).strip()
    if s.endswith('.0'):
        s = s[:-2]
    return s

def safe_int(val):
    try:
        if pd.isna(val):
            return 0
        return int(float(str(val).replace(',', '')))
    except:
        return 0

def resolve_columns(df):
    cols = [c.lower().strip() for c in df.columns]
    mapping = {
        "material": "Material Code",
        "name": "Instrument Name",
        "specs": "Specs",
        "field": "Field Count",
        "store": "Store Stock",
        "consumption": "Monthly Consumption",
        "cycle": "Replacement Cycle"
    }
    for col in df.columns:
        cl = col.lower().strip()
        if any(k in cl for k in ["material", "code", "mat"]):
            mapping["material"] = col
        elif any(k in cl for k in ["instrument", "name", "item", "description"]):
            mapping["name"] = col
        elif any(k in cl for k in ["spec", "range", "details"]):
            mapping["specs"] = col
        elif any(k in cl for k in ["field", "installed", "qty_field"]):
            mapping["field"] = col
        elif any(k in cl for k in ["store", "stock", "spare"]):
            mapping["store"] = col
        elif any(k in cl for k in ["consumption", "usage"]):
            mapping["consumption"] = col
        elif any(k in cl for k in ["cycle", "replacement"]):
            mapping["cycle"] = col
    return mapping

def render_row(row, mapping, area_name):
    inst_name = str(row[mapping["name"]]).strip() if mapping["name"] in row and pd.notna(row[mapping["name"]]) else "No Name"
    mat_code_val = clean_material_code(row[mapping["material"]]) if mapping["material"] in row else "N/A"
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

    show_area_header = f'<div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 6px;">📍 Plant Area: {area_name}</div>' if mapping.get("show_name", True) else ''

    card_html = f"""
    <div class="inventory-card">
        {show_area_header}
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="flex: 2; min-width: 180px;">
                <h4 style="margin:0; color:#0f172a; font-size:16px; font-weight:700;">{inst_name}</h4>
                <div style="font-size: 11px; color: #0284c7; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code_val}</div>
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
    st.components.v1.html(card_html, height=115 if not show_area_header else 135, scrolling=False)

# --- SESSION STATE INITIALIZATION ---
if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = None
if "global_search_mode" not in st.session_state:
    st.session_state["global_search_mode"] = False
if "stock_matrix_mode" not in st.session_state:
    st.session_state["stock_matrix_mode"] = False

# --- TOP NAVIGATION BAR / HEADER WITH TOP-RIGHT BUTTON ---
col_head1, col_head2 = st.columns([3, 1])
with col_head1:
    if st.button("🏠 Master Portal Home", use_container_width=False):
        st.session_state["selected_area"] = None
        st.session_state["global_search_mode"] = False
        st.session_state["stock_matrix_mode"] = False
        st.rerun()
with col_head2:
    if st.button("📊 Area-Wise Stock Matrix", use_container_width=True, type="primary"):
        st.session_state["selected_area"] = None
        st.session_state["global_search_mode"] = False
        st.session_state["stock_matrix_mode"] = True
        st.rerun()

st.markdown("---")

# --- SIDEBAR NAVIGATION ---
st.sidebar.title("🎛️ Navigation")
if st.sidebar.button("🔢 Exact Material Code Locator", use_container_width=True):
    st.session_state["global_search_mode"] = True
    st.session_state["selected_area"] = None
    st.session_state["stock_matrix_mode"] = False
    st.rerun()

if st.sidebar.button("🏭 View All Areas Grid", use_container_width=True):
    st.session_state["global_search_mode"] = False
    st.session_state["selected_area"] = None
    st.session_state["stock_matrix_mode"] = False
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### Plant Areas")
for area_key in AREA_CONFIGS.keys():
    if st.sidebar.button(f"📌 {area_key}", use_container_width=True):
        st.session_state["selected_area"] = area_key
        st.session_state["global_search_mode"] = False
        st.session_state["stock_matrix_mode"] = False
        st.rerun()

# --- AREA-WISE STOCK MATRIX VIEW ---
if st.session_state["stock_matrix_mode"]:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 30px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 25px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">📊 Area-Wise Stock Matrix</h1>
            <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Comprehensive comparative overview of store stocks and active instrumentation across all plant units.</p>
        </div>
    """, unsafe_allow_html=True)

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

    matrix_rows = []
    for area_key, area_cfg in AREA_CONFIGS.items():
        if "YOUR_" in area_cfg["sheet_url"]:
            continue
        try:
            df_area = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
            df_area.columns = df_area.columns.str.strip()
            mapping = resolve_columns(df_area)
            for _, r in df_area.iterrows():
                matrix_rows.append({
                    "Area": area_key,
                    "Material Code": clean_material_code(r.get(mapping["material"], "N/A")),
                    "Instrument Name": r.get(mapping["name"], "Unknown"),
                    "Specs": r.get(mapping["specs"], "N/A"),
                    "Field Count": safe_int(r.get(mapping["field"], 0)),
                    "Store Stock": safe_int(r.get(mapping["store"], 0))
                })
        except Exception:
            pass

    if matrix_rows:
        matrix_df = pd.DataFrame(matrix_rows)
        search_query = st.text_input("🔍 Search Matrix by Material Code or Instrument Name:", "").strip()
        if search_query:
            filtered_matrix = matrix_df[
                matrix_df["Material Code"].str.contains(search_query, case=False, na=False) |
                matrix_df["Instrument Name"].str.contains(search_query, case=False, na=False)
            ]
        else:
            filtered_matrix = matrix_df

        st.dataframe(filtered_matrix, use_container_width=True, hide_index=True)
    else:
        st.info("No matrix data available or configured across active sheets.")

# --- GLOBAL EXACT MATERIAL CODE SEARCH MODE ---
elif st.session_state["global_search_mode"]:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 30px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 25px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">🔢 Exact Material Code Locator</h1>
            <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Enter the exact material code number to precisely scan which area holds it and check its live stock quantities.</p>
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

    search_code = st.text_input(f"Enter Material Code ({sample_code_hint}):", "").strip()

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
            except Exception:
                pass

        if all_results:
            res_df = pd.DataFrame(all_results)
            st.success(f"Found match for material code **{search_code}** in {len(res_df)} location(s) across the plant!")
            
            for _, row in res_df.iterrows():
                area_tag = row["Area_Name"]
                mapping = row["Resolved_Mapping"]
                mapping["show_name"] = True
                render_row(row, mapping, area_tag)
        else:
            st.info(f"No item with exact material code '{search_code}' found across the connected areas.")
    else:
        st.info(f"💡 Type material code above to instantly locate it across all plant areas ({sample_code_hint}).")

# --- HOD LANDING PAGE ---
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

    if "data_timestamp" not in st.session_state:
        st.session_state["data_timestamp"] = int(time.time())

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

        # --- PAGINATION LOGIC ---
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

    if st.sidebar.button("🔄 Sync Live Data Now"):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
        
