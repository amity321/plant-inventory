import streamlit as st
import pandas as pd
pd.set_option('display.max_rows', None)
import time
from datetime import datetime, timedelta

# 1. Page Configuration
st.set_page_config(page_title="Master Instrumentation Dashboard", layout="wide", page_icon="🏭")

# --- AREA CONFIGURATIONS (Preserved URLs & Settings) ---
AREA_CONFIGS = {
    "Area 02/03": {
        "title": "Area 02/03 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=1345118798&single=true&output=csv"
    },
    "Area 04/05": {
        "title": "Area 04/05 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-YNMY8GAWDYkYoC2zW3riA8rnFhnP2hbFRisXYXlLb3Iv95jXyZEHjPUQsfFI4dFt_Z51N0932jPO/pub?gid=345050306&single=true&output=csv",
        "removal_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vS-YNMY8GAWDYkYoC2zW3riA8rnFhnP2hbFRisXYXlLb3Iv95jXyZEHjPUQsfFI4dFt_Z51N0932jPO/pub?gid=593280436&single=true&output=csv"
    },
    "Area 06/07": {
        "title": "Area 06/07 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_06_07_CSV_URL_HERE",
        "removal_url": None
    },
    "Area 08": {
        "title": "Area 08 Instrumentation Inventory",
        "sheet_url": "https://docs.google.com/spreadsheets/d/e/2PACX-1vSEnzn9n4L_uGO9VkLMe8_ylvyaZkskIZZEFJSTqXDQJJ1uEHevl9FfKWhnpcltGsDlhwsxnIEOflaK/pub?gid=1609301093&single=true&output=csv",
        "removal_url": None
    },
    "Area 09/10": {
        "title": "Area 09/10 Instrumentation Inventory",
        "sheet_url": "YOUR_AREA_09_10_CSV_URL_HERE",
        "removal_url": None
    },
    "SPP TG": {
        "title": "SPP TG Instrumentation Inventory",
        "sheet_url": "YOUR_SPP_TG_CSV_URL_HERE",
        "removal_url": None
    },
    "SPP Boiler": {
        "title": "SPP Boiler Instrumentation Inventory",
        "sheet_url": "YOUR_SPP_BOILER_CSV_URL_HERE",
        "removal_url": None
    },
    "C&I Sub Store": {
        "title": "C&I Sub Store Instrumentation Inventory",
        "sheet_url": "YOUR_CNI_SUB_STORE_CSV_URL_HERE",
        "removal_url": None
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

# Initialize session state for navigation
if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = None

if "global_search_mode" not in st.session_state:
    st.session_state["global_search_mode"] = False

if "smart_intelligence_mode" not in st.session_state:
    st.session_state["smart_intelligence_mode"] = False

if "pr_selected_view" not in st.session_state:
    st.session_state["pr_selected_view"] = None

inject_custom_css()

# --- SIDEBAR NAVIGATION CONTROLS ---
st.sidebar.markdown("### 🧭 Navigation & Tools")
if st.sidebar.button("🔍 Material Code", use_container_width=True):
    st.session_state["global_search_mode"] = True
    st.session_state["smart_intelligence_mode"] = False
    st.session_state["selected_area"] = None
    st.session_state["pr_selected_view"] = None
    st.rerun()

if st.sidebar.button("📈 Predictive PR Intelligence", use_container_width=True):
    st.session_state["smart_intelligence_mode"] = True
    st.session_state["global_search_mode"] = False
    st.session_state["selected_area"] = None
    st.session_state["pr_selected_view"] = None
    st.rerun()

if st.sidebar.button("🏠 Home / Portal Grid", use_container_width=True):
    st.session_state["global_search_mode"] = False
    st.session_state["smart_intelligence_mode"] = False
    st.session_state["selected_area"] = None
    st.session_state["pr_selected_view"] = None
    st.rerun()

st.sidebar.markdown("---")

# --- PREDICTIVE PR INTELLIGENCE & CONSUMPTION ANALYTICS MODE ---
if st.session_state["smart_intelligence_mode"]:
    
    if st.session_state["pr_selected_view"] is None:
        st.markdown("""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 35px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 30px;">
                <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">📈 Predictive PR Intelligence & Consumption Portal</h1>
                <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Select a specific plant area or choose **Combined Areas** for centralized planning cell PR analysis.</p>
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
                            st.rerun()
    else:
        current_view = st.session_state["pr_selected_view"]
        
        if st.sidebar.button("⬅️ Back to PR Area Selector"):
            st.session_state["pr_selected_view"] = None
            st.rerun()

        header_title = "🌐 Combined Plant-wide PR Intelligence (Planning Cell)" if current_view == "Combined" else f"📍 Predictive PR Intelligence — {current_view}"
        
        st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 25px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); margin-bottom: 25px;">
                <h1 style="color: #0f172a !important; margin: 0; font-size: 24px; font-weight: 800;">{header_title}</h1>
                <p style="color: #475569 !important; margin-top: 6px; font-size: 13px;">Real-time consumption logs and lead-time-adjusted Purchase Requisition schedules.</p>
            </div>
        """, unsafe_allow_html=True)

        if "data_timestamp" not in st.session_state:
            st.session_state["data_timestamp"] = int(time.time())

        st.sidebar.markdown("### ⚙️ Intelligence Parameters")
        lead_time_months = st.sidebar.slider("Procurement Lead Time (Months):", min_value=1, max_value=12, value=6, help="Total procedural delay from PR generation to final delivery.")
        analysis_months = st.sidebar.selectbox("Consumption Historical Span:", [6, 12, 24], index=1)
        pr_display_limit = st.sidebar.selectbox("Display Records Limit:", [25, 50, 100, 200, "All"], index=0)

        target_configs = AREA_CONFIGS if current_view == "Combined" else {current_view: AREA_CONFIGS[current_view]}

        master_records = []
        for area_key, area_cfg in target_configs.items():
            if "YOUR_" in area_cfg["sheet_url"]:
                continue
            try:
                df_area = fetch_data(area_cfg["sheet_url"], st.session_state["data_timestamp"])
                df_area.columns = df_area.columns.str.strip()
                mapping = resolve_columns(df_area)
                mat_col = mapping["material"]
                name_col = mapping["name"]
                field_col = mapping["field"]
                store_col = mapping["store"]
                specs_col = mapping["specs"]

                removal_df = None
                if area_cfg.get("removal_url"):
                    try:
                        removal_df = fetch_data(area_cfg["removal_url"], st.session_state["data_timestamp"])
                    except Exception:
                        pass

                for _, r in df_area.iterrows():
                    mat_code = clean_material_code(r.get(mat_col, "N/A"))
                    if mat_code == "N/A":
                        continue
                    
                    store_stock = safe_int(r.get(store_col, 0))
                    field_count = safe_int(r.get(field_col, 0))
                    
                    monthly_consumption, replacement_cycle, total_removals = calculate_real_consumption_from_log(
                        mat_code, removal_df, analysis_months
                    )

                    master_records.append({
                        "Area": area_key,
                        "Material Code": mat_code,
                        "Instrument Name": str(r.get(name_col, "No Name")).strip(),
                        "Specs": str(r.get(specs_col, "N/A")).strip(),
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
            st.warning("No inventory records available across active sheets.")

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

    # Removed the "Back to Master Portal Grid" button block here per your request

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
