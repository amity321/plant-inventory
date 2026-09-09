import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Plant Instrumentation Spares Inventory",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CUSTOM CSS STYLING ---
st.markdown("""
<style>
    .inventory-card {
        background: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.02);
        margin-bottom: 12px;
    }
    .status-badge {
        padding: 4px 10px;
        border-radius: 12px;
        font-weight: bold;
        font-size: 11px;
        text-align: center;
    }
    .status-shortfall { background-color: #fee2e2; color: #dc2626; }
    .status-surplus { background-color: #dcfce7; color: #16a34a; }
    .status-balanced { background-color: #f1f5f9; color: #475569; }
    .specs-box {
        background: #f8fafc;
        padding: 8px;
        border-radius: 6px;
        font-size: 12px;
        color: #334155;
        border: 1px solid #e2e8f0;
    }
    .metric-box {
        background: #f8fafc;
        padding: 6px;
        border-radius: 6px;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    .metric-lbl {
        font-size: 10px;
        color: #64748b;
        font-weight: bold;
        text-transform: uppercase;
    }
    .metric-val {
        font-size: 15px;
        font-weight: 700;
        color: #0f172a;
    }
</style>
""", unsafe_allow_html=True)

# --- AREA CONFIGURATIONS ---
AREA_CONFIGS = {
    "Area 02/03": {
        "title": "Area 02/03 - Plant Instrumentation & Spares",
        "sheet_url": "YOUR_SHEET_URL_HERE"
    }
}

# --- HELPER FUNCTIONS ---
def clean_material_code(code):
    if pd.isna(code):
        return "N/A"
    cleaned = str(code).strip().split('.')[0]
    return cleaned if cleaned else "N/A"

def safe_int(val):
    try:
        return int(float(val))
    except (ValueError, TypeError):
        return 0

@st.cache_data(ttl=600)
def fetch_data(url, timestamp):
    try:
        return pd.read_csv(url)
    except Exception:
        return pd.DataFrame()

def resolve_columns(df):
    cols = {
        "material": "Material Code",
        "name": "Instrument Name",
        "specs": "Specs",
        "field": "Field Count",
        "store": "Store Stock",
        "area": "Area"
    }
    for col in df.columns:
        lower_col = col.lower()
        if "material" in lower_col or "code" in lower_col:
            cols["material"] = col
        elif "name" in lower_col or "description" in lower_col or "instrument" in lower_col:
            cols["name"] = col
        elif "spec" in lower_col:
            cols["specs"] = col
        elif "field" in lower_col or "installed" in lower_col:
            cols["field"] = col
        elif "store" in lower_col or "stock" in lower_col:
            cols["store"] = col
        elif "area" in lower_col:
            cols["area"] = col
    return cols

def render_row(row, mapping, current_area):
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

    show_area_header = f'<div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 6px;">📍 Plant Area: {current_area}</div>' if mapping.get("show_name", True) else ''

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
    st.components.v1.html(card_html, height=125, scrolling=False)

# --- SESSION STATE INITIALIZATION ---
if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = None
if "global_search_mode" not in st.session_state:
    st.session_state["global_search_mode"] = False

# --- SIDEBAR CONTROLS ---
st.sidebar.title("Navigation & Controls")
if st.sidebar.button("🏠 Master Portal Grid", use_container_width=True):
    st.session_state["selected_area"] = None
    st.session_state["global_search_mode"] = False
    st.rerun()

if st.sidebar.button("🔢 Exact Material Code Locator", use_container_width=True):
    st.session_state["global_search_mode"] = True
    st.session_state["selected_area"] = None
    st.rerun()

st.sidebar.markdown("---")
lead_time_months = st.sidebar.slider("Procurement Lead Time (Months):", min_value=1, max_value=12, value=3)
pr_display_limit = st.sidebar.selectbox("Display Limit:", ["All", 10, 25, 50], index=0)

# Mock master_records collection for demonstration if needed
master_records = []
for area_key, area_cfg in AREA_CONFIGS.items():
    if "YOUR_" not in area_cfg["sheet_url"]:
        try:
            df_temp = fetch_data(area_cfg["sheet_url"], int(time.time()))
            for _, r in df_temp.iterrows():
                r_dict = r.to_dict()
                r_dict["Area"] = area_key
                master_records.append(r_dict)
        except Exception:
            pass

current_view = st.sidebar.selectbox("Dashboard View Mode:", ["Combined", "Detailed View"], index=0)
st.sidebar.markdown("---")

# --- MAIN ROUTING LOGIC ---

if master_records and not st.session_state["global_search_mode"] and st.session_state["selected_area"] is None:
    master_df = pd.DataFrame(master_records)

    if current_view == "Combined":
        grouped_records = []
        for mat_code, group in master_df.groupby("Material Code"):
            combined_area_tag = ", ".join(group["Area"].unique())
            combined_field = group["Field Count"].sum() if "Field Count" in group.columns else 0
            combined_store = group["Store Stock"].sum() if "Store Stock" in group.columns else 0
            combined_consumption = round(group["Monthly Consumption"].sum(), 2) if "Monthly Consumption" in group.columns else 0.0
            combined_removals = group["Total Removals"].sum() if "Total Removals" in group.columns else 0
            combined_name = group["Instrument Name"].iloc[0] if "Instrument Name" in group.columns else "Unknown"
            combined_specs = group["Specs"].iloc[0] if "Specs" in group.columns else "No Specs"
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

    search_query = st.text_input("🔍 Universal Search (Enter Material Code or Instrument Description):", "").strip()

    if search_query:
        filtered_df = master_df[
            master_df["Material Code"].str.contains(search_query, case=False, na=False) |
            master_df["Instrument Name"].str.contains(search_query, case=False, na=False) |
            master_df["Specs"].str.contains(search_query, case=False, na=False)
        ]
    else:
        if pr_display_limit != "All":
            filtered_df = master_df.head(int(pr_display_limit))
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
            st.components.v1.html(card_html, height=140, scrolling=False)
    else:
        st.info("No matching material codes or instruments found.")
else:
    if st.session_state["global_search_mode"]:
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
                        <div style="font-size: 11px; font-weight: 700; color: #0284c7; text-transform: uppercase; margin-bottom: 6px;">📍 Plant Area: {area_tag}</div>
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
                    st.components.v1.html(card_html, height=125, scrolling=False)
            else:
                st.info(f"No item with exact material code '{search_code}' found across the connected areas.")
        else:
            st.info(f"💡 Type material code above to instantly locate it across all plant areas ({sample_code_hint}).")

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
