import hashlib
import json
import os
import time
import urllib.parse
from datetime import datetime, timedelta
import pandas as pd
import requests
import streamlit as st

pd.set_option("display.max_rows", None)

# --- NALCO BRANDING CONSTANTS ---
NALCO_LOGO_PATH = "nalco_logo.png"

# 1. Page Configuration
st.set_page_config(
    page_title="NALCO - Central C&I Spares Portal",
    layout="wide",
    page_icon=NALCO_LOGO_PATH if os.path.exists(NALCO_LOGO_PATH) else "⚙️",
)

# --- GOOGLE APPS SCRIPT AUTH & WEBHOOK URL ---
AUTH_API_URL = "https://script.google.com/macros/s/AKfycbwnf2s_JeEKydIm4xZE5Lc4MTj3D_A30hKIDOBqJa-ykjDbhgCkvL6YaTqG4myn2I52/exec"

# --- GOOGLE FORM PRE-FILL CONFIGURATION ---
GOOGLE_FORM_BASE_URL = "https://docs.google.com/forms/d/e/1FAIpQLSd8B94YMCCRyh8dMHnJIe5eCb9cj_rzQbj7XAb54O_nsWFs8g/viewform"
FORM_ENTRY_TRANSACTION = "entry.1572263064"
FORM_ENTRY_INSTRUMENT = "entry.661617527"


def hash_pass(pwd: str) -> str:
    return hashlib.sha256(pwd.strip().encode("utf-8")).hexdigest()


# --- HOD / MASTER AUTHORIZED OFFICERS DIRECTORY ---
MASTER_AUTHORIZED_USERS = {
    "10372": {
        "name": "Er. Amit Jangra",
        "pin": "9742900004",
        "role": "Lead Administrator",
    },
    "06505": {
        "name": "Er. S.K. Jain",
        "pin": "9437106841",
        "role": "HOD (C&I)",
    },
    "08165": {
        "name": "Er. H. S. Behera",
        "pin": "9437006963",
        "role": "Planning Cell Head",
    },
}


@st.cache_data(ttl=60)
def fetch_passwords():
    try:
        res = requests.get(AUTH_API_URL, timeout=8)
        if res.status_code == 200:
            return res.json()
    except Exception:
        pass
    return {}


def update_password_in_sheet(area_key, new_password_hash):
    try:
        payload = {"area": area_key, "new_hash": new_password_hash}
        res = requests.post(
            AUTH_API_URL,
            json=payload,
            timeout=15,
            headers={"Content-Type": "application/json"},
        )
        if res.status_code in [200, 302] and (
            "OK" in res.text or res.status_code == 200
        ):
            fetch_passwords.clear()
            return True, "Success"
        return False, f"API Response: {res.text}"
    except requests.exceptions.Timeout:
        time.sleep(2)
        fetch_passwords.clear()
        verify_db = fetch_passwords()
        if verify_db.get(area_key) == new_password_hash:
            return True, "Success (Verified from Sheet)"
        return False, "Request timed out. Please try once more."
    except Exception as e:
        return False, str(e)


# --- AREA CONFIGURATIONS & ZONE THEMES ---
AREA_CONFIGS = {
    "Area 02/03": {
        "title": "Area 02/03 Instrumentation Inventory",
        "manager": "Er. Amit Jangra | P.No. 10372",
        "zone_type": "Refinery Process Area",
        "color": "#0284c7",
        "gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=383890446&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=1345118798&single=true&output=csv"
        ),
    },
    "Area 04/05": {
        "title": "Area 04/05 Instrumentation Inventory",
        "manager": "Er D.C. Mishra | P.No. 09074",
        "zone_type": "Refinery Process Area",
        "color": "#0284c7",
        "gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSZopDMRgkBThhmBF8NAXoBERx24tj7Ae2y6HlvimEHUhahXEWY8tmXoNDSM_MNlkDB7TfGpHB9I2H_/pub?gid=1836901304&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSZopDMRgkBThhmBF8NAXoBERx24tj7Ae2y6HlvimEHUhahXEWY8tmXoNDSM_MNlkDB7TfGpHB9I2H_/pub?gid=1951924870&single=true&output=csv"
        ),
    },
    "Area 06/07": {
        "title": "Area 06/07 Instrumentation Inventory",
        "manager": "Er R. Swarup | P.No. 10565",
        "zone_type": "Refinery Process Area",
        "color": "#0284c7",
        "gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vStPdBa-nm7i9eHjSxpyrIOyyu5VJZo77E4KF3tk2R9ewp0hK58RDVYBKiW5UsRD2DxBTrafX-CfJry/pub?gid=175582315&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vStPdBa-nm7i9eHjSxpyrIOyyu5VJZo77E4KF3tk2R9ewp0hK58RDVYBKiW5UsRD2DxBTrafX-CfJry/pub?gid=1371227319&single=true&output=csv"
        ),
    },
    "Area 08": {
        "title": "Area 08 Instrumentation Inventory",
        "manager": "Er P. Bagde | P.No. 09644",
        "zone_type": "Refinery Process Area",
        "color": "#0284c7",
        "gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMj_W_6-T0duFQ_XS8Yf9xTQPQvguuQP9P_aUwkKuiOZeT8BXSkAHeQspMlhXebcmz0ff-VZRdya-M/pub?gid=664188260&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vRMj_W_6-T0duFQ_XS8Yf9xTQPQvguuQP9P_aUwkKuiOZeT8BXSkAHeQspMlhXebcmz0ff-VZRdya-M/pub?gid=260669801&single=true&output=csv"
        ),
    },
    "Area 09/10": {
        "title": "Area 09/10 Instrumentation Inventory",
        "manager": "Er K. Kumar | P.No. 09643",
        "zone_type": "Refinery Process Area",
        "color": "#0284c7",
        "gradient": "linear-gradient(135deg, #0284c7 0%, #0369a1 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vS7NvVXAcew2ZWcA_kSTmCQJk6OVq3RQfqGqCZ08jGKosNmTYWprvR4JUMC3-vXI28wF6HJ1B_Wk1uo/pub?gid=87821600&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vS7NvVXAcew2ZWcA_kSTmCQJk6OVq3RQfqGqCZ08jGKosNmTYWprvR4JUMC3-vXI28wF6HJ1B_Wk1uo/pub?gid=1187023151&single=true&output=csv"
        ),
    },
    "SPP TG": {
        "title": "SPP TG Instrumentation Inventory",
        "manager": "Er H.S. Mallick | P.No. 10873",
        "zone_type": "Steam Power Plant (SPP)",
        "color": "#d97706",
        "gradient": "linear-gradient(135deg, #d97706 0%, #b45309 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPmgZl9jEQaGMQbxeOu0Xr_GtQ2P4_twAx2qNxUOjoYSvSW27vJsUgRtQB7XtIcU-bcCulPJLX3PLA/pub?gid=974689106&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vTPmgZl9jEQaGMQbxeOu0Xr_GtQ2P4_twAx2qNxUOjoYSvSW27vJsUgRtQB7XtIcU-bcCulPJLX3PLA/pub?gid=900388666&single=true&output=csv"
        ),
    },
    "SPP Boiler": {
        "title": "SPP Boiler Instrumentation Inventory",
        "manager": "Er Sachin Ray | P.No. 10913",
        "zone_type": "Steam Power Plant (SPP)",
        "color": "#d97706",
        "gradient": "linear-gradient(135deg, #d97706 0%, #b45309 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVTH56rybWjsWYThgCiTWzafjabniWhqHUUuXoVdqexuWIjrmvh65AtimfDlFNB5V4StSi5G4BWuKf/pub?gid=1937643350&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vQVTH56rybWjsWYThgCiTWzafjabniWhqHUUuXoVdqexuWIjrmvh65AtimfDlFNB5V4StSi5G4BWuKf/pub?gid=223018013&single=true&output=csv"
        ),
    },
    "C&I Sub Store": {
        "title": "C&I Sub Store Instrumentation Inventory",
        "manager": "Er Astha Singh | P.No. 10567",
        "zone_type": "Central Logistics & Sub-Store",
        "color": "#16a34a",
        "gradient": "linear-gradient(135deg, #16a34a 0%, #15803d 100%)",
        "sheet_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbJUMrlU1bWLUsOt0tL-4xsBpsO2kt70Rq4am-OpMb7hsZZxe69JzLwBqT1EOLZtuU-PGkY-mx4EuZ/pub?gid=2014684236&single=true&output=csv"
        ),
        "removal_url": (
            "https://docs.google.com/spreadsheets/d/e/2PACX-1vSbJUMrlU1bWLUsOt0tL-4xsBpsO2kt70Rq4am-OpMb7hsZZxe69JzLwBqT1EOLZtuU-PGkY-mx4EuZ/pub?gid=158170506&single=true&output=csv"
        ),
    },
}

STOCK_MATRIX_URL = "https://docs.google.com/spreadsheets/d/e/2PACX-1vRyzwW4otIA4Y7xUj3HvrB9Nx0D-rQMqXOMMzK9L8uxVm60X3q3IxZ9D_NsJyU-THMS8O8B5_C-KhbN/pub?gid=868142398&single=true&output=csv"

SUBSTORE_AREA_KEYWORD_MAP = {
    "Area 02/03": ["02/03", "area 2", "area 3"],
    "Area 04/05": ["04/05", "area 4", "area 5"],
    "Area 06/07": ["06/07", "area 6", "area 7"],
    "Area 08": ["08", "area 8"],
    "Area 09/10": ["09/10", "area 9", "area 10"],
    "SPP TG": ["spp tg", "tg"],
    "SPP Boiler": ["spp boiler", "boiler"],
    "C&I Sub Store": ["sub store", "store", "central store", "m7"],
}

# --- URL QUERY PARAMETERS & ROUTING ---
query_params = st.query_params
url_area = query_params.get("area", None)
url_view = query_params.get("view", None)
url_pr_area = query_params.get("pr_area", None)

is_area_direct_mode = bool(url_area and url_area in AREA_CONFIGS)

if "auth_status" not in st.session_state:
    st.session_state["auth_status"] = {}

if "hod_auth_user" not in st.session_state:
    st.session_state["hod_auth_user"] = None

if "selected_area" not in st.session_state:
    st.session_state["selected_area"] = url_area if is_area_direct_mode else None

if "smart_intelligence_mode" not in st.session_state:
    st.session_state["smart_intelligence_mode"] = url_view == "pr"

if "stock_matrix_mode" not in st.session_state:
    st.session_state["stock_matrix_mode"] = url_view == "stock_matrix"

if "pr_selected_view" not in st.session_state:
    if is_area_direct_mode and st.session_state["smart_intelligence_mode"]:
        st.session_state["pr_selected_view"] = url_area
    else:
        st.session_state["pr_selected_view"] = url_pr_area

if "data_timestamp" not in st.session_state:
    st.session_state["data_timestamp"] = int(time.time())

if "urgent_pr_filter_state" not in st.session_state:
    st.session_state["urgent_pr_filter_state"] = False


@st.cache_resource
def get_global_messages():
    return []


GLOBAL_MESSAGES = get_global_messages()


# --- UTILITY & DATA RESOLUTION HELPERS ---
def clean_material_code(val):
    if pd.isna(val):
        return "N/A"
    s_val = str(val).strip()
    if s_val == "" or s_val.lower() == "nan":
        return "N/A"
    if s_val.endswith(".0"):
        s_val = s_val[:-2]
    cleaned = s_val.lstrip("0")
    return cleaned if cleaned != "" else "0"


def safe_int(val):
    if pd.isna(val):
        return 0
    try:
        return int(float(str(val).strip()))
    except (ValueError, TypeError):
        return 0


def resolve_columns(df):
    cols = df.columns
    (
        mat_col,
        field_col,
        store_col,
        shop_col,
        total_col,
        specs_col,
        name_col,
        area_belongs_col,
    ) = (None, None, None, None, None, None, None, None)
    for col in cols:
        c_low = col.lower()
        if not mat_col and ("code" in c_low or "mat" in c_low):
            mat_col = col
        elif not field_col and ("field" in c_low or "existing" in c_low):
            field_col = col
        elif not store_col and (
            "store" in c_low
            or "m7" in c_low
            or ("room" in c_low and "shop" not in c_low)
        ):
            store_col = col
        elif not shop_col and ("shop" in c_low or "floor" in c_low):
            shop_col = col
        elif not total_col and "total" in c_low:
            total_col = col
        elif not specs_col and "spec" in c_low:
            specs_col = col
        elif not name_col and ("instrument" in c_low or "name" in c_low):
            name_col = col
        elif not area_belongs_col and (
            "belong" in c_low
            or "area" in c_low
            or "location" in c_low
            or "section" in c_low
        ):
            area_belongs_col = col

    return {
        "name": name_col or "Instrument Name",
        "material": mat_col or "Material Code",
        "specs": specs_col or "Specs",
        "field": field_col or "Existing Instrument on Field",
        "store": store_col or "Remaining Spares in Store-Room",
        "shop": shop_col or "Remaining Spares in Shop-Floor",
        "total": total_col or "Total Spares",
        "area_belongs": area_belongs_col or "Belongs To Area",
    }


@st.cache_data(ttl=60)
def fetch_data(url, timestamp):
    live_url = f"{url}&t={timestamp}"
    df = pd.read_csv(live_url, dtype=str)
    return df


# --- PRIVACY-FIRST STOCK MATRIX SEARCH & BACKGROUND EXTRACTOR ---
@st.cache_data(ttl=60)
def search_stock_matrix_catalog(search_term, timestamp):
    if not search_term or len(search_term.strip()) < 2:
        return []

    try:
        df_mat = fetch_data(STOCK_MATRIX_URL, timestamp)
        df_mat.columns = df_mat.columns.str.strip()

        cols = df_mat.columns
        mat_col = next(
            (
                c
                for c in cols
                if any(k in c.lower() for k in ["code", "mat", "item", "sap"])
            ),
            cols[0],
        )
        desc_col = next(
            (
                c
                for c in cols
                if any(
                    k in c.lower()
                    for k in ["desc", "name", "instrument", "details"]
                )
            ),
            cols[1] if len(cols) > 1 else cols[0],
        )

        term = search_term.strip().lower()

        mask = df_mat[mat_col].astype(str).str.lower().str.contains(
            term, na=False
        ) | df_mat[desc_col].astype(str).str.lower().str.contains(
            term, na=False
        )

        matched_df = df_mat[mask].head(25)

        results = []
        for _, r in matched_df.iterrows():
            m_code = clean_material_code(r.get(mat_col, "N/A"))
            d_name = str(r.get(desc_col, "N/A")).strip()

            results.append(
                {
                    "label": f"[{m_code}] {d_name}",
                    "mat_code": m_code,
                    "description": d_name,
                    "_raw_row": r.to_dict(),
                }
            )

        return results
    except Exception:
        return []


def extract_area_stock_from_row(raw_row, target_area_name):
    if not raw_row or not target_area_name:
        return 0

    target_keywords = SUBSTORE_AREA_KEYWORD_MAP.get(
        target_area_name, [target_area_name]
    )

    for col_name, val in raw_row.items():
        col_lower = col_name.lower().strip()
        if any(kw.lower() in col_lower for kw in target_keywords):
            return safe_int(val)

    clean_target = (
        target_area_name.replace("Area", "")
        .replace("C&I", "")
        .strip()
        .lower()
    )
    if clean_target:
        for col_name, val in raw_row.items():
            if clean_target in col_name.lower():
                return safe_int(val)

    return 0


# --- CONSUMPTION ENGINE ---
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

        mat_col = None
        for c in df_log.columns:
            c_l = c.lower()
            if any(
                k in c_l
                for k in [
                    "material",
                    "mat code",
                    "item code",
                    "sap code",
                    "code",
                    "mat",
                ]
            ):
                mat_col = c
                break

        if not mat_col:
            for c in df_log.columns:
                if not any(
                    k in c.lower()
                    for k in ["time", "date", "timestamp", "user", "name"]
                ):
                    mat_col = c
                    break

        if not mat_col:
            return {}

        action_col = None
        for c in df_log.columns:
            c_l = c.lower()
            if any(
                k in c_l
                for k in [
                    "action",
                    "transaction",
                    "type",
                    "status",
                    "movement",
                    "nature",
                    "particular",
                ]
            ):
                action_col = c
                break

        if action_col:

            def is_valid_removal(val):
                s = str(val).lower().strip()
                return ("remov" in s) and ("add" not in s)

            mask = df_log[action_col].astype(str).apply(is_valid_removal)
            if mask.sum() > 0:
                df_log = df_log[mask]
            else:
                return {}

        df_log["clean_mat"] = (
            df_log[mat_col]
            .astype(str)
            .str.replace(r"\.0$", "", regex=True)
            .str.strip()
            .str.lstrip("0")
        )

        qty_col = next(
            (
                c
                for c in df_log.columns
                if any(
                    k in c.lower()
                    for k in ["qty", "quantity", "issued", "nos", "count"]
                )
            ),
            None,
        )
        if qty_col:
            df_log["clean_qty"] = pd.to_numeric(
                df_log[qty_col].astype(str).str.extract(r"(\d+)", expand=False),
                errors="coerce",
            ).fillna(1)
        else:
            df_log["clean_qty"] = 1.0

        grouped = df_log.groupby("clean_mat")["clean_qty"].sum().to_dict()

        res = {}
        for m_code, total_removals in grouped.items():
            if m_code and m_code not in ["nan", "none", "n/a", ""]:
                tot = float(total_removals)
                if tot > 0:
                    m_cons = round(tot / float(analysis_months), 2)
                    if m_cons == 0.0:
                        m_cons = 0.08
                    repl_cycle = round(1.0 / m_cons, 1) if m_cons > 0 else 0.0
                    res[str(m_code)] = (m_cons, repl_cycle, int(tot))
        return res
    except Exception:
        return {}


# --- INVENTORY TEAM HIERARCHY MODAL ---
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
      <path d="M 915 140 L 915 165" stroke="#0284c7" stroke-width="2.5" fill="none"/>
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


# --- CHANGE PASSWORD MODAL ---
@st.dialog("🔑 Change Area Password")
def change_password_dialog(area_key):
    st.markdown(f"**Area:** `{area_key}`")
    curr_pass = st.text_input(
        "Current Password", type="password", key="curr_pwd_input"
    )
    new_pass = st.text_input("New Password", type="password", key="new_pwd_input")
    confirm_pass = st.text_input(
        "Confirm New Password", type="password", key="conf_pwd_input"
    )

    if st.button("Update Password", use_container_width=True, type="primary"):
        c_curr = curr_pass.strip()
        c_new = new_pass.strip()
        c_conf = confirm_pass.strip()

        db = fetch_passwords()
        stored_hash = str(db.get(area_key, "")).strip().lower()

        is_curr_valid = stored_hash and (hash_pass(c_curr).lower() == stored_hash)

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


# --- SMART GOOGLE FORM FAST-ENTRY MODAL (PRE-FILLED SEARCHABLE PORTAL) ---
@st.dialog("📝 Store-Room Inventory Log (Fast Entry)", width="large")
def show_entry_form_dialog():
    st.markdown("### ⚡ Fast Smart Spares Entry")
    st.caption(
        "Select Transaction and search Spare by Material Code or Name. "
        "Form will open pre-filled with your selection directly at the next section."
    )

    # 1. Transaction Type
    tx_type = st.radio(
        "Item Transaction *",
        options=[
            "Added in Store-Room Inventory",
            "Removed from Store-Room Inventory",
        ],
        horizontal=True,
        key="fast_entry_tx_type",
    )

    # 2. Material Code / Instrument Name Search Bar
    kw = st.text_input(
        "🔍 Type Material Code or Instrument Name:",
        placeholder="e.g. 1004521 or Pressure or Flow or pH...",
        key="fast_entry_search_box",
    ).strip()

    chosen_inst_type = None
    chosen_mat_code = "N/A"

    if kw:
        matches = search_stock_matrix_catalog(
            kw, st.session_state["data_timestamp"]
        )
        if matches:
            st.caption(f"Found {len(matches)} matching instruments:")
            labels = [m["label"] for m in matches]
            selected_idx = st.selectbox(
                "Select Matching Instrument:",
                range(len(matches)),
                format_func=lambda i: labels[i],
                key="fast_entry_chosen_idx",
            )
            item = matches[selected_idx]
            chosen_inst_type = item["description"]
            chosen_mat_code = item["mat_code"]
        else:
            st.warning(f"No catalog item matches '{kw}'. Try another keyword.")

    # Fallback direct type list if technician wants to choose category directly
    if not chosen_inst_type:
        common_types = [
            "Pressure Transmitter",
            "Flow Transmitter",
            "Flow Element",
            "Density Transmitter",
            "PH Transmitter",
            "pH Electrode",
            "Conductivity Transmitter",
            "Conductivity Cell",
            "Level Transmitter",
            "Temperature Transmitter",
            "Control Valve",
            "Positioner",
            "Solenoid Valve",
            "Limit Switch",
            "Load Cell",
        ]
        chosen_inst_type = st.selectbox(
            "Or Pick Standard Type from List:",
            common_types,
            key="fast_entry_fallback_select",
        )

    if chosen_inst_type:
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-left: 4px solid #0284c7; padding: 10px 14px; border-radius: 8px; margin: 10px 0; font-size: 13px;">
                <b>Transaction:</b> <span style="color:#0284c7; font-weight:700;">{tx_type}</span><br>
                <b>Instrument:</b> <span style="font-weight:700;">{chosen_inst_type}</span> | <b>Mat Code:</b> <code>{chosen_mat_code}</code>
            </div>
            """,
            unsafe_allow_html=True,
        )

        q_txn = urllib.parse.quote_plus(tx_type)
        q_inst = urllib.parse.quote_plus(chosen_inst_type)
        prefilled_url = (
            f"{GOOGLE_FORM_BASE_URL}?usp=pp_url&"
            f"{FORM_ENTRY_TRANSACTION}={q_txn}&"
            f"{FORM_ENTRY_INSTRUMENT}={q_inst}"
        )

        st.link_button(
            "🚀 Open Full Screen Form (New Tab)",
            prefilled_url,
            use_container_width=True,
        )

        st.markdown("---")
        st.caption(
            "💡 Both options are already pre-selected! Click **Next** below to fill specific specs/serial no:"
        )
        st.components.v1.iframe(prefilled_url, height=750, scrolling=True)


# --- AREA ACCESS CHECK ---
def check_authentication(area_key):
    if not is_area_direct_mode or st.session_state.get("auth_status", {}).get(
        area_key, False
    ):
        return True

    area_cfg = AREA_CONFIGS.get(area_key, {})
    zone_title = area_cfg.get("title", f"{area_key} Spares Inventory")
    zone_mgr = area_cfg.get("manager", "Area Incharge")
    zone_type = area_cfg.get("zone_type", "Refinery Process Area")
    accent_col = area_cfg.get("color", "#0284c7")

    logo_html = (
        f'<img src="data:image/png;base64,{__import__("base64").b64encode(open(NALCO_LOGO_PATH, "rb").read()).decode()}" width="65"/>'
        if os.path.exists(NALCO_LOGO_PATH)
        else '<div style="font-size: 32px;">🏛️</div>'
    )

    col1, col2, col3 = st.columns([1, 1.35, 1])

    with col2:
        st.markdown(
            f"""
            <div style="width: 100%; background: #ffffff; padding: 24px 22px 18px 22px; border-radius: 14px; border: 1.5px solid #cbd5e1; border-top: 4px solid {accent_col}; box-shadow: 0 4px 18px rgba(15, 23, 42, 0.06); text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin-top: 30px; margin-bottom: 18px; box-sizing: border-box;">
                <div style="display: flex; justify-content: center; margin-bottom: 10px;">
                    {logo_html}
                </div>
                <div style="color: #0f172a; margin: 0; font-size: 16.5px; font-weight: 800; line-height: 1.35;">
                    NATIONAL ALUMINIUM COMPANY LIMITED
                </div>
                <div style="color: {accent_col}; font-size: 11.5px; font-weight: 700; margin-top: 4px; text-transform: uppercase; letter-spacing: 0.5px;">
                    {zone_type}
                </div>
                <div style="height: 1px; background: #e2e8f0; margin: 14px 0 12px 0;"></div>
                <div style="font-size: 15px; font-weight: 800; color: #0f172a;">
                    📍 {area_key} Security Gateway
                </div>
                <div style="font-size: 12px; color: #64748b; margin-top: 3px; font-weight: 600;">
                    {zone_mgr}
                </div>
                <p style="color: #64748b; font-size: 11.5px; margin: 6px 0 0 0;">
                    Enter the authorized area access key to unlock telemetry records.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        pwd = st.text_input(
            "Security Password",
            type="password",
            key=f"login_{area_key}",
            placeholder="••••••••",
        )

        if st.button("Unlock Portal 🔓", use_container_width=True, type="primary"):
            c_pwd = pwd.strip()
            db = fetch_passwords()
            stored_hash = str(db.get(area_key, "")).strip().lower()

            is_valid = bool(stored_hash and hash_pass(c_pwd).lower() == stored_hash)

            if is_valid:
                st.session_state["auth_status"][area_key] = True
                st.success(f"✅ Access Granted: {area_key}")
                time.sleep(0.6)
                st.rerun()
            else:
                st.error("❌ Incorrect Password. Contact Lead Admin.")

    return False


# --- HOD / MASTER LANDING PAGE CHECK ---
def check_hod_authentication():
    if st.session_state.get("hod_auth_user") is not None:
        return True

    col1, col2, col3 = st.columns([1, 1.35, 1])

    with col2:
        logo_html = (
            f'<img src="data:image/png;base64,{__import__("base64").b64encode(open(NALCO_LOGO_PATH, "rb").read()).decode()}" width="65"/>'
            if os.path.exists(NALCO_LOGO_PATH)
            else '<div style="font-size: 32px;">🏛️</div>'
        )

        st.markdown(
            f"""
            <div style="width: 100%; background: #ffffff; padding: 24px 20px 18px 20px; border-radius: 12px; border: 1px solid #cbd5e1; box-shadow: 0 4px 18px rgba(15, 23, 42, 0.05); text-align: center; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin-top: 30px; margin-bottom: 18px; box-sizing: border-box;">
                <div style="display: flex; justify-content: center; margin-bottom: 12px;">
                    {logo_html}
                </div>
                <div style="color: #0f172a; margin: 0; font-size: 17px; font-weight: 800; line-height: 1.35; text-align: center;">
                    NATIONAL ALUMINIUM COMPANY LIMITED
                </div>
                <div style="color: #0284c7; font-size: 12px; font-weight: 700; margin-top: 6px; text-transform: uppercase; text-align: center; letter-spacing: 0;">
                    Instrumentation Spares &amp; Inventory Cell
                </div>
                <div style="height: 1px; background: #e2e8f0; margin: 16px 0 14px 0;"></div>
                <div style="font-size: 13.5px; font-weight: 700; color: #1e293b; text-align: center;">
                    Planning Cell Master Access
                </div>
                <p style="color: #64748b; font-size: 12px; margin: 3px 0 0 0; text-align: center;">
                    Authorized for HOD (C&amp;I) &amp; Central Planning Officers
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        user_input_id = st.text_input(
            "Personal No. (P.No.)",
            placeholder="e.g. 06505",
            key="hod_user_id_input",
        ).strip()

        user_input_pin = st.text_input(
            "Security PIN",
            type="password",
            placeholder="••••••••",
            key="hod_pin_input",
        ).strip()

        if st.button(
            "Authenticate & Enter", use_container_width=True, type="primary"
        ):
            clean_id = user_input_id.lstrip("0")
            matched_user = None
            for uid, udata in MASTER_AUTHORIZED_USERS.items():
                if (
                    uid.lstrip("0") == clean_id
                    or uid.lower() == user_input_id.lower()
                ):
                    matched_user = udata
                    break

            if not matched_user:
                st.error("❌ Unauthorized Personal No. for Master Dashboard.")
            elif matched_user["pin"] != user_input_pin:
                st.error("❌ Incorrect password. Please contact admin, 9742900004")
            else:
                st.session_state["hod_auth_user"] = matched_user
                st.success(f"✅ Authenticated: {matched_user['name']}")
                time.sleep(0.8)
                st.rerun()

    return False


# --- SUB-STORE ITEMS MODAL ---
@st.dialog("📦 Area Spares in C&I Sub Store", width="large")
def show_substore_items_dialog(current_area_name):
    substore_cfg = AREA_CONFIGS.get("C&I Sub Store")
    if not substore_cfg:
        st.error("❌ C&I Sub Store configuration missing.")
        return

    target_tags = SUBSTORE_AREA_KEYWORD_MAP.get(
        current_area_name, [current_area_name]
    )

    with st.spinner("Fetching Sub-Store inventory..."):
        df_sub = fetch_data(
            substore_cfg["sheet_url"], st.session_state["data_timestamp"]
        )
        df_sub.columns = df_sub.columns.str.strip()
        mapping = resolve_columns(df_sub)

        name_col = mapping["name"]
        mat_col = mapping["material"]
        specs_col = mapping["specs"]
        store_col = mapping["store"]
        belongs_col = mapping.get("area_belongs", "Belongs To Area")

        def is_strict_area_match(val):
            if pd.isna(val):
                return False
            val_clean = str(val).strip()
            return any(tag.lower() in val_clean.lower() for tag in target_tags)

        filtered_sub = df_sub[
            df_sub[belongs_col].apply(is_strict_area_match)
        ].copy()

    st.markdown(
        f"#### 📍 Dedicated Available Spares for: `{current_area_name}`"
    )
    st.caption(
        f"Filtering Sub-Store for tags: {', '.join([f'`{t}`' for t in target_tags])} (Stock > 0 Only)"
    )

    display_data = []
    for _, r in filtered_sub.iterrows():
        qty = safe_int(r.get(store_col, 0))

        if qty <= 0:
            continue

        display_data.append({
            "Material Code": clean_material_code(r.get(mat_col, "N/A")),
            "Instrument Name": str(r.get(name_col, "N/A")).strip(),
            "Specifications": str(r.get(specs_col, "N/A")).strip(),
            "Sub-Store Stock": qty,
            "Belongs To Area": str(r.get(belongs_col, "N/A")).strip(),
        })

    df_display = pd.DataFrame(display_data)

    if df_display.empty:
        st.info(
            f"ℹ️ Currently no available spares (stock > 0) in Sub Store for"
            f" {current_area_name}."
        )
        return

    q = st.text_input(
        "🔍 Filter by Name, Specs, or Material Code:", "", key="sub_search_box"
    ).strip()
    if q:
        df_display = df_display[
            df_display.astype(str)
            .apply(lambda x: x.str.contains(q, case=False, na=False))
            .any(axis=1)
        ]

    st.markdown(
        f"**Found `{len(df_display)}` available items in Sub Store:**"
    )
    st.dataframe(df_display, use_container_width=True, hide_index=True)


# --- SENDER MODAL: STREAMLINED BROADCAST & MATERIAL REQUEST ---
@st.dialog("📢 Inter-Area Dispatch & Material Request", width="large")
def show_broadcast_message_dialog(current_area_name):
    st.markdown(f"**Originating Area:** 📍 `{current_area_name}`")

    msg_category = st.radio(
        "Select Operation Mode:",
        ["📢 General Message / Announcement", "📦 Material Spare Request"],
        horizontal=True,
    )

    other_areas = [a for a in AREA_CONFIGS.keys() if a != current_area_name]
    target_options = ["📢 ALL AREAS (Plant-wide Broadcast)"] + other_areas

    c_top1, c_top2 = st.columns([1.5, 1])
    with c_top1:
        selected_target_opt = st.selectbox(
            "Send Request / Message To:",
            target_options,
            key="bc_unified_target_select",
        )
    with c_top2:
        priority_level = st.radio(
            "Priority:",
            ["Normal", " Urgent Breakdown"],
            horizontal=True,
            key="bc_priority_radio",
        )

    target_area = (
        "ALL"
        if "ALL AREAS" in selected_target_opt
        else selected_target_opt.replace("📍 ", "").strip()
    )

    selected_material_payload = None
    msg_body = ""

    if msg_category == "📦 Material Spare Request":
        search_kw = st.text_input(
            "Type Material Code or Instrument Name:",
            placeholder="e.g. 5040012 or RTD or Pressure Transmitter...",
            key="mat_matrix_search",
        ).strip()

        if search_kw:
            matching_items = search_stock_matrix_catalog(
                search_kw, st.session_state["data_timestamp"]
            )
            if matching_items:
                st.caption(f"Found {len(matching_items)} catalog matches:")
                labels = [item["label"] for item in matching_items]
                chosen_idx = st.selectbox(
                    "Select Matching Instrument:",
                    range(len(matching_items)),
                    format_func=lambda x: labels[x],
                    key="mat_matrix_chosen_idx",
                )
                selected_item = matching_items[chosen_idx]

                st.markdown(
                    f"""
                    <div style="background: #ffffff; border: 1.5px solid #e2e8f0; border-left: 4px solid #0284c7; padding: 9px 13px; border-radius: 6px; font-size: 12.5px; margin-bottom: 10px;">
                        <b>Selected Instrument:</b> {selected_item['description']}<br>
                        <b>Material Code:</b> <span style="color:#0284c7; font-weight:700;">{selected_item['mat_code']}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                c_qty, c_purp = st.columns([1, 2.5])
                with c_qty:
                    req_qty = st.number_input(
                        "Required Quantity (Nos):", min_value=1, max_value=50, value=1
                    )
                with c_purp:
                    req_purpose = st.text_input(
                        "Tag No. / Plant Location / Purpose:",
                        placeholder="e.g. Breakdown replacement at Ball Mill #2",
                    )

                selected_material_payload = {
                    "material_code": selected_item["mat_code"],
                    "instrument_name": selected_item["description"],
                    "requested_qty": int(req_qty),
                    "purpose": req_purpose.strip(),
                    "_raw_row": selected_item.get("_raw_row", {}),
                }
            else:
                st.warning(
                    f"⚠️ No catalog item found for '{search_kw}'. Try another keyword."
                )

    else:
        msg_body = st.text_area(
            "Message Content:",
            placeholder="Type plant broadcast, shutdown update, or inter-area query...",
            height=100,
            key="bc_body_text",
        ).strip()

    if st.button("🚀 Dispatch Request", type="primary", use_container_width=True):
        if (
            msg_category == "📦 Material Spare Request"
            and not selected_material_payload
        ):
            st.error(
                "❌ Please search and select an instrument from the catalog list first!"
            )
            return

        if msg_category == "📢 General Message / Announcement" and not msg_body:
            st.error("❌ Message cannot be empty!")
            return

        is_urgent = "Urgent" in priority_level
        sender_label = AREA_CONFIGS.get(current_area_name, {}).get(
            "manager", f"{current_area_name} Incharge"
        )

        broadcast_record = {
            "msg_id": f"MSG-{int(time.time())}",
            "msg_type": (
                "MATERIAL_REQUEST"
                if msg_category == "📦 Material Spare Request"
                else "ANNOUNCEMENT"
            ),
            "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
            "from_area": current_area_name,
            "to_area": target_area,
            "sender_officer": sender_label,
            "priority": "URGENT" if is_urgent else "NORMAL",
            "message": msg_body,
            "material_details": selected_material_payload,
            "seen_by": [],
        }

        GLOBAL_MESSAGES.append(broadcast_record)
        try:
            requests.post(
                AUTH_API_URL,
                json={"action": "INTERAREA_BROADCAST", "data": broadcast_record},
                timeout=3,
            )
        except Exception:
            pass

        st.success(f"✅ Dispatched successfully to `{target_area}`!")
        time.sleep(1.0)
        st.rerun()


# --- NOTIFICATIONS & INCOMING ALERTS MODAL ---
@st.dialog("🔔 Notifications & Incoming Alerts", width="large")
def show_notifications_dialog(current_area_name):
    active_messages = []
    for m in GLOBAL_MESSAGES:
        is_target = m["to_area"] == current_area_name or m["to_area"] == "ALL"
        not_self = m.get("from_area") != current_area_name

        seen_list = (
            m.get("seen_by")
            if isinstance(m.get("seen_by"), list)
            else ([m.get("seen_by")] if m.get("seen_by") else [])
        )
        is_not_seen = current_area_name not in seen_list

        if is_target and not_self and is_not_seen:
            active_messages.append(m)

    if not active_messages:
        st.info("🎉 No unread messages or material requests for your area.")
        return

    st.markdown(f"### 🔔 Pending Alerts ({len(active_messages)})")

    for m in active_messages:
        m_id = m["msg_id"]
        from_a = m["from_area"]
        m_time = m["timestamp"]
        is_urg = m.get("priority") == "URGENT"
        is_mat_req = m.get("msg_type") == "MATERIAL_REQUEST"
        mat_info = m.get("material_details")

        border_col = (
            "#ef4444" if is_urg else ("#16a34a" if is_mat_req else "#0284c7")
        )

        if is_mat_req:
            badge_html = """<span style="font-size: 11px; font-weight: 700; color: #166534; background: #dcfce7; padding: 3px 10px; border-radius: 12px; border: 1px solid #86efac;">📦 MATERIAL SPARE REQUEST</span>"""
        elif m["to_area"] == "ALL":
            badge_html = """<span style="font-size: 11px; font-weight: 700; color: #0369a1; background: #e0f2fe; padding: 3px 10px; border-radius: 12px;">📢 PLANT BROADCAST</span>"""
        else:
            badge_html = """<span style="font-size: 11px; font-weight: 700; color: #4338ca; background: #e0e7ff; padding: 3px 10px; border-radius: 12px;">📍 DIRECT MESSAGE</span>"""

        if is_urg:
            badge_html += """ <span style="font-size: 11px; font-weight: 700; color: #b91c1c; background: #fee2e2; padding: 3px 8px; border-radius: 12px; margin-left: 4px;"> URGENT</span>"""

        mat_block_html = ""
        if is_mat_req and mat_info:
            raw_row_data = mat_info.get("_raw_row", {})
            area_stock = (
                extract_area_stock_from_row(raw_row_data, current_area_name)
                if raw_row_data
                else mat_info.get("target_area_stock", 0)
            )

            stock_badge_col = "#15803d" if area_stock > 0 else "#dc2626"
            purpose_text = mat_info.get("purpose", "")
            purpose_line = (
                f"<br><b>Plant Location / Purpose:</b> {purpose_text}"
                if purpose_text
                else ""
            )

            mat_block_html = f"""
            <div style="background: #ffffff; border: 1.5px solid #86efac; border-radius: 8px; padding: 12px; margin: 10px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 1px dashed #cbd5e1; padding-bottom: 6px; margin-bottom: 6px;">
                    <span style="font-size: 13.5px; font-weight: 800; color: #0f172a;">🛠️ {mat_info.get('instrument_name', 'Instrument')}</span>
                    <div>
                        <span style="font-size: 12px; font-weight: 800; color: #dc2626; background: #fee2e2; padding: 2px 8px; border-radius: 6px;">Requested: {mat_info.get('requested_qty', 1)} Nos</span>
                        <span style="font-size: 12px; font-weight: 800; color: {stock_badge_col}; background: #f0fdf4; padding: 2px 8px; border-radius: 6px; border: 1px solid #bbf7d0; margin-left: 4px;">Your Stock: {area_stock} Nos</span>
                    </div>
                </div>
                <div style="font-size: 12px; color: #475569; line-6: 1.6;">
                    <b>Material Code:</b> <span style="color:#0284c7; font-weight:700;">{mat_info.get('material_code', 'N/A')}</span>{purpose_line}
                </div>
            </div>
            """

        msg_body_html = ""
        if m.get("message"):
            msg_body_html = f"""
            <div style="font-size: 12.5px; color: #334155; margin-top: 6px; background: #f8fafc; padding: 8px 10px; border-radius: 6px; border-left: 3px solid #94a3b8;">
                <b>Note:</b> {m['message']}
            </div>
            """

        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-left: 5px solid {border_col}; padding: 14px 16px; border-radius: 10px; margin-bottom: 12px;">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div>
                        <span style="font-size: 14px; font-weight: 800; color: #0f172a;">📍 From: {from_a}</span>
                        <span style="margin-left: 8px;">{badge_html}</span>
                    </div>
                    <span style="font-size: 11px; color: #64748b; font-weight: 600;">🕒 {m_time}</span>
                </div>
                <div style="font-size: 11.5px; color: #64748b; margin-top: 3px;">
                    <b>Initiated by:</b> {m.get('sender_officer', 'Area Officer')}
                </div>
                {mat_block_html}
                {msg_body_html}
            </div>
            """,
            unsafe_allow_html=True,
        )

        c_reply, c_seen = st.columns([3.6, 1.4], vertical_alignment="center")

        with c_seen:
            ack_btn_text = "✅ Acknowledge / Seen" if is_mat_req else "👁️ Mark Seen"
            if st.button(
                ack_btn_text,
                key=f"seen_{m_id}",
                use_container_width=True,
                type="primary",
            ):
                if not isinstance(m.get("seen_by"), list):
                    old_val = m.get("seen_by")
                    m["seen_by"] = [old_val] if old_val else []

                if current_area_name not in m["seen_by"]:
                    m["seen_by"].append(current_area_name)

                try:
                    requests.post(
                        AUTH_API_URL,
                        json={
                            "action": "RESOLVE_MESSAGE",
                            "msg_id": m_id,
                            "seen_by": current_area_name,
                        },
                        timeout=3,
                    )
                except Exception:
                    pass

                st.rerun()

        with c_reply:
            with st.expander(f"↩️ Reply / Confirm Availability to {from_a}"):
                reply_placeholder = (
                    "e.g. Approved. You can collect 1 unit from our area store..."
                    if is_mat_req
                    else f"Type reply back to {from_a}..."
                )
                reply_text = st.text_input(
                    "Reply Text:",
                    placeholder=reply_placeholder,
                    key=f"rep_{m_id}",
                    label_visibility="collapsed",
                )
                if st.button(
                    "🚀 Send Response", key=f"send_{m_id}", use_container_width=True
                ):
                    clean_reply = reply_text.strip()
                    if not clean_reply:
                        st.error("Reply text cannot be empty!")
                    else:
                        subject_tag = (
                            f"Spare Req [{mat_info.get('material_code', '')}]"
                            if is_mat_req and mat_info
                            else "Message"
                        )
                        reply_record = {
                            "msg_id": f"MSG-{int(time.time())}",
                            "msg_type": "ANNOUNCEMENT",
                            "timestamp": datetime.now().strftime("%d-%b-%Y %H:%M:%S"),
                            "from_area": current_area_name,
                            "to_area": from_a,
                            "sender_officer": "Area Reply",
                            "priority": "NORMAL",
                            "message": f"↩️ Re: [{subject_tag}] -> {clean_reply}",
                            "seen_by": [],
                        }
                        GLOBAL_MESSAGES.append(reply_record)

                        if not isinstance(m.get("seen_by"), list):
                            old_val = m.get("seen_by")
                            m["seen_by"] = [old_val] if old_val else []

                        if current_area_name not in m["seen_by"]:
                            m["seen_by"].append(current_area_name)

                        try:
                            requests.post(
                                AUTH_API_URL,
                                json={
                                    "action": "INTERAREA_BROADCAST",
                                    "data": reply_record,
                                },
                                timeout=3,
                            )
                            requests.post(
                                AUTH_API_URL,
                                json={
                                    "action": "RESOLVE_MESSAGE",
                                    "msg_id": m_id,
                                    "seen_by": current_area_name,
                                },
                                timeout=3,
                            )
                        except Exception:
                            pass

                        st.success(f"✅ Response sent to {from_a}!")
                        time.sleep(0.8)
                        st.rerun()

        st.markdown(
            "<div style='margin: 8px 0; border-bottom: 1px dashed #cbd5e1;'></div>",
            unsafe_allow_html=True,
        )


# --- DYNAMIC THEMED ROW RENDERER ---
def render_row(row, mapping, current_area_name):
    name_key = mapping["name"]
    mat_key = mapping["material"]
    specs_key = mapping["specs"]
    field_key = mapping["field"]
    store_key = mapping["store"]
    area_belongs_key = mapping.get("area_belongs", "Belongs To Area")

    inst_name = (
        str(row[name_key]).strip()
        if name_key in row and pd.notna(row[name_key])
        else "No Name"
    )
    mat_code = clean_material_code(row[mat_key]) if mat_key in row else "N/A"
    full_spec = (
        str(row[specs_key]).strip()
        if specs_key in row and pd.notna(row[specs_key])
        else "No Specs Added"
    )
    spares_store = safe_int(row[store_key]) if store_key in row else 0
    cleaned_spec = full_spec.replace("•", "").strip()
    show_name_flag = mapping.get("show_name", True)

    area_cfg = AREA_CONFIGS.get(current_area_name, {})
    theme_accent = area_cfg.get("color", "#0284c7")

    if current_area_name == "C&I Sub Store":
        belongs_val = (
            str(row[area_belongs_key]).strip()
            if area_belongs_key in row and pd.notna(row[area_belongs_key])
            else "Unassigned / General"
        )

        card_html = f"""
        <div class="inventory-card">
            <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                <div style="flex: 2; min-width: 180px;">
                    <h4 style="margin:0; color:#0f172a; font-size:16px; font-weight:700;">{inst_name if show_name_flag else ""}</h4>
                    <div style="font-size: 11px; color: {theme_accent}; font-weight: 700; margin-top: 2px;">Mat. Code: {mat_code}</div>
                </div>
                <div style="flex: 2.5; min-width: 200px;">
                    <div class="specs-box" style="border-left: 3px solid {theme_accent};"><b>Specs:</b> {cleaned_spec}</div>
                </div>
                <div style="flex: 1.5; min-width: 140px;" class="metric-box">
                    <div class="metric-lbl">Belongs To Area</div>
                    <div class="metric-val" style="font-size: 14px; font-weight: 700; color: #15803d;">📍 {belongs_val}</div>
                </div>
                <div style="flex: 1; min-width: 110px;" class="metric-box">
                    <div class="metric-lbl">Store-Room Stock</div>
                    <div class="metric-val" style="font-size: 17px; font-weight: 700; color: #0f172a;">{spares_store}</div>
                </div>
            </div>
        </div>
        """
        st.markdown(card_html, unsafe_allow_html=True)
        return

    field_count = safe_int(row[field_key]) if field_key in row else 0

    name_lower = inst_name.lower()
    if "transmitter" in name_lower or "converter" in name_lower:
        healthy_stock = max(2, int(field_count * 0.20))
    elif (
        "element" in name_lower or "switch" in name_lower or "probe" in name_lower
    ):
        healthy_stock = max(3, int(field_count * 0.30))
    else:
        healthy_stock = max(2, int(field_count * 0.15))

    shortfall_excess = spares_store - healthy_stock

    if shortfall_excess < 0:
        status_html = (
            '<div class="status-badge status-shortfall"> Shortfall'
            f" ({shortfall_excess})</div>"
        )
    elif shortfall_excess > 0:
        status_html = (
            '<div class="status-badge status-surplus">✅ Surplus'
            f" (+{shortfall_excess})</div>"
        )
    else:
        status_html = (
            '<div class="status-badge status-balanced">👌 Balanced (0)</div>'
        )

    card_html = f"""
    <div class="inventory-card">
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
            <div style="flex: 2; min-width: 180px;">
                <h4 style="margin:0; color:#0f172a; font-size:16px; font-weight:700;">{inst_name if show_name_flag else ""}</h4>
                <div style="font-size: 11px; color: {theme_accent}; font-weight: 700; margin-top: 2px;">Mat. Code: {mat_code}</div>
            </div>
            <div style="flex: 2.5; min-width: 200px;">
                <div class="specs-box" style="border-left: 3px solid {theme_accent};"><b>Specs:</b> {cleaned_spec}</div>
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


def inject_custom_css(hide_sidebar=False):
    sidebar_hide_css = ""
    if hide_sidebar:
        sidebar_hide_css = """
        [data-testid="stSidebar"],
        [data-testid="collapsedControl"],
        section[data-testid="stSidebar"] {
            display: none !important;
        }
        """

    css = f"""
    <style>
    {sidebar_hide_css}
    .stApp {{ background-color: #f8fafc; }}
    h1, h2, h3 {{ color: #1e293b !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; }}
    
    .header-pill {{
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
    }}

    div[data-testid="column"] {{
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }}

    button[key="team_btn"],
    button[key="urgent_pr_btn"],
    button[key="substore_items_btn"],
    button[key="broadcast_btn"],
    button[key="notify_btn"],
    button[key="fast_entry_btn"] {{
        height: 42px !important;
        min-height: 42px !important;
        max-height: 42px !important;
        line-height: 42px !important;
        padding: 0px 14px !important;
        margin: 0 !important;
        border-radius: 24px !important;
        font-weight: 800 !important;
        font-size: 12.5px !important;
        display: inline-flex !important;
        align-items: center !important;
        justify-content: center !important;
        box-sizing: border-box !important;
        transition: all 0.2s ease-in-out !important;
    }}

    button[key="fast_entry_btn"] {{
        background: linear-gradient(135deg, #0284c7 0%, #2563eb 100%) !important;
        color: #ffffff !important;
        border: 2px solid #60a5fa !important;
        box-shadow: 0 2px 10px rgba(37, 99, 235, 0.3) !important;
    }}

    button[key="team_btn"] {{
        background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%) !important;
        color: #ffffff !important;
        border: 2px solid #38bdf8 !important;
        box-shadow: 0 2px 10px rgba(2, 132, 199, 0.4) !important;
    }}

    button[key="substore_items_btn"] {{
        background: linear-gradient(135deg, #059669 0%, #047857 100%) !important;
        color: #ffffff !important;
        border: 2px solid #34d399 !important;
        box-shadow: 0 2px 10px rgba(5, 150, 105, 0.3) !important;
    }}

    button[key="broadcast_btn"] {{
        background: linear-gradient(135deg, #7c3aed 0%, #6d28d9 100%) !important;
        color: #ffffff !important;
        border: 2px solid #a78bfa !important;
        box-shadow: 0 2px 10px rgba(124, 58, 237, 0.3) !important;
    }}

    button[key="notify_btn"] {{
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%) !important;
        color: #ffffff !important;
        border: 2px solid #fcd34d !important;
        box-shadow: 0 2px 10px rgba(217, 119, 6, 0.3) !important;
    }}

    button[key="urgent_pr_btn"] {{
        background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%) !important;
        color: #ffffff !important;
        border: 2.5px solid #f87171 !important;
        box-shadow: 0 0 16px rgba(239, 68, 68, 0.6), 0 4px 12px rgba(220, 38, 38, 0.2) !important;
    }}

    section[data-testid="stSidebar"] {{
        background-color: #f1f5f9 !important;
        border-right: 2px solid #cbd5e1 !important;
    }}
    
    .sidebar-section-title {{
        font-size: 11.5px !important;
        font-weight: 800 !important;
        color: #0f172a !important;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        margin-top: 10px;
        margin-bottom: 6px;
        display: flex;
        align-items: center;
        gap: 6px;
    }}

    .inventory-card {{ 
        background-color: #ffffff; 
        border-radius: 12px; 
        padding: 14px 18px; 
        box-shadow: 0 4px 12px rgba(0,0,0,0.03); 
        border: 1px solid #e2e8f0; 
        margin-bottom: 12px; 
        transition: all 0.15s ease-in-out;
    }}
    .inventory-card:hover {{ 
        border-color: #cbd5e1; 
        box-shadow: 0 6px 16px rgba(0,0,0,0.05); 
    }}
    .metric-box {{ 
        text-align: center; 
        padding: 6px; 
        background-color: #f8fafc; 
        border-radius: 8px; 
        border: 1px solid #f1f5f9; 
    }}
    .metric-val {{ 
        font-size: 17px; 
        font-weight: 700; 
        color: #0f172a; 
    }}
    .metric-lbl {{ 
        font-size: 10px; 
        text-transform: uppercase; 
        color: #64748b; 
        font-weight: 600; 
        margin-bottom: 2px; 
    }}
    .status-badge {{ 
        display: inline-block; 
        padding: 6px 10px; 
        border-radius: 20px; 
        font-size: 12px; 
        font-weight: 600; 
        text-align: center; 
        width: 100%; 
    }}
    .status-shortfall {{ background-color: #fee2e2; color: #dc2626; border: 1px solid #fca5a5; }}
    .status-surplus {{ background-color: #dcfce7; color: #16a34a; border: 1px solid #86efac; }}
    .status-balanced {{ background-color: #e0f2fe; color: #0284c7; border: 1px solid #7dd3fc; }}
    .specs-box {{ 
        background-color: #f8fafc; 
        padding: 6px 10px; 
        border-radius: 6px; 
        font-size: 11.5px; 
        color: #334155; 
    }}
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)


# --- TOP BAR ---
def render_top_bar(status_text="⚡ Live Spares Telemetry Active"):
    is_pr_active = st.session_state.get("smart_intelligence_mode", False)
    current_area = st.session_state.get("selected_area") or url_area

    pending_count = 0
    for m in GLOBAL_MESSAGES:
        if not current_area or m.get("from_area") == current_area:
            continue

        is_target = m["to_area"] == current_area or m["to_area"] == "ALL"
        seen_list = (
            m.get("seen_by")
            if isinstance(m.get("seen_by"), list)
            else ([m.get("seen_by")] if m.get("seen_by") else [])
        )
        is_not_seen = current_area not in seen_list

        if is_target and is_not_seen:
            pending_count += 1

    notify_label = (
        f"🔔 Alerts ({pending_count})"
        if pending_count > 0
        else "🔔 Notifications"
    )

    if is_pr_active:
        c_left, c_entry, c_mid, c_right = st.columns(
            [3.2, 1.8, 3.2, 1.8], vertical_alignment="center"
        )
        with c_left:
            st.markdown(
                f"""
                <div class="header-pill">
                    <span style="color: #10b981; font-size: 15px;">●</span> {status_text}
                </div>
                """,
                unsafe_allow_html=True,
            )
        with c_entry:
            if st.button(
                "📝 Fast Entry",
                key="fast_entry_btn",
                type="primary",
                use_container_width=True,
            ):
                show_entry_form_dialog()
        with c_mid:
            is_active = st.session_state["urgent_pr_filter_state"]
            btn_label = "✅ Showing Overdue PR" if is_active else " Show Overdue PR Only"
            if st.button(
                btn_label,
                key="urgent_pr_btn",
                type="primary",
                use_container_width=True,
            ):
                st.session_state["urgent_pr_filter_state"] = not is_active
                st.rerun()
        with c_right:
            if st.button(
                "👥 Team",
                key="team_btn",
                type="primary",
                use_container_width=True,
            ):
                show_team_modal()
    else:
        if current_area and current_area in AREA_CONFIGS:
            if current_area != "C&I Sub Store":
                c_left, c_entry, c_sub, c_bc, c_not, c_team = st.columns(
                    [2.6, 1.6, 1.6, 1.5, 1.5, 1.2], vertical_alignment="center"
                )
                with c_left:
                    st.markdown(
                        f"""
                        <div class="header-pill">
                            <span style="color: #10b981; font-size: 15px;">●</span> {status_text}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_entry:
                    if st.button(
                        "📝 Fast Entry",
                        key="fast_entry_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_entry_form_dialog()
                with c_sub:
                    if st.button(
                        "📦 In Sub-Store",
                        key="substore_items_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_substore_items_dialog(current_area)
                with c_bc:
                    if st.button(
                        "📢 Message",
                        key="broadcast_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_broadcast_message_dialog(current_area)
                with c_not:
                    if st.button(
                        notify_label,
                        key="notify_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_notifications_dialog(current_area)
                with c_team:
                    if st.button(
                        "👥 Team",
                        key="team_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_team_modal()
            else:
                c_left, c_entry, c_bc, c_not, c_team = st.columns(
                    [3.5, 1.8, 1.6, 1.6, 1.5], vertical_alignment="center"
                )
                with c_left:
                    st.markdown(
                        f"""
                        <div class="header-pill">
                            <span style="color: #10b981; font-size: 15px;">●</span> {status_text}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )
                with c_entry:
                    if st.button(
                        "📝 Fast Entry",
                        key="fast_entry_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_entry_form_dialog()
                with c_bc:
                    if st.button(
                        "📢 Message",
                        key="broadcast_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_broadcast_message_dialog(current_area)
                with c_not:
                    if st.button(
                        notify_label,
                        key="notify_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_notifications_dialog(current_area)
                with c_team:
                    if st.button(
                        "👥 Team",
                        key="team_btn",
                        type="primary",
                        use_container_width=True,
                    ):
                        show_team_modal()
        else:
            c_left, c_entry, c_team = st.columns(
                [6.2, 2.0, 1.8], vertical_alignment="center"
            )
            with c_left:
                st.markdown(
                    f"""
                    <div class="header-pill">
                        <span style="color: #10b981; font-size: 15px;">●</span> {status_text}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )
            with c_entry:
                if st.button(
                    "📝 Fast Entry",
                    key="fast_entry_btn",
                    type="primary",
                    use_container_width=True,
                ):
                    show_entry_form_dialog()
            with c_team:
                if st.button(
                    "👥 Inventory Team",
                    key="team_btn",
                    type="primary",
                    use_container_width=True,
                ):
                    show_team_modal()

    st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)


# ==============================================================================
# --- AUTHENTICATION GATEWAY (BEFORE ANY SIDEBAR OR TOPBAR RENDERING) ---
# ==============================================================================

# 1. DIRECT AREA URL ACCESS CHECK
if is_area_direct_mode:
    is_area_auth = st.session_state.get("auth_status", {}).get(url_area, False)
    if not is_area_auth:
        inject_custom_css(hide_sidebar=True)
        check_authentication(url_area)
        st.stop()

# 2. HOD / MASTER SUITE ACCESS CHECK
else:
    is_hod_auth = st.session_state.get("hod_auth_user") is not None
    if not is_hod_auth:
        inject_custom_css(hide_sidebar=True)
        check_hod_authentication()
        st.stop()

# --- AT THIS POINT USER IS AUTHENTICATED: RENDER SIDEBAR & TOP BAR ---
inject_custom_css(hide_sidebar=False)

active_tag = (
    f"📍 Active Area: {st.session_state['selected_area']}"
    if st.session_state["selected_area"]
    else "Master Control Room"
)
render_top_bar(status_text=active_tag)


# --- GLOBAL SIDEBAR QUICK PR SEARCH ENGINE HANDLER ---
def on_sidebar_search():
    if st.session_state.get("global_pr_search", "").strip():
        st.session_state["smart_intelligence_mode"] = True
        st.session_state["stock_matrix_mode"] = False
        if not is_area_direct_mode and not st.session_state.get("pr_selected_view"):
            st.session_state["pr_selected_view"] = "Combined"


# ==============================================================================
# --- RESTRUCTURED STREAMLINED SIDEBAR ---
# Sequence: 1. Branding -> 2. Navigation -> 3. Global Search -> 4. Parameters -> 5. User Profile
# ==============================================================================

with st.sidebar:
    # 1. BRANDING HEADER
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%); padding: 13px; border-radius: 10px; margin-bottom: 12px; text-align: center; border: 1px solid #334155;">
            <h4 style="margin:0; color:#38bdf8; font-size:13.5px; font-weight:800; letter-spacing:0.5px;">NALCO C&amp;I CONTROL PANEL</h4>
            <p style="margin:3px 0 0 0; color:#94a3b8; font-size:11px; font-weight:500;">Central Spares &amp; Inventory Suite</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # 2. PRIMARY PORTAL NAVIGATION
    if is_area_direct_mode:
        st.markdown(
            '<div class="sidebar-section-title">📌 Area Navigation</div>',
            unsafe_allow_html=True,
        )
        if st.button("📝 Log Spares Entry", use_container_width=True):
            show_entry_form_dialog()

        if not st.session_state["smart_intelligence_mode"]:
            if st.button("📈 Predictive PR Date", use_container_width=True):
                st.session_state["smart_intelligence_mode"] = True
                st.session_state["pr_selected_view"] = url_area
                st.query_params["area"] = url_area
                st.query_params["view"] = "pr"
                st.rerun()
        else:
            if st.button("📦 Back to Area Stock", use_container_width=True):
                st.session_state["smart_intelligence_mode"] = False
                st.session_state["pr_selected_view"] = None
                st.query_params["area"] = url_area
                if "view" in st.query_params:
                    del st.query_params["view"]
                st.rerun()
    else:
        st.markdown(
            '<div class="sidebar-section-title">🧭 Portal Navigation</div>',
            unsafe_allow_html=True,
        )
        if st.button("Dashboard Home", use_container_width=True):
            st.session_state["smart_intelligence_mode"] = False
            st.session_state["stock_matrix_mode"] = False
            st.session_state["selected_area"] = None
            st.session_state["pr_selected_view"] = None
            st.query_params.clear()
            st.rerun()

        if st.button("📝 Log Spares Entry", use_container_width=True):
            show_entry_form_dialog()

        if st.button("Predictive PR Intelligence", use_container_width=True):
            st.session_state["smart_intelligence_mode"] = True
            st.session_state["stock_matrix_mode"] = False
            st.session_state["selected_area"] = None
            st.session_state["pr_selected_view"] = None
            st.query_params["view"] = "pr"
            st.rerun()

        if st.button("Areawise Stock Matrix", use_container_width=True):
            st.session_state["stock_matrix_mode"] = True
            st.session_state["smart_intelligence_mode"] = False
            st.session_state["selected_area"] = None
            st.session_state["pr_selected_view"] = None
            st.query_params["view"] = "stock_matrix"
            st.rerun()

    st.markdown("<div style='margin: 10px 0; border-top: 1.5px solid #cbd5e1;'></div>", unsafe_allow_html=True)

    # 3. GLOBAL SEARCH
    st.markdown('<div class="sidebar-section-title">🔍 Quick Material Search</div>', unsafe_allow_html=True)
    st.text_input(
        "Search Mat Code/ Text:",
        placeholder="e.g. 90521... or RTD...",
        key="global_pr_search",
        on_change=on_sidebar_search,
        label_visibility="collapsed",
    )

    # 4. VIEW-SPECIFIC PARAMETERS (Only visible when PR mode is active)
    lead_time_months = 6
    analysis_months = 12
    if st.session_state.get("smart_intelligence_mode"):
        st.markdown("<div style='margin: 10px 0; border-top: 1.5px solid #cbd5e1;'></div>", unsafe_allow_html=True)
        st.markdown('<div class="sidebar-section-title">⚙️ Analysis Parameters</div>', unsafe_allow_html=True)
        lead_time_months = st.slider(
            "Procurement Lead Time (Months):",
            min_value=0,
            max_value=12,
            value=6,
            help="Setting to 0 displays direct stock runout / exhaustion dates without lead-time subtraction.",
        )
        if lead_time_months == 0:
            st.caption("⚡ Zero Lead Time: Showing direct runout dates.")

        analysis_months = st.selectbox(
            "Consumption Historical Span:", [6, 12, 24], index=1
        )

    # 5. USER SESSION & CONTROLS FOOTER
    st.markdown("<div style='margin: 14px 0 10px 0; border-top: 1.5px solid #cbd5e1;'></div>", unsafe_allow_html=True)

    if is_area_direct_mode:
        curr_mgr = AREA_CONFIGS.get(url_area, {}).get("manager", "Area Officer")
        st.markdown(
            f"""
            <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-left: 4px solid #0284c7; padding: 10px 12px; border-radius: 8px; margin-bottom: 10px;">
                <div style="font-size: 10px; font-weight: 800; color: #64748b; text-transform: uppercase;">Area Active Session</div>
                <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-top: 2px;">📍 {url_area}</div>
                <div style="font-size: 11px; color: #0284c7; font-weight: 600;">{curr_mgr}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        c_p1, c_p2 = st.columns(2)
        with c_p1:
            if st.button("🔑 Password", use_container_width=True):
                change_password_dialog(url_area)
        with c_p2:
            if st.button("🔒 Logout", use_container_width=True, key="area_logout"):
                st.session_state["auth_status"][url_area] = False
                st.rerun()

    else:
        if st.session_state.get("hod_auth_user"):
            u_info = st.session_state["hod_auth_user"]
            st.markdown(
                f"""
                <div style="background: #ffffff; border: 1.5px solid #cbd5e1; border-left: 4px solid #0284c7; padding: 10px 12px; border-radius: 8px; margin-bottom: 10px;">
                    <div style="font-size: 10px; font-weight: 800; color: #64748b; text-transform: uppercase;">Active Master Session</div>
                    <div style="font-size: 13px; font-weight: 700; color: #0f172a; margin-top: 2px;">👤 {u_info['name']}</div>
                    <div style="font-size: 11px; color: #0284c7; font-weight: 600;">{u_info['role']}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
            if st.button("🔒 Logout Session", use_container_width=True, key="master_logout"):
                st.session_state["hod_auth_user"] = None
                st.rerun()


# ==============================================================================
# --- MAIN APPLICATION VIEWS ---
# ==============================================================================

# --- VIEW 1: AREAWISE STOCK MATRIX VIEWER ---
if st.session_state["stock_matrix_mode"] and not is_area_direct_mode:
    st.markdown(
        """
        <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 30px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); text-align: center; margin-bottom: 25px;">
            <h1 style="color: #0f172a !important; margin: 0; font-size: 28px; font-weight: 800;">📊 Areawise Stock Matrix</h1>
            <p style="color: #475569 !important; margin-top: 8px; font-size: 14px;">Live centralized stock overview across all operating areas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    try:
        df_matrix = fetch_data(
            STOCK_MATRIX_URL, st.session_state["data_timestamp"]
        )
        df_matrix.columns = df_matrix.columns.str.strip()
        matrix_search = st.text_input(
            "🔍 Search (Material Code, Description or Area):", ""
        ).strip()
        filtered_matrix = (
            df_matrix[
                df_matrix.astype(str)
                .apply(
                    lambda x: x.str.contains(matrix_search, case=False, na=False)
                )
                .any(axis=1)
            ]
            if matrix_search
            else df_matrix
        )
        styled_matrix = filtered_matrix.style.set_table_styles([
            {
                "selector": "th",
                "props": [("font-weight", "bold"), ("color", "#000000")],
            },
            {
                "selector": "tr th",
                "props": [("font-weight", "bold"), ("color", "#000000")],
            },
        ]).set_properties(**{"color": "#000000"})
        st.dataframe(styled_matrix, use_container_width=True, height=600)
    except Exception as e:
        st.error(f"Error loading Stock Matrix data: {e}")

# --- VIEW 2: PREDICTIVE PR INTELLIGENCE ---
elif st.session_state["smart_intelligence_mode"]:
    current_view = (
        url_area if is_area_direct_mode else st.session_state["pr_selected_view"]
    )

    if current_view is None:
        hero_pr_html = """
<div style="background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%); padding: 34px 28px; border-radius: 18px; border: 1.5px solid #334155; box-shadow: 0 12px 30px rgba(15, 23, 42, 0.25); text-align: center; margin-bottom: 25px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <div style="display: inline-block; background: rgba(245, 158, 11, 0.1); border: 1px solid rgba(245, 158, 11, 0.3); padding: 4px 14px; border-radius: 20px; color: #fbbf24; font-size: 11.5px; font-weight: 700; letter-spacing: 1px; text-transform: uppercase; margin-bottom: 10px;">
        📈 PREDICTIVE REQUISITION INTELLIGENCE
    </div>
    <h1 style="color: #ffffff !important; margin: 0; font-size: 30px; font-weight: 800;">
        Spares Consumption &amp; PR Schedulers
    </h1>
    <p style="color: #94a3b8 !important; margin-top: 8px; font-size: 14.5px;">
        Select an individual area or open the centralized <b>Combined Planning Cell</b> view.
    </p>
</div>
"""
        st.html(hero_pr_html)

        st.markdown(
            """
            <div style="background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); padding: 20px; border-radius: 12px; border: 2px solid #3b82f6; margin-bottom: 25px; text-align: center; box-shadow: 0 4px 12px rgba(59, 130, 246, 0.1);">
                <h3 style="margin: 0 0 5px 0; color: #1e3a8a; font-size: 20px; font-weight: 800;">🌐 Combined Areas (Plant-wide / Planning Cell View)</h3>
                <p style="margin: 0; color: #1e40af; font-size: 13px;">Merges identical material codes across all active areas for centralized bulk procurement and unified PR dates.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        if st.button("🚀 Open Combined Plant-wide PR View", use_container_width=True):
            st.session_state["pr_selected_view"] = "Combined"
            st.query_params["view"] = "pr"
            st.query_params["pr_area"] = "Combined"
            st.rerun()

        st.markdown(
            "<div style='margin: 20px 0; border-top: 1px solid #e2e8f0;'></div>",
            unsafe_allow_html=True,
        )
        st.markdown(
            "<h3 style='color: #0f172a; font-size: 18px; font-weight: 700;"
            " margin-bottom: 15px;'>🎛️ Or Select Individual Area Block:</h3>",
            unsafe_allow_html=True,
        )

        areas = list(AREA_CONFIGS.keys())
        for i in range(0, len(areas), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(areas):
                    area_name = areas[i + j]
                    cfg = AREA_CONFIGS[area_name]
                    accent_col = cfg.get("color", "#0284c7")
                    with cols[j]:
                        st.markdown(
                            f"""
                            <div style="background: #ffffff; padding: 18px; border-radius: 12px; border: 1px solid #e2e8f0; border-top: 3px solid {accent_col}; box-shadow: 0 4px 6px rgba(0,0,0,0.02); margin-bottom: 10px; text-align: center;">
                                <h4 style="margin: 0 0 4px 0; color: #0f172a; font-size: 16px; font-weight: 700;">📍 {area_name}</h4>
                                <span style="font-size: 11px; color: {accent_col}; font-weight: 700;">{cfg.get('zone_type', '')}</span>
                            </div>
                            """,
                            unsafe_allow_html=True,
                        )
                        if st.button(
                            f"Open {area_name}",
                            use_container_width=True,
                            key=f"pr_btn_{area_name}",
                        ):
                            st.session_state["pr_selected_view"] = area_name
                            st.query_params["view"] = "pr"
                            st.query_params["pr_area"] = area_name
                            st.rerun()
    else:
        if not is_area_direct_mode:
            if st.sidebar.button(
                "⬅️ Back to PR Area Selector", use_container_width=True
            ):
                st.session_state["pr_selected_view"] = None
                st.query_params["view"] = "pr"
                if "pr_area" in st.query_params:
                    del st.query_params["pr_area"]
                st.rerun()

        header_title = (
            "🌐 Combined Plant-wide PR Intelligence (Planning Cell)"
            if current_view == "Combined"
            else f"📍 Predictive PR Intelligence — {current_view}"
        )

        st.markdown(
            f"""
            <div style="background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%); padding: 25px; border-radius: 16px; border: 1px solid #cbd5e1; box-shadow: 0 10px 25px rgba(0,0,0,0.03); margin-bottom: 25px;">
                <h1 style="color: #0f172a !important; margin: 0; font-size: 24px; font-weight: 800;">{header_title}</h1>
                <p style="color: #475569 !important; margin-top: 6px; font-size: 13px;">Real-time consumption logs and lead-time-adjusted Purchase Requisition schedules.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        only_urgent_pr = st.session_state.get("urgent_pr_filter_state", False)

        target_configs = (
            AREA_CONFIGS
            if current_view == "Combined"
            else {current_view: AREA_CONFIGS[current_view]}
        )

        master_records = []
        now_dt = datetime.now()

        for area_key, area_cfg in target_configs.items():
            try:
                df_area = fetch_data(
                    area_cfg["sheet_url"], st.session_state["data_timestamp"]
                )
                df_area.columns = df_area.columns.str.strip()
                mapping = resolve_columns(df_area)

                consumption_map = build_consumption_map(
                    area_cfg.get("removal_url"),
                    st.session_state["data_timestamp"],
                    analysis_months,
                )

                for _, r in df_area.iterrows():
                    raw_mat = r.get(mapping["material"], "N/A")
                    mat_code = clean_material_code(raw_mat)
                    if mat_code == "N/A":
                        continue
                    store_stock = safe_int(r.get(mapping["store"], 0))
                    field_count = safe_int(r.get(mapping["field"], 0))

                    monthly_consumption, replacement_cycle, total_removals = (
                        consumption_map.get(str(mat_code), (0.0, 0.0, 0))
                    )

                    master_records.append({
                        "Area": area_key,
                        "Material Code": mat_code,
                        "Instrument Name": (
                            str(r.get(mapping["name"], "No Name")).strip()
                        ),
                        "Specs": str(r.get(mapping["specs"], "N/A")).strip(),
                        "Field Count": field_count,
                        "Store Stock": store_stock,
                        "Monthly Consumption": monthly_consumption,
                        "Replacement Cycle": replacement_cycle,
                        "Total Removals": total_removals,
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
                    combined_cycle = (
                        round(1.0 / combined_consumption, 1)
                        if combined_consumption > 0
                        else 0.0
                    )

                    grouped_records.append({
                        "Area": f"Plant-wide ({combined_area_tag})",
                        "Material Code": mat_code,
                        "Instrument Name": combined_name,
                        "Specs": combined_specs,
                        "Field Count": combined_field,
                        "Store Stock": combined_store,
                        "Monthly Consumption": combined_consumption,
                        "Replacement Cycle": combined_cycle,
                        "Total Removals": combined_removals,
                    })
                master_df = pd.DataFrame(grouped_records)

            pr_dates_str = []
            is_urgents = []

            for _, row in master_df.iterrows():
                m_cons = row["Monthly Consumption"]
                s_stock = row["Store Stock"]
                if m_cons > 0:
                    days_remaining = int((s_stock / m_cons) * 30)
                    exhaustion_date = now_dt + timedelta(days=days_remaining)
                    lead_time_days = lead_time_months * 30
                    pr_trigger_date = exhaustion_date - timedelta(days=lead_time_days)
                    urgent = pr_trigger_date <= now_dt
                    p_str = pr_trigger_date.strftime("%d %b %Y")
                else:
                    urgent = False
                    p_str = "No History / Stable"
                is_urgents.append(urgent)
                pr_dates_str.append(p_str)

            master_df["Is_Urgent"] = is_urgents
            master_df["PR_Date_Str"] = pr_dates_str

            master_df = master_df.sort_values(
                by="Instrument Name", key=lambda col: col.str.lower(), ascending=True
            ).reset_index(drop=True)

            if only_urgent_pr:
                master_df = master_df[master_df["Is_Urgent"] == True]

            sidebar_val = st.session_state.get("global_pr_search", "").strip()
            local_search = st.text_input(
                "🔍 Search (Enter Material Code or Instrument Description):", 
                value=sidebar_val
            ).strip()

            search_query = local_search or sidebar_val

            if search_query:
                filtered_df = master_df[
                    master_df["Material Code"].str.contains(
                        search_query, case=False, na=False
                    )
                    | master_df["Instrument Name"].str.contains(
                        search_query, case=False, na=False
                    )
                    | master_df["Specs"].str.contains(
                        search_query, case=False, na=False
                    )
                ]
            else:
                filtered_df = master_df

            if not filtered_df.empty:
                status_text = (
                    f"Showing {len(filtered_df)} Overdue PR Items"
                    if only_urgent_pr
                    else f"Analytics Results (items displayed - {len(filtered_df)})"
                )
                st.markdown(f"### {status_text}")

                date_box_title = (
                    "ESTIMATED STOCK RUNOUT DATE" 
                    if lead_time_months == 0 
                    else "RECOMMENDED PR DATE"
                )

                for _, item in filtered_df.iterrows():
                    is_urgent = item["Is_Urgent"]
                    pr_date_str = item["PR_Date_Str"]
                    store_stock = item["Store Stock"]

                    if is_urgent:
                        badge_text = (
                            "⚠️ ZERO STOCK WARNING" 
                            if lead_time_months == 0 
                            else " URGENT PR REQUIRED"
                        )
                        urgency_badge = (
                            f'<span style="background-color: #fee2e2; color: #dc2626; padding:'
                            f' 4px 10px; border-radius: 12px; font-weight: bold; font-size:'
                            f' 11px;">{badge_text}</span>'
                        )
                    else:
                        urgency_badge = (
                            '<span style="background-color: #dcfce7; color: #16a34a;'
                            ' padding: 4px 10px; border-radius: 12px; font-weight: bold;'
                            ' font-size: 11px;">✅ Stock Healthy</span>'
                        )

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
                            <div style="flex: 1.2; background: {'#fee2e2' if is_urgent else '#eff6ff'}; padding: 6px; border-radius: 6px; text-align: center; border: 1px solid {'#fca5a5' if is_urgent else '#bfdbfe'};">
                                <div style="font-size: 10px; color: {'#b91c1c' if is_urgent else '#1e40af'}; font-weight: bold;">{date_box_title}</div>
                                <div style="font-size: 14px; font-weight: 800; color: {'#991b1b' if is_urgent else '#1e3a8a'};">{pr_date_str}</div>
                            </div>
                        </div>
                    </div>
                    """
                    st.markdown(card_html, unsafe_allow_html=True)
            else:
                if only_urgent_pr:
                    st.success(
                        "🎉 Great news! No items have overdue PR dates in this view."
                    )
                else:
                    st.info("No matching material codes or instruments found.")
        else:
            st.warning("No inventory records available for this area.")

# --- VIEW 3: HOD MASTER LANDING PAGE (AREA TILES) ---
elif st.session_state["selected_area"] is None:
    if os.path.exists(NALCO_LOGO_PATH):
        top_c1, top_c2 = st.columns([1, 6], vertical_alignment="center")
        with top_c1:
            st.image(NALCO_LOGO_PATH, width=120)
        with top_c2:
            st.markdown(
                """
                <div style="margin-left: 5px;">
                    <h2 style="margin: 0; color: #0f172a; font-weight: 800; font-size: 26px;">NATIONAL ALUMINIUM COMPANY LIMITED</h2>
                    <p style="margin: 2px 0 0 0; color: #475569; font-size: 14px; font-weight: 600;">Instrumentation Spares &amp; Inventory Cell (C&amp;I)</p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<div style='margin-bottom: 25px;'></div>", unsafe_allow_html=True)

    areas = list(AREA_CONFIGS.keys())
    for i in range(0, len(areas), 3):
        cols = st.columns(3)
        for j in range(3):
            if i + j < len(areas):
                area_name = areas[i + j]
                cfg = AREA_CONFIGS[area_name]
                mgr = cfg.get("manager", "Plant Engineer")
                accent_color = cfg.get("color", "#0284c7")

                with cols[j]:
                    card_html = f"""
<div style="background: #ffffff; padding: 20px 20px 14px 20px; border-radius: 14px 14px 0 0; border: 1.5px solid #cbd5e1; border-bottom: none; box-shadow: 0 4px 12px rgba(0,0,0,0.03); text-align: center; border-top: 4px solid {accent_color}; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
    <h3 style="margin: 0 0 6px 0; color: #0f172a; font-size: 18px; font-weight: 800;">
        📍 {area_name}
    </h3>
    <div style="font-size: 11.5px; color: {accent_color}; font-weight: 700; margin-bottom: 8px;">
        {mgr}
    </div>
    <p style="color: #64748b; font-size: 12.5px; margin: 0; line-height: 1.4; min-height: 36px;">
        Live instrumentation spares
    </p>
</div>
"""
                    st.html(card_html)
                    if st.button(
                        f"Enter {area_name} ➔",
                        use_container_width=True,
                        key=f"btn_{area_name}",
                    ):
                        st.session_state["selected_area"] = area_name
                        st.rerun()
                    st.markdown(
                        "<div style='margin-bottom: 22px;'></div>", unsafe_allow_html=True
                    )

# --- VIEW 4: ACTIVE AREA DASHBOARD VIEW ---
else:
    current_area = st.session_state["selected_area"]
    config = AREA_CONFIGS[current_area]
    manager_name = config.get("manager", "Lead Officer")
    zone_name = config.get("zone_type", "Refinery Process Area")
    theme_accent = config.get("color", "#0284c7")

    if os.path.exists(NALCO_LOGO_PATH):
        h_col1, h_col2 = st.columns([1, 7], vertical_alignment="center")
        with h_col1:
            st.image(NALCO_LOGO_PATH, width=95)
        with h_col2:
            st.markdown(
                f"""
                <div>
                    <span style="background: {theme_accent}15; color: {theme_accent}; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 800; text-transform: uppercase;">
                        {zone_name}
                    </span>
                    <h2 style="color: #0f172a !important; margin: 3px 0 0 0; font-size: 24px; font-weight: 800;">
                        {config['title']}
                    </h2>
                    <p style="color: #475569 !important; margin: 2px 0 0 0; font-size: 13px; font-weight: 500;">
                        Live Spares Tracking Sheet &bull; Managed by <span style="color: {theme_accent}; font-weight: 700;">{manager_name} (Inventory Team, C&amp;I)</span>
                    </p>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<div style='margin-bottom: 15px;'></div>", unsafe_allow_html=True)
    else:
        area_header_html = f"""
        <div style="background: #ffffff; padding: 22px 26px; border-radius: 14px; border: 1.5px solid #cbd5e1; border-top: 5px solid {theme_accent}; box-shadow: 0 4px 15px rgba(0,0,0,0.04); font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 10px;">
                <div>
                    <span style="background: {theme_accent}15; color: {theme_accent}; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: 800; text-transform: uppercase; letter-spacing: 0.5px;">
                        {zone_name}
                    </span>
                    <h1 style="color: #0f172a !important; margin: 4px 0 0 0; font-size: 24px; font-weight: 800;">
                        {config['title']}
                    </h1>
                    <p style="color: #475569 !important; margin-top: 4px 0 0 0; font-size: 13px; font-weight: 500;">
                        Live Spares Tracking Sheet &bull; Managed by <span style="color: {theme_accent}; font-weight: 700;">{manager_name} (Inventory Team, C&amp;I)</span>
                    </p>
                </div>
                <div style="background: #f8fafc; border: 1px solid #e2e8f0; padding: 8px 16px; border-radius: 10px; text-align: right;">
                    <div style="font-size: 10.5px; color: #64748b; font-weight: 700; text-transform: uppercase;">ZONE STATUS</div>
                    <div style="font-size: 13.5px; font-weight: 800; color: #10b981;">● Active &amp; Synced</div>
                </div>
            </div>
        </div>
        """
        st.markdown(area_header_html, unsafe_allow_html=True)

    try:
        df = fetch_data(config["sheet_url"], st.session_state["data_timestamp"])
        df.columns = df.columns.str.strip()

        mapping = resolve_columns(df)
        NAME_COL = mapping["name"]
        STORE_COL = mapping["store"]

        df = df.dropna(subset=[NAME_COL])

        st.sidebar.markdown(
            '<div class="sidebar-section-title">🔍 Filter &amp; Search</div>',
            unsafe_allow_html=True,
        )
        all_instruments = ["All System Data"] + sorted(
            list(df[NAME_COL].dropna().unique()), key=lambda x: str(x).lower()
        )
        selected_instrument = st.sidebar.selectbox(
            "Select Instrument Category:", all_instruments
        )

        st.sidebar.markdown(
            "<div style='margin: 15px 0; border-top: 1.5px solid #cbd5e1;'></div>",
            unsafe_allow_html=True,
        )

        if selected_instrument != "All System Data":
            df = df[df[NAME_COL].str.strip() == selected_instrument]

        unique_names_ordered = sorted(
            df[NAME_COL].unique(), key=lambda x: str(x).lower()
        )

        # Single Continuous Feed: Renders all items on one page without pagination controls
        for current_name in unique_names_ordered:
            sub_df = df[
                df[NAME_COL].astype(str).str.strip() == str(current_name).strip()
            ]
            entry_count = len(sub_df)

            if entry_count == 1:
                row = sub_df.iloc[0]
                mapping["show_name"] = True
                render_row(row, mapping, current_area)
            else:
                total_current_store = sum(
                    safe_int(r[STORE_COL])
                    for _, r in sub_df.iterrows()
                    if STORE_COL in r
                )

                st.markdown(
                    f"""
                    <div style="background-color: #f1f5f9; border: 1px solid #cbd5e1; border-left: 4px solid {theme_accent}; padding: 12px 16px; border-radius: 8px; margin-bottom: -43px; position: relative; z-index: 99; pointer-events: none; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 4px rgba(0,0,0,0.02);">
                        <span style="font-size: 15px !important; font-weight: 700 !important; color: #0f172a !important; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                            📂 {current_name} — ({entry_count} Variants Grouped) | Combined Store Stock: {total_current_store}
                        </span>
                        <span style="font-size: 12px; color: #475569; font-weight: bold; margin-right: 5px;">▼</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                with st.expander(" "):
                    for idx, row in sub_df.iterrows():
                        mapping["show_name"] = False
                        render_row(row, mapping, current_area)

    except Exception as e:
        st.error(
            f"Error accessing Google Sheets Database for {current_area}: {e}"
        )

    st.sidebar.markdown(
        '<div class="sidebar-section-title">🔄 Database Control</div>',
        unsafe_allow_html=True,
    )
    if st.sidebar.button("🔄 Sync Live Data Now", use_container_width=True):
        st.cache_data.clear()
        st.session_state["data_timestamp"] = int(time.time())
        st.rerun()
