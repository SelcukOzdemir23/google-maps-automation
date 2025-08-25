import streamlit as st
import os

def show_sidebar():
    """Display the sidebar with navigation and info"""
    # Beautiful header
    st.sidebar.markdown("""
    <div style="text-align: center; padding: 1rem; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%); border-radius: 10px; margin-bottom: 2rem;">
        <h2 style="color: white; margin: 0;">🚀 Google Maps</h2>
        <h3 style="color: white; margin: 0;">İşletme Kazıyıcı</h3>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0; font-size: 0.9rem;">& WhatsApp Mesajlaşma</p>
    </div>
    """, unsafe_allow_html=True)

    # Collapsible features
    with st.sidebar.expander("🎯 Özellikler"):
        st.markdown("""
        ✅ **CSV Dosyaları** - İşletme verilerini görüntüle  
        ✅ **Google Maps Kazıma** - Yeni veriler topla  
        ✅ **WhatsApp Mesajlaşma** - Toplu mesaj gönder  
        ✅ **Türk Cep Telefonu** - 05 ile başlayan numaralar  
        """)

    st.sidebar.markdown("---")

    # Navigation
    st.sidebar.markdown("### 🧭 Navigasyon")
    page_options = {
        "📊 CSV Seç": "CSV Seç",
        "🔍 Google Maps Kazı": "Google Maps Kazı", 
        "📱 Mesaj Gönder": "Mesaj Gönder"
    }

    # Initialize session state
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "CSV Seç"

    selected_page = st.sidebar.radio(
        "Sayfa Seçin:",
        list(page_options.keys()),
        index=list(page_options.values()).index(st.session_state.current_page)
    )

    st.session_state.current_page = page_options[selected_page]

    # CSV files info
    _show_csv_info()
    
    return st.session_state.current_page

def _show_csv_info():
    """Show CSV files information in sidebar"""
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]

    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📁 CSV Dosyaları")
    
    if csv_files:
        st.sidebar.success(f"📋 {len(csv_files)} CSV dosyası mevcut")
        for csv_file in csv_files[:3]:  # Show first 3
            st.sidebar.write(f"• {csv_file}")
        if len(csv_files) > 3:
            st.sidebar.write(f"... ve {len(csv_files) - 3} dosya daha")
    else:
        st.sidebar.info("📄 Henüz CSV dosyası yok")