import streamlit as st
import pandas as pd
import os
from wp_message_sender import is_valid_turkish_mobile

def show_csv_viewer():
    """CSV viewing page"""
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    if csv_files:
        selected_csv = st.selectbox("Bir CSV dosyası seçin", csv_files)
        df = pd.read_csv(os.path.join(csv_dir, selected_csv))
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
                st.info("💡 Mesaj göndermek için 'Mesaj Gönder' sekmesine geçin")
                
                with st.expander(f"Geçerli Numaraları Gör ({len(valid_phones)} adet)"):
                    for item in valid_phones:
                        st.write(f"• {item['name']} - {item['phone']}")
            else:
                st.warning("⚠️ 05 ile başlayan geçerli cep telefonu numarası bulunamadı.")
        else:
            st.warning("CSV dosyasında 'phone' sütunu bulunamadı.")
    else:
        st.info("'csv_files' klasöründe CSV dosyası bulunamadı. Yeni veri kazıyın veya dosyaları bu klasöre ekleyin.")