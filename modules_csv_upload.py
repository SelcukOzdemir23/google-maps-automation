import streamlit as st
import pandas as pd
import os
from wp_message_sender import is_valid_turkish_mobile

def show_csv_upload():
    """CSV upload page"""
    # Header
    st.markdown("""
    <div style="background: linear-gradient(90deg, #28a745 0%, #20c997 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
        <h2 style="color: white; margin: 0; font-size: 2rem;">📤 CSV Dosyası Yükle</h2>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0; font-size: 1.1rem;">Kendi CSV dosyanızı yükleyin ve mesaj gönderin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Instructions
    with st.expander("📋 CSV Formatı Hakkında", expanded=True):
        st.markdown("""
        **Gerekli Sütunlar:**
        - `name` - İşletme/Kişi adı
        - `phone` - Telefon numarası (05XXXXXXXXX formatında)
        
        **İsteğe Bağlı Sütunlar:**
        - `address` - Adres bilgisi
        - `category` - Kategori
        - `website` - Web sitesi
        
        **Örnek CSV İçeriği:**
        ```
        name,phone,address,category
        Ahmet's Cafe,05551234567,Antalya Merkez,Kafe
        Mehmet Restaurant,05559876543,İstanbul Kadıköy,Restoran
        ```
        """)
    
    # File upload
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "CSV dosyanızı seçin:",
            type=['csv'],
            help="Sadece .csv formatındaki dosyalar kabul edilir"
        )
        
        if uploaded_file is not None:
            try:
                # Read CSV
                df = pd.read_csv(uploaded_file)
                
                # Validate required columns
                required_columns = ['name', 'phone']
                missing_columns = [col for col in required_columns if col not in df.columns]
                
                if missing_columns:
                    st.error(f"❌ Eksik sütunlar: {', '.join(missing_columns)}")
                    st.info("CSV dosyanızda 'name' ve 'phone' sütunları bulunmalıdır.")
                    return
                
                # Show preview
                st.success(f"✅ CSV başarıyla yüklendi! ({len(df)} kayıt)")
                
                # Validate phone numbers
                valid_phones = _get_valid_phones(df)
                invalid_count = len(df) - len(valid_phones)
                
                if valid_phones:
                    st.info(f"📱 {len(valid_phones)} geçerli numara | ❌ {invalid_count} geçersiz numara")
                else:
                    st.warning("⚠️ Hiçbir geçerli Türk cep telefonu numarası bulunamadı!")
                    st.info("Numaralar 05XXXXXXXXX formatında olmalıdır.")
                
                # Preview data
                with st.expander("🔍 Veri Önizlemesi", expanded=True):
                    st.dataframe(df.head(10), use_container_width=True)
                
                # Save option
                if valid_phones:
                    _show_save_options(df, uploaded_file.name, valid_phones)
                
            except Exception as e:
                st.error(f"❌ CSV okuma hatası: {str(e)}")
                st.info("Dosyanızın UTF-8 kodlamasında ve doğru CSV formatında olduğundan emin olun.")
    
    with col2:
        # Sample CSV download
        st.markdown("### 📥 Örnek CSV İndir")
        sample_data = {
            'name': ['Ahmet Cafe', 'Mehmet Restaurant', 'Ayşe Kuaför'],
            'phone': ['05551234567', '05559876543', '05557654321'],
            'address': ['Antalya Merkez', 'İstanbul Kadıköy', 'Ankara Çankaya'],
            'category': ['Kafe', 'Restoran', 'Kuaför']
        }
        sample_df = pd.DataFrame(sample_data)
        csv_sample = sample_df.to_csv(index=False).encode('utf-8')
        
        st.download_button(
            "📄 Örnek CSV İndir",
            csv_sample,
            "ornek_csv.csv",
            "text/csv",
            use_container_width=True,
            help="Bu örnek dosyayı indirip kendi verilerinizle doldurun"
        )
        
        # Tips
        st.markdown("### 💡 İpuçları")
        st.markdown("""
        - Excel'den CSV olarak kaydedin
        - Türkçe karakterler için UTF-8 kullanın
        - Telefon numaraları 05 ile başlamalı
        - Virgül ayırıcı kullanın
        """)

def _get_valid_phones(df):
    """Extract valid phone numbers from dataframe"""
    valid_phones = []
    seen_phones = set()
    
    if "phone" in df.columns:
        for idx, row in df.iterrows():
            phone = str(row["phone"]).replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
            if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                if phone not in seen_phones:
                    valid_phones.append({
                        "name": row.get('name', 'İşletme'), 
                        "phone": phone, 
                        "idx": idx,
                        "address": row.get('address', ''),
                        "category": row.get('category', '')
                    })
                    seen_phones.add(phone)
    return valid_phones

def _show_save_options(df, filename, valid_phones):
    """Show options to save the uploaded CSV"""
    st.markdown("---")
    st.markdown("### 💾 Dosyayı Kaydet")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Clean filename
        clean_filename = filename.replace('.csv', '')
        new_filename = st.text_input(
            "Dosya adı:",
            value=clean_filename,
            help="Dosya csv_files klasörüne kaydedilecek"
        )
        
        if st.button("💾 CSV Dosyasını Kaydet", type="primary", use_container_width=True):
            if new_filename:
                _save_csv_file(df, new_filename, valid_phones)
            else:
                st.error("Lütfen bir dosya adı girin!")
    
    with col2:
        st.markdown("**📊 Özet:**")
        st.metric("Toplam Kayıt", len(df))
        st.metric("Geçerli Numara", len(valid_phones))
        st.metric("Sütun Sayısı", len(df.columns))

def _save_csv_file(df, filename, valid_phones):
    """Save CSV file to csv_files directory"""
    try:
        # Ensure csv_files directory exists
        csv_dir = os.path.join(os.getcwd(), "csv_files")
        if not os.path.exists(csv_dir):
            os.makedirs(csv_dir)
        
        # Clean filename and add .csv extension
        clean_filename = filename.replace('.csv', '') + '.csv'
        file_path = os.path.join(csv_dir, clean_filename)
        
        # Save the file
        df.to_csv(file_path, index=False, encoding='utf-8')
        
        st.success(f"✅ Dosya başarıyla kaydedildi: `{clean_filename}`")
        st.info(f"📁 Konum: `csv_files/{clean_filename}`")
        st.info("💡 Artık 'Mesajlaşma' sekmesinden bu dosyayı seçerek mesaj gönderebilirsiniz!")
        
        # Show valid numbers summary
        if valid_phones:
            with st.expander(f"📱 Geçerli Numaralar ({len(valid_phones)} adet)"):
                for item in valid_phones[:10]:  # Show first 10
                    st.write(f"• {item['name']} - {item['phone']}")
                if len(valid_phones) > 10:
                    st.write(f"... ve {len(valid_phones) - 10} numara daha")
        
        # Balloons for success
        st.balloons()
        
    except Exception as e:
        st.error(f"❌ Dosya kaydetme hatası: {str(e)}")
        st.info("Dosya adında özel karakter kullanmayın ve yazma izniniz olduğundan emin olun.")