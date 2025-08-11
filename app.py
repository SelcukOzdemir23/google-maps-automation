
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

# Phone number input in sidebar
st.sidebar.header("WhatsApp Ayarları")
user_phone = st.sidebar.text_input(
    "Telefon Numaranız (+90 ile başlayın):", 
    placeholder="+905551234567",
    help="WhatsApp mesajları göndermek için telefon numaranızı girin"
)

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
        st.dataframe(df)
        st.markdown("### WhatsApp Mesajı Gönder")
        message = st.text_area("WhatsApp ile göndermek istediğiniz mesajı yazın:", key="wa_msg1")
        
        if message and user_phone:
            if "phone" in df.columns:
                send_col1, send_col2 = st.columns([1, 3])
                with send_col1:
                    if st.button("Tüm İşletmelere Gönder", type="primary"):
                        success_count = 0
                        for idx, row in df.iterrows():
                            phone = str(row["phone"]).replace(" ", "")
                            if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                                try:
                                    send_whatsapp_message(user_phone, phone, message)
                                    success_count += 1
                                    time.sleep(2)  # Wait between messages
                                except Exception as e:
                                    st.error(f"Hata: {e}")
                        st.success(f"{success_count} işletmeye mesaj gönderildi!")
                
                with send_col2:
                    st.markdown("**Veya tek tek gönder:**")
                    valid_count = 0
                    for idx, row in df.iterrows():
                        phone = str(row["phone"]).replace(" ", "")
                        if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                            wa_url = f"https://wa.me/+90{phone[1:]}?text={urllib.parse.quote(message)}"
                            st.markdown(f"📱 [{row.get('name', 'İşletme')} - {phone}]({wa_url})")
                            valid_count += 1
                    if valid_count == 0:
                        st.warning("05 ile başlayan geçerli cep telefonu numarası bulunamadı.")
            else:
                st.warning("CSV dosyasında 'phone' sütunu bulunamadı.")
        elif not user_phone:
            st.warning("Lütfen sol menüden telefon numaranızı girin.")
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
                        st.success(f"{len(df2)} işletme kazındı.")
                        st.dataframe(df2)
                        st.markdown("### WhatsApp Mesajı Gönder")
                        message2 = st.text_area("WhatsApp ile göndermek istediğiniz mesajı yazın:", key="wa_msg2")
                        
                        if message2 and user_phone:
                            if "phone" in df2.columns:
                                send_col1, send_col2 = st.columns([1, 3])
                                with send_col1:
                                    if st.button("Tüm İşletmelere Gönder", type="primary", key="send_all_2"):
                                        success_count = 0
                                        for idx, row in df2.iterrows():
                                            phone = str(row["phone"]).replace(" ", "")
                                            if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                                                try:
                                                    send_whatsapp_message(user_phone, phone, message2)
                                                    success_count += 1
                                                    time.sleep(2)  # Wait between messages
                                                except Exception as e:
                                                    st.error(f"Hata: {e}")
                                        st.success(f"{success_count} işletmeye mesaj gönderildi!")
                                
                                with send_col2:
                                    st.markdown("**Veya tek tek gönder:**")
                                    valid_count = 0
                                    for idx, row in df2.iterrows():
                                        phone = str(row["phone"]).replace(" ", "")
                                        if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                                            wa_url = f"https://wa.me/+90{phone[1:]}?text={urllib.parse.quote(message2)}"
                                            st.markdown(f"📱 [{row.get('name', 'İşletme')} - {phone}]({wa_url})")
                                            valid_count += 1
                                    if valid_count == 0:
                                        st.warning("05 ile başlayan geçerli cep telefonu numarası bulunamadı.")
                            else:
                                st.warning("Sonuçlarda 'phone' sütunu bulunamadı.")
                        elif not user_phone:
                            st.warning("Lütfen sol menüden telefon numaranızı girin.")
                        
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
