import streamlit as st
import pandas as pd
import time

# 1. Page Configuration
st.set_page_config(page_title="Plant Intranet Inventory", layout="wide", page_icon="🏭")

# --- CUSTOM PROFESSIONAL CSS INJECTION ---
st.markdown("""
    <style>
    /* Global Background and Typography */
    .stApp {
        background-color: #f8fafc;
    }
    h1, h2, h3 {
        color: #1e293b !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* Elegant Card Design */
    .inventory-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
    
    /* Metrics Layout inside Cards */
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
        letter-spacing: 0.5px;
        color: #64748b;
        margin-bottom: 4px;
    }
    
    /* Status Badge Styling */
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
    
    /* Technical Specs Box Override */
    .specs-box {
        background-color: #f8fafc;
        border-left: 4px solid #475569;
        padding: 10px;
        border-radius: 4px;
        font-size: 13px;
        color: #334155;
    }
    </style>
""", unsafe_allowed_html=True)


# 2. Password Protection (Authentication Logic)
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


# Safe conversion function to handle text or empty cells gracefully
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


# Helper function to render rows beautifully inside custom UI wrappers
def render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True):
    inst_name = str(row[NAME_COL]).strip()
    full_spec = str(row[SPECS_COL]).strip() if pd.notna(row[SPECS_COL]) else "No Specs Added"
    
    field_count = safe_int(row[FIELD_COL])
    spares_m7 = safe_int(row[SPARES_M7_COL])
    spares_shop = safe_int(row[SPARES_SHOP_COL])
    total_spares = safe_int(row[TOTAL_SPARES_COL])
    
    # AI Inventory Rule Engine
    name_lower = inst_name.lower()
    if "transmitter" in name_lower or "converter" in name_lower:
        healthy_stock = max(2, int(field_count * 0.20))
    elif "element" in name_lower or "switch" in name_lower or "probe" in name_lower:
        healthy_stock = max(3, int(field_count * 0.30))
    else:
        healthy_stock = max(2, int(field_count * 0.15))
    
    shortfall_excess = total_spares - healthy_stock
    cleaned_spec = full_spec.replace('•', '').strip()

    # Determine status markup
    if shortfall_excess < 0:
        status_html = f'<div class="status-badge status-shortfall">🚨 Shortfall ({shortfall_excess})</div>'
    elif shortfall_excess > 0:
        status_html = f'<div class="status-badge status-surplus">✅ Surplus (+{shortfall_excess})</div>'
    else:
        status_html = '<div class="status-badge status-balanced">👌 Balanced (0)</div>'

    # Render Card Row Layout
    st.markdown(f"""
    <div class="inventory-card">
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px;">
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
                <div class="metric-lbl">📦 M7</div><div class="metric-val">{spares_m7}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">⚙️ Shop</div><div class="metric-val">{spares_shop}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">📊 Total</div><div class="metric-val">{total_spares}</div>
            </div>
            <div style="flex: 1; min-width: 90px;" class="metric-box">
                <div class="metric-lbl">🤖 Target</div><div class="metric-val">{healthy_stock}</div>
            </div>
            <div style="flex: 1.5; min-width: 130px; text-align: center;">
                {status_html}
            </div>
        </div>
    </div>
    """, unsafe_allowed_html=True)


if check_password():
    st.title("🏭
