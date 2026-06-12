import streamlit as st
import pandas as pd
import time
from datetime import datetime

# 1. Page Configuration
st.set_page_config(page_title="Plant Instrumentation Inventory", layout="wide", page_icon="🏭")

# Helper function to render rows using fallback display wrapper
def render_row(row, NAME_COL, SPECS_COL, FIELD_COL, SPARES_M7_COL, SPARES_SHOP_COL, TOTAL_SPARES_COL, show_name=True):
    inst_name = str(row[NAME_COL]).strip()
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
        <div style="display: flex; flex-wrap: wrap; align-items: center; gap: 15px; font-family: sans-serif;">
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
    """
    st.components.v1.html(card_html, height=110, scrolling=False)

# --- FIXED LOGIC: Injection directly through safe config placeholders ---
def inject_custom_css():
    css = """
    <style>
    .stApp {
        background-color: #f8fafc; 
    }
    h1, h2, h3 {
        color: #1e293b !important; 
        font-family: sans-serif; 
    }
    .inventory-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);
        border: 1px solid #e2e8f0;
        margin-bottom: 15px;
    }
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
        color: #64748b; 
        margin-bottom: 4px;
    }
    .status-badge {
        display: inline-block; 
        padding: 6px 12px; 
        border-radius: 20px; 
        font-size: 13px;
        font-weight: 600; 
        text
