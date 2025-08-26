import streamlit as st
import pandas as pd
import os
from wp_message_sender import is_valid_turkish_mobile

def show_scraper_page():
    """Google Maps scraping page"""
    try:
        from scraper import GoogleMapsScraper
    except ImportError:
        GoogleMapsScraper = None
    
    st.markdown("#### Google Maps'ten İşletme Bilgilerini Kazı")
    
    # Language and location selection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Konum Ayarları**")
        language = st.selectbox(
            "Arama Dili:",
            ["Türkçe", "English"],
            help="Arama yapılacak dil"
        )
        
        if language == "Türkçe":
            country_options = {
                "Türkiye": {"search": "Türkiye", "english": "Turkey"},
                "Almanya": {"search": "Almanya", "english": "Germany"}, 
                "Fransa": {"search": "Fransa", "english": "France"},
                "İngiltere": {"search": "İngiltere", "english": "United Kingdom"},
                "ABD": {"search": "Amerika", "english": "United States"}
            }
        else:
            country_options = {
                "Turkey": {"search": "Turkey", "english": "Turkey"},
                "Germany": {"search": "Germany", "english": "Germany"},
                "France": {"search": "France", "english": "France"}, 
                "United Kingdom": {"search": "United Kingdom", "english": "United Kingdom"},
                "United States": {"search": "United States", "english": "United States"}
            }
        
        selected_country_display = st.selectbox("Ülke:", list(country_options.keys()))
        country_search = country_options[selected_country_display]["search"]
        country_english = country_options[selected_country_display]["english"]
    
    with col2:
        st.markdown("**Arama Ayarları**")
        
        if language == "Türkçe":
            business_types = {
                "Özel Arama": "custom",
                "Restoran": "restoran",
                "Kafe": "kafe", 
                "Otel": "otel",
                "Market": "market",
                "Eczane": "eczane",
                "Kuaför": "kuaför",
                "Spor Salonu": "spor salonu"
            }
        else:
            business_types = {
                "Custom Search": "custom",
                "Restaurant": "restaurant",
                "Cafe": "cafe",
                "Hotel": "hotel", 
                "Store": "store",
                "Pharmacy": "pharmacy",
                "Hair Salon": "hair salon",
                "Gym": "gym"
            }
        
        selected_type = st.selectbox("İşletme Türü:", list(business_types.keys()))
        
        if business_types[selected_type] == "custom":
            custom_col1, custom_col2 = st.columns([3, 1])
            with custom_col1:
                query_type = st.text_input("Özel Arama Terimi:", placeholder="Örn: pizza, berber, oto tamiri")
            with custom_col2:
                st.markdown("<br>", unsafe_allow_html=True)  # Add spacing
                if st.button("💾 Kaydet", help="Özel arama terimini kaydet"):
                    if query_type:
                        _save_custom_search(query_type, language)
                        st.success(f"✅ '{query_type}' kaydedildi!")
                    else:
                        st.warning("⚠️ Önce arama terimi girin")
        else:
            query_type = business_types[selected_type]
    
    # Additional settings
    st.markdown("---")
    col3, col4 = st.columns([1, 1])
    
    with col3:
        max_results = st.number_input("Maksimum Sonuç", min_value=1, max_value=500, value=15)
    
    with col4:
        headless = st.checkbox("Tarayıcıyı gizli modda çalıştır", value=True)
    
    # Search query preview
    if language == "English":
        search_query = f"{query_type} in {country_search}"
    else:
        search_query = f"{query_type} {country_search}"
    
    st.info(f"🔍 Arama sorgusu: **{search_query}**")
    
    # Show saved custom searches if any exist
    _show_saved_searches(language)
    
    scrape_btn = st.button("Kazımaya Başla", type="primary", use_container_width=True)

    if scrape_btn:
        if not GoogleMapsScraper:
            st.error("Kazıyıcı modülü bulunamadı. scraper.py dosyasının aynı klasörde olduğundan emin olun.")
        else:
            _run_scraping(GoogleMapsScraper, country_english, query_type, max_results, headless, search_query)

def _run_scraping(GoogleMapsScraper, country, query_type, max_results, headless, search_query):
    """Run the scraping process with logging"""
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    
    # Create containers for progress and logs
    progress_container = st.container()
    log_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        business_progress = st.empty()
    
    with log_container:
        st.markdown("### 📄 Kazıma Süreci Logları")
        log_area = st.empty()
        logs = []
    
    try:
        import datetime
        
        # Initialize logs
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"{current_time} - INFO - Kazıyıcı başlatılıyor...")
        logs.append(f"{current_time} - INFO - Hedef: {country} - {query_type}")
        logs.append(f"{current_time} - INFO - Maksimum sonuç: {max_results}")
        logs.append(f"{current_time} - INFO - Tarayıcı modu: {'Gizli' if headless else 'Görünür'}")
        log_area.text_area("Loglar:", "\n".join(logs), height=300)
        
        status_text.text("🚀 Kazıyıcı başlatılıyor...")
        progress_bar.progress(10)
        
        scraper = GoogleMapsScraper(headless=headless)
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"{current_time} - INFO - Tarayıcı başlatıldı")
        log_area.text_area("Loglar:", "\n".join(logs), height=300)
        
        status_text.text("🔍 Arama yapılıyor...")
        progress_bar.progress(30)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"{current_time} - INFO - Google Maps'te arama: {search_query}")
        log_area.text_area("Loglar:", "\n".join(logs), height=300)
        
        # Capture scraper logs and run scraping
        businesses = _scrape_with_log_capture(scraper, country, query_type, max_results, logs, log_area, business_progress, progress_bar)
        
        status_text.text("📋 Veriler işleniyor...")
        progress_bar.progress(90)
        
        if businesses:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logs.append(f"{current_time} - INFO - Toplam {len(businesses)} işletme kazındı")
            logs.append(f"{current_time} - INFO - DataFrame oluşturuluyor...")
            log_area.text_area("Loglar:", "\n".join(logs), height=300)
            
            df2 = pd.DataFrame(businesses)
            
            progress_bar.progress(100)
            status_text.text("✅ Kazıma tamamlandı!")
            
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logs.append(f"{current_time} - INFO - Kazıma başarıyla tamamlandı!")
            log_area.text_area("Loglar:", "\n".join(logs), height=300)
            
            st.success(f"{len(df2)} işletme kazındı.")
            st.dataframe(df2)
            
            _show_valid_numbers(df2)
            _save_csv_file(df2, country, query_type, csv_dir, logs, log_area)
        else:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            logs.append(f"{current_time} - WARNING - Hiçbir işletme bulunamadı")
            log_area.text_area("Loglar:", "\n".join(logs), height=300)
            st.warning("Hiçbir işletme kazınamadı.")
    except Exception as e:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"{current_time} - ERROR - {str(e)}")
        log_area.text_area("Loglar:", "\n".join(logs), height=300)
        st.error(f"Kazıma sırasında hata: {e}")

def _scrape_with_log_capture(scraper, country, query_type, max_results, logs, log_area, business_progress, progress_bar):
    """Scrape businesses and capture real-time logs"""
    import datetime
    import logging
    import io
    import sys
    import threading
    import time
    
    businesses = []
    
    try:
        # Create a custom log handler to capture scraper logs
        log_capture = io.StringIO()
        handler = logging.StreamHandler(log_capture)
        handler.setLevel(logging.INFO)
        
        # Get the scraper's logger
        scraper_logger = logging.getLogger()
        scraper_logger.addHandler(handler)
        scraper_logger.setLevel(logging.INFO)
        
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"{current_time} - INFO - İşletme arama başlatılıyor...")
        log_area.text_area("Loglar:", "\n".join(logs), height=300)
        
        # Start scraping in a separate thread to capture logs
        def scrape_worker():
            nonlocal businesses
            businesses = scraper.scrape_businesses(country, query_type, max_results)
        
        scrape_thread = threading.Thread(target=scrape_worker)
        scrape_thread.start()
        
        # Monitor logs while scraping
        last_log_pos = 0
        business_count = 0
        
        while scrape_thread.is_alive():
            # Get new log content
            log_content = log_capture.getvalue()
            if len(log_content) > last_log_pos:
                new_logs = log_content[last_log_pos:].strip()
                if new_logs:
                    # Process new log lines
                    for line in new_logs.split('\n'):
                        if line.strip():
                            logs.append(line.strip())
                            
                            # Check if this is a business scraping log
                            if "Scraped" in line and "/" in line:
                                try:
                                    # Extract business count from log
                                    parts = line.split("Scraped ")[1]
                                    current_business = int(parts.split("/")[0])
                                    total_business = int(parts.split("/")[1].split(":")[0])
                                    business_name = parts.split(": ")[1] if ": " in parts else "Unknown"
                                    
                                    # Update progress
                                    progress = 30 + (current_business / total_business) * 50
                                    progress_bar.progress(int(progress))
                                    business_progress.text(f"🏢 {current_business}/{total_business}: {business_name}")
                                    business_count = current_business
                                except:
                                    pass
                    
                    # Update log display
                    log_area.text_area("Loglar:", "\n".join(logs[-50:]), height=300)  # Show last 50 lines
                    last_log_pos = len(log_content)
            
            time.sleep(0.5)  # Check for new logs every 0.5 seconds
        
        # Wait for thread to complete
        scrape_thread.join()
        
        # Get any remaining logs
        final_log_content = log_capture.getvalue()
        if len(final_log_content) > last_log_pos:
            new_logs = final_log_content[last_log_pos:].strip()
            if new_logs:
                for line in new_logs.split('\n'):
                    if line.strip():
                        logs.append(line.strip())
        
        # Clean up
        scraper_logger.removeHandler(handler)
        handler.close()
        
        return businesses
        
    except Exception as e:
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        logs.append(f"{current_time} - ERROR - Scraping error: {str(e)}")
        log_area.text_area("Loglar:", "\n".join(logs), height=300)
        return businesses

def _save_custom_search(search_term, language):
    """Save custom search term to file"""
    import os
    import json
    
    # Create custom_searches directory if it doesn't exist
    custom_dir = os.path.join(os.getcwd(), "custom_searches")
    if not os.path.exists(custom_dir):
        os.makedirs(custom_dir)
    
    # Load existing custom searches
    file_path = os.path.join(custom_dir, "saved_searches.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_searches = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        saved_searches = {"turkish": [], "english": []}
    
    # Add new search term if not already exists
    lang_key = "turkish" if language == "Türkçe" else "english"
    if search_term not in saved_searches[lang_key]:
        saved_searches[lang_key].append(search_term)
        
        # Save back to file
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(saved_searches, f, ensure_ascii=False, indent=2)

def _show_saved_searches(language):
    """Show saved custom searches"""
    import os
    import json
    
    file_path = os.path.join(os.getcwd(), "custom_searches", "saved_searches.json")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            saved_searches = json.load(f)
        
        lang_key = "turkish" if language == "Türkçe" else "english"
        if saved_searches.get(lang_key):
            with st.expander(f"💾 Kaydedilmiş Özel Aramalar ({len(saved_searches[lang_key])} adet)"):
                for term in saved_searches[lang_key]:
                    st.write(f"• {term}")
    except (FileNotFoundError, json.JSONDecodeError):
        pass

def _show_valid_numbers(df):
    """Show valid mobile numbers from scraped data"""
    if "phone" in df.columns:
        valid_phones = []
        for idx, row in df.iterrows():
            phone = str(row["phone"]).replace(" ", "")
            if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                valid_phones.append({"name": row.get('name', 'İşletme'), "phone": phone})
        
        if valid_phones:
            st.success(f"📱 {len(valid_phones)} geçerli cep telefonu numarası bulundu")
            st.info("💡 Mesaj göndermek için 'Mesaj Gönder' sekmesine geçin")
            
            with st.expander(f"Geçerli Numaraları Gör ({len(valid_phones)} adet)"):
                for item in valid_phones:
                    st.write(f"• {item['name']} - {item['phone']}")
        else:
            st.warning("⚠️ 05 ile başlayan geçerli cep telefonu numarası bulunamadı.")
    else:
        st.warning("Sonuçlarda 'phone' sütunu bulunamadı.")

def _save_csv_file(df, country, query_type, csv_dir, logs, log_area):
    """Save scraped data to CSV file"""
    # Option to download CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("Sonuçları CSV olarak indir", csv, f"{country.lower()}_{query_type}.csv", "text/csv")
    
    # Save to csv_files directory
    logs.append("💾 CSV dosyası kaydediliyor...")
    log_area.text_area("Loglar:", "\n".join(logs), height=200)
    
    out_path = os.path.join(csv_dir, f"{country.lower()}_{query_type}.csv")
    df.to_csv(out_path, index=False)
    
    logs.append(f"✅ CSV kaydedildi: {out_path}")
    log_area.text_area("Loglar:", "\n".join(logs), height=200)
    
    st.info(f"Sonuçlar ayrıca {out_path} konumuna kaydedildi")
    
    # Auto-refresh messaging page cache
    if 'messaging_step' in st.session_state:
        st.session_state.messaging_step = 1
    if 'selected_csv' in st.session_state:
        st.session_state.selected_csv = None
    
    # Show quick navigation to messaging
    st.success("🚀 CSV kaydedildi! Mesaj göndermek için 'Mesajlaşma' sekmesine geçin.")
    st.balloons()