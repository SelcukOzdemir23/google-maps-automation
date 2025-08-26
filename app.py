import streamlit as st
from components.sidebar import show_sidebar
from modules_csv_viewer import show_csv_viewer
from modules_csv_upload import show_csv_upload
from modules_messaging import show_messaging_page
from modules_scraper_page import show_scraper_page

# Page config
st.set_page_config(
    page_title="Google Maps Business Scraper & WhatsApp Messenger",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #1f4e79 0%, #2d5aa0 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
    }
    .feature-card {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #2d5aa0;
        margin: 0.5rem 0;
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    .stTabs [data-baseweb="tab"] {
        height: 3rem;
        padding: 0 1.5rem;
        background-color: #f0f2f6;
        border-radius: 8px 8px 0 0;
        color: #333 !important;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #2d5aa0 !important;
        color: white !important;
        font-weight: 600;
    }
    .stTabs [data-baseweb="tab"] p {
        color: inherit !important;
        margin: 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🗺️ Google Maps Business Scraper & WhatsApp Messenger</h1>
    <p>İşletme bilgilerini kazıyın ve WhatsApp ile iletişime geçin</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
show_sidebar()

# Main navigation
tab1, tab2, tab3, tab4 = st.tabs(["📊 CSV Görüntüleyici", "📤 CSV Yükle", "💬 Mesajlaşma", "🔍 Google Maps Kazıyıcı"])

with tab1:
    show_csv_viewer()

with tab2:
    show_csv_upload()

with tab3:
    show_messaging_page()

with tab4:
    show_scraper_page()