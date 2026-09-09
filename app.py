import streamlit as st
import pandas as pd
import time

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Master Instrumentation Portal | NALCO",
    page_icon="🏭",
    layout="wide"
)

# --- GLOBAL DARK THEME STYLING ---
st.markdown("""
<style>
    /* Global Dark Theme Integration */
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 1px solid #1f2937;
    }
    [data-testid="stSidebar"] .stMarkdown, [data-testid="stSidebar"] label {
        color: #e2e8f0 !important;
    }

    /* Inventory Cards */
    .inventory-card {
        background: #1e293b;
        border: 1px solid #334155;
        padding: 16px 20px;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        margin-bottom: 12px;
        transition: border-color 0.2s ease;
    }
    .inventory-card:hover {
        border-color: #38bdf8;
    }

    /* Status Badges */
    .status-badge {
        padding: 6px 12px;
        border-radius: 20px;
        font-size: 11px;
        font-weight: 700;
        text-align: center;
        display: inline-block;
        letter-spacing: 0.3px;
    }
    .status-shortfall {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
    }
    .status-surplus {
        background: rgba(34, 197, 94, 0.15);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.3);
    }
    .status-balanced {
        background: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
        border: 1px solid rgba(59, 130, 246, 0.3);
    }

    /* Specs & Metric Boxes */
    .specs-box {
        background: #0f172a;
        border: 1px solid #334155;
        padding: 8px 12px;
        border-radius: 8px;
        font-size: 12px;
        color: #cbd5e1;
        line-height: 1.4;
    }
    .metric-box {
        background: #0f172a;
        border: 1px solid #334155;
        padding: 8px 10px;
        border-radius: 8px;
        text-align: center;
    }
    .metric-lbl {
        font-size: 10px;
        font-weight: 600;
        color: #94a3b8;
        text-transform: uppercase;
        margin-bottom: 2px;
    }
    .metric-val {
        font-size: 15px;
        font-weight: 700;
        color: #f8fafc;
    }

    /* Form Inputs & Buttons */
    .stTextInput input, .stSelectbox select, .stNumberInput input {
        background-color: #1e293b !important;
        color: #f8fafc !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stButton button {
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 8px 16px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
        transition: opacity 0.2s ease;
    }
    .stButton button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)

# --- SESSION STATE INITIALIZATION ---
if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = None

# --- SIDEBAR GLOBAL SEARCH & CONTROLS ---
search_code = st.sidebar.text_input(f"Enter Material Code ({sample_code_hint}):", "").strip()

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
                <div style="font-size: 11px; font-weight: 700; color: #38bdf8; text-transform: uppercase; margin-bottom: 6px;">📍 Plant Area: {area_tag}</div>
                <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                    <div style="flex: 2; min-width: 180px;">
                        <h4 style="margin:0; color:#f8fafc; font-size:16px; font-weight:700;">{inst_name}</h4>
                        <div style="font-size: 11px; color: #38bdf8; font-weight: 600; margin-top: 2px;">Mat. Code: {mat_code_val}</div>
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

# --- HOD LANDING PAGE ---
elif st.session_state["selected_area"] is None:
    st.markdown("""
        <div style="background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%); padding: 35px; border-radius: 16px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.2); text-align: center; margin-bottom: 35px;">
            <h1 style="color: #f8fafc !important; margin: 0; font-size: 32px; font-weight: 800; letter-spacing: -0.5px;">🏭 Master Instrumentation Portal</h1>
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
            <h1 style="color: #f8fafc !important; margin: 0; font-size: 24px; font-weight: 700;">
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
                <div style="background-color: #1e293b; border: 1px solid #334155; padding: 12px 16px; border-radius: 8px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                    <span style="font-size: 15px !important; font-weight: 700 !important; color: #f8fafc !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                        📂 {current_name} — ({entry_count} Variants Grouped) | Combined Store Stock: {total_current_store}
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
        
