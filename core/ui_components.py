# -*- coding: utf-8 -*-
"""
UI Components and styling for ABAP Documentation Generator.
Centralizes SVG icons and custom CSS styles to modernize the application.
"""

import streamlit as st

# Custom SVG Icons (Personalized, sharp line-art style)
ICONS = {
    "forms": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #38bdf8;"><path d="m18 16 4-4-4-4"/><path d="m6 8-4 4 4 4"/><path d="m14.5 4-5 16"/></svg>""",
    "performs": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #a855f7;"><circle cx="18" cy="18" r="3"/><circle cx="6" cy="6" r="3"/><path d="M13 6h3a2 2 0 0 1 2 2v7"/><path d="M6 9v12"/></svg>""",
    "selects": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #22c55e;"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5V19A9 3 0 0 0 21 19V5"/><path d="M3 12A9 3 0 0 0 21 12"/></svg>""",
    "functions": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #f59e0b;"><rect x="4" y="4" width="16" height="16" rx="2"/><rect x="9" y="9" width="6" height="6" rx="1"/><path d="M9 1v3"/><path d="M15 1v3"/><path d="M9 20v3"/><path d="M15 20v3"/><path d="M20 9h3"/><path d="M20 15h3"/><path d="M1 9h3"/><path d="M1 15h3"/></svg>""",
    "sap_tables": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #ec4899;"><path d="M9 3H5a2 2 0 0 0-2 2v4h6V3z"/><path d="M9 21v-8H3v6a2 2 0 0 0 2 2h4z"/><path d="M21 9V5a2 2 0 0 0-2-2h-8v6h10z"/><path d="M21 13H11v8h8a2 2 0 0 0 2-2v-6z"/></svg>""",
    "internal_tables": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #06b6d4;"><path d="m12 3-10 5 10 5 10-5-10-5Z"/><path d="m2 17 10 5 10-5"/><path d="m2 12 10 5 10-5"/></svg>""",
    "classes": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #6366f1;"><path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/><polyline points="3.27 6.96 12 12.01 20.73 6.96"/><line x1="12" y1="22.08" x2="12" y2="12"/></svg>""",
    "methods": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #84cc16;"><polyline points="4 17 10 11 4 5"/><line x1="12" y1="19" x2="20" y2="19"/></svg>""",
    "set_handlers": """<svg xmlns="http://www.w3.org/2000/svg" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color: #e11d48;"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>""",
    "status_ok": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#22c55e" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><polyline points="22 4 12 14.01 9 11.01"/></svg>""",
    "status_warn": """<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="vertical-align: middle; margin-right: 6px;"><path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>""",
    "doc": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 19.5v-15A2.5 2.5 0 0 1 6.5 2H20v20H6.5a2.5 2.5 0 0 1-2.5-2.5Z"/><path d="M6 6h10"/><path d="M6 10h10"/><path d="M8 14h8"/></svg>""",
    "chat": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>""",
    "code": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg>""",
    "search": """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>"""
}

# Injected CSS stylesheet
CSS_STYLES = """
<style>
/* Load modern fonts */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

/* Apply font to Streamlit app container */
html, body, [data-testid="stAppViewContainer"], [data-testid="stHeader"], .st-emotion-cache-183lysc, .st-emotion-cache-16idsys, [class*="st-key-"] {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif !important;
}

/* Page background */
[data-testid="stAppViewContainer"] {
    background-color: #F8FAFC !important;
}

/* Modernized glassmorphic sidebar */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
    color: #F8FAFC !important;
    border-right: 1px solid rgba(255, 255, 255, 0.05);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255, 255, 255, 0.1) !important;
}

[data-testid="stSidebar"] .stMarkdown p, [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
    color: #F8FAFC !important;
}

/* Tab modern style */
div[data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 2px solid #E2E8F0 !important;
    gap: 8px !important;
    padding: 0.5rem 0 !important;
}

button[data-baseweb="tab"] {
    font-size: 1rem !important;
    font-weight: 600 !important;
    color: #64748B !important;
    border: none !important;
    border-radius: 8px !important;
    padding: 8px 16px !important;
    background-color: transparent !important;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

button[data-baseweb="tab"]:hover {
    color: #0F4C81 !important;
    background-color: #EEF2F6 !important;
}

button[data-baseweb="tab"][aria-selected="true"] {
    color: #FFFFFF !important;
    background: linear-gradient(135deg, #0F4C81 0%, #1D70B8 100%) !important;
    box-shadow: 0 4px 12px rgba(15, 76, 129, 0.2) !important;
}

/* Beautiful KPI Metric Cards layout */
.kpi-container {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
    gap: 16px;
    margin: 1.5rem 0;
}

.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 1.25rem;
    display: flex;
    align-items: center;
    gap: 16px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.kpi-card:hover {
    transform: translateY(-4px);
    border-color: #0F4C81;
    box-shadow: 0 10px 15px -3px rgba(15, 76, 129, 0.1), 0 4px 6px -4px rgba(15, 76, 129, 0.05);
}

.kpi-icon-wrapper {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    background: #F1F5F9;
    display: flex;
    align-items: center;
    justify-content: center;
    transition: all 0.3s ease;
}

.kpi-card:hover .kpi-icon-wrapper {
    background: #EEF2F6;
    transform: scale(1.05);
}

.kpi-info {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.kpi-label {
    font-size: 0.85rem;
    font-weight: 500;
    color: #64748B;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.kpi-value {
    font-size: 1.8rem;
    font-weight: 700;
    color: #0F172A;
    line-height: 1.2;
}

.kpi-detail {
    font-size: 0.8rem;
    color: #94A3B8;
}

/* File Uploader override styles */
[data-testid="stFileUploader"] {
    background-color: #FFFFFF !important;
    border: 2px dashed #CBD5E1 !important;
    border-radius: 16px !important;
    padding: 1.5rem !important;
    transition: all 0.3s ease !important;
}

[data-testid="stFileUploader"]:hover {
    border-color: #0F4C81 !important;
    background-color: #F8FAFC !important;
    box-shadow: 0 4px 12px rgba(15, 76, 129, 0.05) !important;
}

/* Custom styled buttons */
.stButton>button {
    background: linear-gradient(135deg, #0F4C81 0%, #1D70B8 100%) !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 12px 24px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    box-shadow: 0 4px 12px rgba(15, 76, 129, 0.2) !important;
    transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
}

.stButton>button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 16px rgba(15, 76, 129, 0.3) !important;
    filter: brightness(1.1) !important;
}

.stButton>button:active {
    transform: translateY(0px) !important;
}

/* Welcome Page Card Styling */
.welcome-container {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 20px;
    padding: 3rem 2rem;
    text-align: center;
    box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.05);
    margin: 2rem auto;
    max-width: 800px;
}

.welcome-logo {
    display: inline-block;
    padding: 10px;
    border-radius: 24px;
    background: linear-gradient(135deg, #F1F5F9 0%, #EEF2F6 100%);
    box-shadow: 0 8px 16px rgba(0,0,0,0.03);
    margin-bottom: 1.5rem;
    border: 1px solid #E2E8F0;
}

.welcome-logo img {
    border-radius: 16px;
}

.welcome-title {
    color: #0F172A;
    font-weight: 800;
    font-size: 2.25rem;
    margin-bottom: 0.75rem;
    background: linear-gradient(135deg, #0F4C81 0%, #1D70B8 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

.welcome-subtitle {
    font-size: 1.1rem;
    color: #64748B;
    max-width: 500px;
    margin: 0 auto 2.5rem auto;
    line-height: 1.6;
}

.features-grid {
    display: grid;
    grid-template-columns: repeat(2, 1fr);
    gap: 20px;
    margin-bottom: 2.5rem;
    text-align: left;
}

.feature-box {
    background: #F8FAFC;
    border: 1px solid #F1F5F9;
    border-radius: 14px;
    padding: 1.25rem;
    display: flex;
    gap: 16px;
    transition: all 0.2s ease;
}

.feature-box:hover {
    background: #F1F5F9;
    transform: translateY(-2px);
}

.feature-icon-wrapper {
    background: #0F4C81;
    color: #FFFFFF;
    width: 40px;
    height: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}

.feature-title {
    font-weight: 600;
    color: #1E293B;
    margin-bottom: 4px;
    font-size: 0.95rem;
}

.feature-desc {
    font-size: 0.85rem;
    color: #64748B;
    line-height: 1.4;
}

/* Chat bubble styling overrides */
[data-testid="stChatMessage"] {
    background-color: #FFFFFF !important;
    border: 1px solid #E2E8F0 !important;
    border-radius: 16px !important;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02) !important;
    margin-bottom: 1rem !important;
    padding: 1rem !important;
    transition: transform 0.2s ease !important;
}

[data-testid="stChatMessage"]:hover {
    transform: translateX(2px);
}

[data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"], [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
    background-color: #0F4C81 !important;
}

/* Hide Streamlit default hamburger menu and footer for cleaner view */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header {background-color: transparent !important;}
</style>
"""

def inject_styles():
    """Injects the custom CSS style rules into the Streamlit session."""
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

def render_metric_card(label, value, detail, icon_name):
    """
    Renders a custom HTML KPI metric card with personalized SVG icon.
    """
    icon_svg = ICONS.get(icon_name, "")
    card_html = (
        f'<div class="kpi-card">'
        f'<div class="kpi-icon-wrapper">{icon_svg}</div>'
        f'<div class="kpi-info">'
        f'<span class="kpi-label">{label}</span>'
        f'<span class="kpi-value">{value}</span>'
        f'<span class="kpi-detail">{detail}</span>'
        f'</div>'
        f'</div>'
    )
    return card_html

def render_kpi_grid(cards_data):
    """
    Renders a grid container populated with metric cards.
    cards_data should be a list of dicts: [{'label':..., 'value':..., 'detail':..., 'icon':...}]
    """
    grid_html = '<div class="kpi-container">'
    for card in cards_data:
        grid_html += render_metric_card(card['label'], card['value'], card['detail'], card['icon'])
    grid_html += '</div>'
    return grid_html
