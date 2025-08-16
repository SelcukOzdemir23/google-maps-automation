
import streamlit as st
import pandas as pd
import urllib.parse
import os
import sys
import time
from wp_message_sender import send_whatsapp_message, is_valid_turkish_mobile

# Import scraper if available
try:
    from scraper import GoogleMapsScraper, save_to_csv
except ImportError:
    GoogleMapsScraper = None
    save_to_csv = None

st.set_page_config(page_title="Google Maps İşletme Kazıyıcı & WhatsApp Mesajlaşma", layout="wide")
st.title("Google Maps İşletme Kazıyıcı & WhatsApp Mesajlaşma")

st.markdown("""
Bu uygulama ile:
- İşletme CSV dosyalarını seçebilirsiniz
- Sonuçları görüntüleyip filtreleyebilirsiniz
- İşletmelere tek tıkla WhatsApp mesajı gönderebilirsiniz
- Google Maps'ten yeni veri kazıyabilirsiniz
""")

# Sidebar for WhatsApp controls
st.sidebar.header("📱 WhatsApp Ayarları")
user_phone = st.sidebar.text_input(
    "Telefon Numaranız (+90 ile başlayın):", 
    placeholder="+905551234567",
    help="WhatsApp mesajları göndermek için telefon numaranızı girin"
)

st.sidebar.markdown("---")
st.sidebar.header("✍️ Mesaj Ayarları")
message = st.sidebar.text_area(
    "Gönderilecek Mesaj:",
    placeholder="Merhaba! İşletmeniz için...",
    height=100,
    help="Tüm işletmelere gönderilecek mesajı yazın"
)

# Message sending delay
delay_seconds = st.sidebar.slider(
    "Mesajlar Arası Bekleme (saniye):",
    min_value=1,
    max_value=10,
    value=3,
    help="Toplu gönderimde mesajlar arasındaki bekleme süresi"
)

st.sidebar.markdown("---")
st.sidebar.header("🚀 Mesaj Gönder")

# Store current data in session state
if 'current_data' not in st.session_state:
    st.session_state.current_data = None

if st.session_state.current_data is not None and message and user_phone:
    df_current = st.session_state.current_data
    
    # Count valid numbers
    valid_phones = []
    if "phone" in df_current.columns:
        for idx, row in df_current.iterrows():
            phone = str(row["phone"]).replace(" ", "")
            if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                valid_phones.append({"name": row.get('name', 'İşletme'), "phone": phone, "idx": idx})
    
    if valid_phones:
        st.sidebar.success(f"📱 {len(valid_phones)} geçerli numara")
        
        if st.sidebar.button("🚀 Tümüne Gönder", type="primary", use_container_width=True):
            progress_bar = st.sidebar.progress(0)
            status_text = st.sidebar.empty()
            
            success_count = 0
            total_count = len(valid_phones)
            
            for i, item in enumerate(valid_phones):
                try:
                    status_text.text(f"Gönderiliyor: {item['name']}")
                    send_whatsapp_message(user_phone, item['phone'], message)
                    success_count += 1
                    progress_bar.progress((i + 1) / total_count)
                    if i < total_count - 1:  # Don't wait after last message
                        time.sleep(delay_seconds)
                except Exception as e:
                    st.sidebar.error(f"Hata: {item['name']} - {str(e)[:50]}...")
            
            status_text.text("Tamamlandı!")
            st.sidebar.success(f"✅ {success_count}/{total_count} mesaj gönderildi!")
        
        # Individual send buttons
        st.sidebar.markdown("**Tek tek gönder:**")
        for item in valid_phones[:5]:  # Show first 5
            if st.sidebar.button(f"📱 {item['name'][:20]}...", key=f"send_{item['idx']}"):
                try:
                    send_whatsapp_message(user_phone, item['phone'], message)
                    st.sidebar.success(f"✅ {item['name']} - Gönderildi!")
                except Exception as e:
                    st.sidebar.error(f"❌ Hata: {str(e)[:30]}...")
        
        if len(valid_phones) > 5:
            st.sidebar.info(f"... ve {len(valid_phones) - 5} numara daha")
    else:
        st.sidebar.warning("⚠️ Geçerli numara yok")
elif not user_phone:
    st.sidebar.warning("⚠️ Telefon numaranızı girin")
elif not message:
    st.sidebar.warning("⚠️ Mesajınızı yazın")
else:
    st.sidebar.info("📄 Önce veri seçin veya kazıyın")

tab1, tab2 = st.tabs(["CSV Seç", "Google Maps'ten Kazı"])

# --- Tab 1: Select CSV from directory ---
with tab1:
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    if csv_files:
        selected_csv = st.selectbox("Bir CSV dosyası seçin", csv_files)
        df = pd.read_csv(os.path.join(csv_dir, selected_csv))
        st.session_state.current_data = df  # Store in session state
        st.dataframe(df)
        # Show valid mobile numbers
        if "phone" in df.columns:
            valid_phones = []
            for idx, row in df.iterrows():
                phone = str(row["phone"]).replace(" ", "")
                if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                    valid_phones.append({"name": row.get('name', 'İşletme'), "phone": phone})
            
            if valid_phones:
                st.success(f"📱 {len(valid_phones)} geçerli cep telefonu numarası bulundu")
                
                # Show valid numbers in expandable section
                with st.expander(f"Geçerli Numaraları Gör ({len(valid_phones)} adet)"):
                    for item in valid_phones:
                        st.write(f"• {item['name']} - {item['phone']}")
            else:
                st.warning("⚠️ 05 ile başlayan geçerli cep telefonu numarası bulunamadı.")
        else:
            st.warning("CSV dosyasında 'phone' sütunu bulunamadı.")
    else:
        st.info("'csv_files' klasöründe CSV dosyası bulunamadı. Yeni veri kazıyın veya dosyaları bu klasöre ekleyin.")


# --- Tab 2: Scrape from Google Maps ---
with tab2:
    st.markdown("#### Google Maps'ten İşletme Bilgilerini Kazı")
    country = st.text_input("Ülke (örn: Turkey)", value="Turkey")
    query_type = st.text_input("Arama Türü (örn: restoran, otel)", value="restoran")
    max_results = st.number_input("Maksimum Sonuç", min_value=1, max_value=500, value=15)
    headless = st.checkbox("Tarayıcıyı gizli modda çalıştır", value=True)
    scrape_btn = st.button("Kazımaya Başla", type="primary")

    if scrape_btn:
        if not GoogleMapsScraper:
            st.error("Kazıyıcı modülü bulunamadı. scraper.py dosyasının aynı klasörde olduğundan emin olun.")
        else:
            with st.spinner("Kazıma işlemi devam ediyor. Lütfen bekleyin..."):
                try:
                    scraper = GoogleMapsScraper(headless=headless)
                    businesses = scraper.scrape_businesses(country, query_type, max_results)
                    if businesses:
                        df2 = pd.DataFrame(businesses)
                        st.session_state.current_data = df2  # Store in session state
                        st.success(f"{len(df2)} işletme kazındı.")
                        st.dataframe(df2)
                        # Show valid mobile numbers for scraped data
                        if "phone" in df2.columns:
                            valid_phones = []
                            for idx, row in df2.iterrows():
                                phone = str(row["phone"]).replace(" ", "")
                                if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                                    valid_phones.append({"name": row.get('name', 'İşletme'), "phone": phone})
                            
                            if valid_phones:
                                st.success(f"📱 {len(valid_phones)} geçerli cep telefonu numarası bulundu")
                                
                                # Show valid numbers in expandable section
                                with st.expander(f"Geçerli Numaraları Gör ({len(valid_phones)} adet)"):
                                    for item in valid_phones:
                                        st.write(f"• {item['name']} - {item['phone']}")
                            else:
                                st.warning("⚠️ 05 ile başlayan geçerli cep telefonu numarası bulunamadı.")
                        else:
                            st.warning("Sonuçlarda 'phone' sütunu bulunamadı.")
                        
                        # Option to download CSV and save to csv_files dir
                        csv = df2.to_csv(index=False).encode('utf-8')
                        st.download_button("Sonuçları CSV olarak indir", csv, f"{country.lower()}_{query_type}.csv", "text/csv")
                        # Save to csv_files directory
                        out_path = os.path.join(csv_dir, f"{country.lower()}_{query_type}.csv")
                        df2.to_csv(out_path, index=False)
                        st.info(f"Sonuçlar ayrıca {out_path} konumuna kaydedildi")
                    else:
                        st.warning("Hiçbir işletme kazınamadı.")
                except Exception as e:
                    st.error(f"Kazıma sırasında hata: {e}")
