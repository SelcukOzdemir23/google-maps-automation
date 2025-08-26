import streamlit as st
import pandas as pd
import os
import time
from wp_message_sender import send_whatsapp_message, is_valid_turkish_mobile, is_message_already_sent, log_sent_message

def show_messaging_page():
    """WhatsApp messaging page with enhanced UI/UX"""
    # Header with gradient background
    st.markdown("""
    <div style="background: linear-gradient(90deg, #25D366 0%, #128C7E 100%); padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem; text-align: center;">
        <h2 style="color: white; margin: 0; font-size: 2rem;">📱 WhatsApp Mesaj Gönderme</h2>
        <p style="color: #f0f0f0; margin: 0.5rem 0 0 0; font-size: 1.1rem;">Türk cep telefonu numaralarına toplu mesaj gönderin</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Step-by-step process
    _show_step_process()

def _show_step_process():
    """Show step-by-step messaging process"""
    # Initialize session state
    if 'messaging_step' not in st.session_state:
        st.session_state.messaging_step = 1
    if 'selected_csv' not in st.session_state:
        st.session_state.selected_csv = None
    if 'user_phone' not in st.session_state:
        st.session_state.user_phone = None
    if 'message_content' not in st.session_state:
        st.session_state.message_content = ""
    
    # Progress indicator
    progress_col1, progress_col2, progress_col3, progress_col4 = st.columns(4)
    
    with progress_col1:
        if st.session_state.messaging_step >= 1:
            st.markdown("🟢 **1. Veri Seç**")
        else:
            st.markdown("⚪ 1. Veri Seç")
    
    with progress_col2:
        if st.session_state.messaging_step >= 2:
            st.markdown("🟢 **2. Telefon**")
        else:
            st.markdown("⚪ 2. Telefon")
    
    with progress_col3:
        if st.session_state.messaging_step >= 3:
            st.markdown("🟢 **3. Mesaj**")
        else:
            st.markdown("⚪ 3. Mesaj")
    
    with progress_col4:
        if st.session_state.messaging_step >= 4:
            st.markdown("🟢 **4. Gönder**")
        else:
            st.markdown("⚪ 4. Gönder")
    
    st.markdown("---")
    
    # Step 1: CSV Selection
    if st.session_state.messaging_step == 1:
        _show_csv_selection_step()
    
    # Step 2: Phone Input
    elif st.session_state.messaging_step == 2:
        _show_phone_input_step()
    
    # Step 3: Message Composition
    elif st.session_state.messaging_step == 3:
        _show_message_composition_step()
    
    # Step 4: Send Messages
    elif st.session_state.messaging_step == 4:
        _show_send_messages_step()

def _show_csv_selection_step():
    """Step 1: CSV file selection"""
    st.markdown("### 📄 Adım 1: Veri Dosyası Seçimi")
    
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    if not os.path.exists(csv_dir):
        os.makedirs(csv_dir)
    csv_files = [f for f in os.listdir(csv_dir) if f.endswith('.csv')]
    
    if not csv_files:
        st.error("🙅‍♂️ Hiçbir CSV dosyası bulunamadı!")
        st.info("💡 Önce 'Google Maps Kazı' sekmesinden veri kazıyın.")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        selected_csv = st.selectbox(
            "Mesaj gönderilecek CSV dosyasını seçin:",
            csv_files,
            help="Kazıdığınız işletme verilerini içeren dosyayı seçin"
        )
        
        if selected_csv:
            # Preview CSV data with proper separator detection
            file_path = os.path.join(csv_dir, selected_csv)
            try:
                df = pd.read_csv(file_path, dtype={'phone': str})
                # Check if semicolon separated
                if len(df.columns) == 1 and ';' in df.columns[0]:
                    df = pd.read_csv(file_path, dtype={'phone': str}, sep=';')
            except:
                df = pd.read_csv(file_path, dtype={'phone': str}, sep=';')
            valid_phones = _get_valid_phones(df)
            
            st.success(f"✅ **{selected_csv}** seçildi")
            st.info(f"📊 **{len(df)}** toplam kayıt | **{len(valid_phones)}** geçerli numara")
            
            with st.expander("🔍 Veri Önizlemesi"):
                st.dataframe(df.head(3), use_container_width=True)
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        if st.button("➡️ Devam Et", type="primary", use_container_width=True):
            if selected_csv:
                st.session_state.selected_csv = selected_csv
                st.session_state.messaging_step = 2
                st.rerun()
            else:
                st.error("Lütfen bir CSV dosyası seçin!")

def _show_phone_input_step():
    """Step 2: Phone number input"""
    st.markdown("### 📞 Adım 2: Telefon Numaranız")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        phone_input = st.text_input(
            "WhatsApp telefon numaranızı girin:",
            placeholder="5349128082 veya 534 912 8082",
            help="10 haneli cep telefonu numaranızı girin (+90 otomatik eklenecek)",
            value=st.session_state.get('user_phone', '').replace('+90', '') if st.session_state.get('user_phone', '').startswith('+90') else st.session_state.get('user_phone', '')
        )
        
        if phone_input:
            # Clean and format phone number
            clean_phone = phone_input.replace(' ', '').replace('(', '').replace(')', '').replace('-', '')
            
            # Remove +90 if user entered it
            if clean_phone.startswith('+90'):
                clean_phone = clean_phone[3:]
            elif clean_phone.startswith('90'):
                clean_phone = clean_phone[2:]
            
            # Check if valid 10-digit mobile number starting with 5
            if len(clean_phone) == 10 and clean_phone.startswith('5') and clean_phone.isdigit():
                formatted_phone = f"+90{clean_phone}"
                st.success(f"✅ Geçerli numara: **{formatted_phone}**")
                valid_phone = True
                # Update session state with formatted number
                st.session_state.user_phone = formatted_phone
            else:
                st.error("❌ Geçersiz format! 10 haneli cep telefonu numarası girin (5 ile başlamalı)")
                st.info("💡 Örnek: 5349128082 veya 534 912 8082")
                valid_phone = False
        else:
            valid_phone = False
    
    with col2:
        st.markdown("<br><br>", unsafe_allow_html=True)
        col_back, col_next = st.columns(2)
        
        with col_back:
            if st.button("⬅️ Geri", use_container_width=True):
                st.session_state.messaging_step = 1
                st.rerun()
        
        with col_next:
            if st.button("➡️ Devam Et", type="primary", use_container_width=True):
                if valid_phone:
                    # Phone is already formatted and stored in session state
                    st.session_state.messaging_step = 3
                    st.rerun()
                else:
                    st.error("Geçerli bir telefon numarsı girin!")

def _show_message_composition_step():
    """Step 3: Message composition"""
    st.markdown("### ✍️ Adım 3: Mesajınızı Hazırlayın")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Message templates with better organization
        st.markdown("**Hazır Şablonlar:**")
        template_col1, template_col2, template_col3 = st.columns(3)
        
        with template_col1:
            if st.button("🍕 QR Menü", use_container_width=True):
                st.session_state.message_content = """Merhaba! 😊

İşletmeniz için dijital QR menü çözümleri geliştiriyoruz.

Size fikir vermesi için örnek bir menüyü paylaşıyorum:
https://digital-menu-example.com

İlginizi çekerse bu numaradan bize ulaşabilirsiniz.

Teşekkürler! 🙏"""
        
        with template_col2:
            if st.button("💻 Dijital Hizmet", use_container_width=True):
                st.session_state.message_content = """Merhaba!

İşletmeniz için dijital çözümler sunuyoruz:

• Web sitesi tasarımı
• Sosyal medya yönetimi  
• Dijital pazarlama

Detaylı bilgi için bize ulaşabilirsiniz.

Saygılarımla"""
        
        with template_col3:
            if st.button("🧙‍♂️ Temizle", use_container_width=True):
                st.session_state.message_content = ""
        
        # Message input
        message = st.text_area(
            "Mesajınız:",
            value=st.session_state.message_content,
            height=250,
            help="Mesajınızı yazın veya yukarıdaki şablonlardan birini seçin",
            key="message_input"
        )
        
        # Character count
        char_count = len(message)
        if char_count > 1600:
            st.warning(f"⚠️ Mesaj çok uzun: {char_count} karakter (Max: 1600)")
        else:
            st.info(f"📝 Karakter sayısı: {char_count}/1600")
    
    with col2:
        # Message preview
        st.markdown("**🔍 Önizleme:**")
        if message:
            st.text_area(
                "Gönderilecek mesaj:",
                value=message,
                height=200,
                disabled=True
            )
        else:
            st.info("Mesaj yazın...")
        
        # Navigation buttons
        st.markdown("<br>", unsafe_allow_html=True)
        col_back, col_next = st.columns(2)
        
        with col_back:
            if st.button("⬅️ Geri", use_container_width=True):
                st.session_state.messaging_step = 2
                st.rerun()
        
        with col_next:
            if st.button("➡️ Devam Et", type="primary", use_container_width=True):
                if message.strip():
                    st.session_state.message_content = message
                    st.session_state.messaging_step = 4
                    st.rerun()
                else:
                    st.error("Lütfen bir mesaj yazın!")

def _show_send_messages_step():
    """Step 4: Send messages"""
    st.markdown("### 🚀 Adım 4: Mesajları Gönder")
    
    # Load data with proper separator detection
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    file_path = os.path.join(csv_dir, st.session_state.selected_csv)
    try:
        df = pd.read_csv(file_path, dtype={'phone': str})
        # Check if semicolon separated
        if len(df.columns) == 1 and ';' in df.columns[0]:
            df = pd.read_csv(file_path, dtype={'phone': str}, sep=';')
    except:
        df = pd.read_csv(file_path, dtype={'phone': str}, sep=';')
    valid_phones = _get_valid_phones(df)
    
    # Summary card
    st.markdown("""
    <div style="background: #f0f8ff; padding: 1rem; border-radius: 10px; border-left: 5px solid #1f77b4; margin-bottom: 1rem;">
        <h4 style="margin: 0; color: #1f77b4;">📊 Gönderim Özeti</h4>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📄 CSV Dosyası", st.session_state.selected_csv)
    with col2:
        st.metric("📞 Telefon", st.session_state.user_phone)
    with col3:
        st.metric("📱 Geçerli Numara", len(valid_phones))
    with col4:
        msg_len = len(st.session_state.message_content)
        st.metric("📝 Mesaj Uzunluğu", f"{msg_len} kar.", delta=f"{msg_len}/1600" if msg_len <= 1600 else "Çok uzun!")
    
    if not valid_phones:
        st.error("🙅‍♂️ Geçerli cep telefonu numarası bulunamadı!")
        if st.button("⬅️ Geri Dön", type="primary"):
            st.session_state.messaging_step = 1
            st.rerun()
        return
    
    # Sending options
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Message preview
        with st.expander("🔍 Mesaj Önizlemesi", expanded=False):
            st.text_area("Gönderilecek mesaj:", st.session_state.message_content, height=150, disabled=True)
        
        # Contact selection
        st.markdown("**🎯 Hedef Seçimi:**")
        send_option = st.radio(
            "Kime gönderilsin?",
            ["Tüm numaralar", "Seçili numaralar"],
            horizontal=True
        )
        
        selected_indices = []
        if send_option == "Seçili numaralar":
            st.markdown("**Gönderilecek numaraları seçin:**")
            for i, item in enumerate(valid_phones[:10]):  # Show first 10
                if st.checkbox(f"{item['name']} - {item['phone']}", key=f"contact_{i}"):
                    selected_indices.append(i)
            
            if len(valid_phones) > 10:
                if st.checkbox(f"Diğer {len(valid_phones) - 10} numara", key="select_all_remaining"):
                    selected_indices.extend(list(range(10, len(valid_phones))))
        else:
            selected_indices = list(range(len(valid_phones)))
    
    with col2:
        # Settings
        st.markdown("**⚙️ Ayarlar:**")
        delay_seconds = st.slider(
            "Mesajlar arası bekleme:",
            min_value=1,
            max_value=30,
            value=5,
            help="Saniye cinsinden bekleme süresi"
        )
        
        # Send button
        selected_count = len(selected_indices)
        if selected_count > 0:
            st.markdown(f"**📱 {selected_count} numaraya gönderilecek**")
            
            if st.button(
                f"🚀 {selected_count} Numaraya Gönder",
                type="primary",
                use_container_width=True
            ):
                _send_bulk_messages_enhanced(valid_phones, selected_indices, st.session_state.message_content, st.session_state.user_phone, delay_seconds)
        else:
            st.warning("Hiçbir numara seçilmedi!")
        
        # Navigation
        st.markdown("---")
        if st.button("⬅️ Mesajı Düzenle", use_container_width=True):
            st.session_state.messaging_step = 3
            st.rerun()
        
        if st.button("🔄 Baştan Başla", use_container_width=True):
            st.session_state.messaging_step = 1
            st.session_state.selected_csv = None
            st.session_state.user_phone = None
            st.session_state.message_content = ""
            st.rerun()

def _show_messaging_interface(selected_csv, user_phone):
    """Show the main messaging interface"""
    csv_dir = os.path.join(os.getcwd(), "csv_files")
    df_current = pd.read_csv(os.path.join(csv_dir, selected_csv))
    
    # Get valid phone numbers
    valid_phones = _get_valid_phones(df_current)
    
    if not valid_phones:
        st.warning("⚠️ Yüklü veride geçerli cep telefonu numarası bulunamadı.")
        return
    
    # Show data info
    st.markdown("---")
    st.info(f"📈 **Seçili CSV:** {selected_csv} | {len(df_current)} kayıt | {len(valid_phones)} geçerli numara")
    
    with st.expander("🔍 Veri Önizlemesi"):
        st.dataframe(df_current.head(3), use_container_width=True)
    
    # Message composition and sending
    message = _show_message_composer()
    _show_bulk_sender(valid_phones, message, user_phone)
    _show_individual_contacts(valid_phones, message, user_phone)

def _get_valid_phones(df):
    """Extract valid phone numbers from dataframe with deduplication"""
    valid_phones = []
    seen_phones = set()  # Track unique phone numbers
    
    if "phone" in df.columns:
        for idx, row in df.iterrows():
            phone = str(row["phone"]).replace(" ", "")
            if phone and phone != "nan" and is_valid_turkish_mobile(phone):
                # Only add if phone number hasn't been seen before
                if phone not in seen_phones:
                    valid_phones.append({
                        "name": row.get('name', 'İşletme'), 
                        "phone": phone, 
                        "idx": idx,
                        "address": row.get('address', '')
                    })
                    seen_phones.add(phone)
    return valid_phones

def _show_message_composer():
    """Show message composition interface"""
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("#### ✍️ Mesajınızı Yazın")
        
        template_options = {
            "Boş Mesaj": "",
            "QR Menü Tanıtım": """Merhaba! 😊

İşletmeniz için dijital QR menü çözümleri geliştiriyoruz.

Size fikir vermesi için örnek bir menüyü paylaşıyorum:
https://digital-menu-example.com

İlginizi çekerse bu numaradan bize ulaşabilirsiniz.

Teşekkürler! 🙏""",
            "Genel Tanıtım": """Merhaba!

İşletmeniz için dijital çözümler sunuyoruz:

• Web sitesi tasarımı
• Sosyal medya yönetimi  
• Dijital pazarlama

Detaylı bilgi için bize ulaşabilirsiniz.

Saygılarımla"""
        }
        
        selected_template = st.selectbox("Mesaj Şablonu Seçin:", list(template_options.keys()))
        message = st.text_area(
            "Mesajınız:",
            value=template_options[selected_template],
            height=300,
            help="Mesajınızı yazın. Alt satır geçmek için Enter'a basın."
        )
        
        if message:
            st.markdown("**Mesaj Önizleme:**")
            st.text_area("Gönderilecek mesaj:", value=message, height=200, disabled=True)
    
    return message

def _show_bulk_sender(valid_phones, message, user_phone):
    """Show bulk message sending interface"""
    col1, col2 = st.columns([2, 1])
    
    with col2:
        st.markdown("#### 🎯 Hedef Kişiler")
        st.success(f"📱 {len(valid_phones)} geçerli numara")
        
        delay_seconds = st.slider("Mesajlar arası bekleme (saniye):", min_value=1, max_value=30, value=5)
        
        st.markdown("**Numara Seçimi:**")
        send_option = st.radio("Gönderim seçeneği:", ["Tüm Numaralar", "Seçili Numaralar"])
        
        selected_indices = []
        if send_option == "Seçili Numaralar":
            st.markdown("Gönderilecek numaraları seçin:")
            for i, item in enumerate(valid_phones):
                if st.checkbox(f"{item['name']} - {item['phone']}", key=f"select_{i}"):
                    selected_indices.append(i)
        else:
            selected_indices = list(range(len(valid_phones)))
        
        # Send button
        if message and selected_indices:
            selected_count = len(selected_indices)
            if st.button(f"🚀 {selected_count} Numaraya Gönder", type="primary", use_container_width=True):
                _send_bulk_messages(valid_phones, selected_indices, message, user_phone, delay_seconds)
        elif not message:
            st.warning("⚠️ Mesaj yazın")
        elif not selected_indices:
            st.warning("⚠️ En az bir numara seçin")

def _send_bulk_messages_enhanced(valid_phones, selected_indices, message, user_phone, delay_seconds):
    """Enhanced bulk message sending with duplicate prevention"""
    import hashlib
    
    # Create containers for better organization
    progress_container = st.container()
    results_container = st.container()
    
    with progress_container:
        st.markdown("""
        <div style="background: #e8f5e8; padding: 1rem; border-radius: 10px; border-left: 5px solid #28a745; margin-bottom: 1rem;">
            <h4 style="margin: 0; color: #28a745;">🚀 Mesaj Gönderimi Başlatıldı</h4>
        </div>
        """, unsafe_allow_html=True)
        
        progress_bar = st.progress(0)
        status_text = st.empty()
        current_contact = st.empty()
    
    success_count = 0
    error_count = 0
    skip_count = 0
    selected_count = len(selected_indices)
    
    # Results tracking
    results = []
    
    # Create message hash for duplicate checking
    message_hash = hashlib.md5(message.encode()).hexdigest()[:8]
    
    for i, idx in enumerate(selected_indices):
        item = valid_phones[idx]
        
        # Update current contact info
        current_contact.info(f"📱 İşleniyor ({i+1}/{selected_count}): **{item['name']}** - {item['phone']}")
        
        # Check if message already sent to this number
        if is_message_already_sent(item['phone'], message):
            skip_count += 1
            results.append({
                "name": item['name'],
                "phone": item['phone'],
                "status": "skipped",
                "message": "Bu numaraya aynı mesaj daha önce gönderildi"
            })
        else:
            try:
                send_whatsapp_message(user_phone, item['phone'], message)
                log_sent_message(item['phone'], message_hash)
                success_count += 1
                results.append({
                    "name": item['name'],
                    "phone": item['phone'],
                    "status": "success",
                    "message": "Başarıyla gönderildi"
                })
                
                # Wait between messages (except for last one)
                if i < selected_count - 1:
                    time.sleep(delay_seconds)
                    
            except Exception as e:
                error_count += 1
                results.append({
                    "name": item['name'],
                    "phone": item['phone'],
                    "status": "error",
                    "message": str(e)[:100]
                })
        
        # Update progress
        progress = (i + 1) / selected_count
        progress_bar.progress(progress)
        status_text.text(f"İlerleme: {i+1}/{selected_count} ({int(progress*100)}%)")
    
    # Final status
    current_contact.empty()
    status_text.success("✅ Tüm mesajlar işlendi!")
    
    # Show results
    with results_container:
        st.markdown("---")
        
        # Summary metrics
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.metric("📱 Toplam", selected_count)
        with col2:
            st.metric("✅ Başarılı", success_count, delta=f"{int(success_count/selected_count*100)}%" if selected_count > 0 else "0%")
        with col3:
            st.metric("❌ Hatalı", error_count, delta=f"{int(error_count/selected_count*100)}%" if error_count > 0 else None)
        with col4:
            st.metric("⏭️ Atlandı", skip_count, delta="Duplicate" if skip_count > 0 else None)
        with col5:
            actual_sent = success_count + error_count  # Only count actual attempts
            total_time = actual_sent * delay_seconds
            st.metric("⏱️ Süre", f"{total_time//60}dk {total_time%60}sn")
        
        # Detailed results
        if error_count > 0 or skip_count > 0:
            with st.expander(f"📄 Detaylı Sonuçlar ({error_count} hata, {skip_count} atlandı)", expanded=True):
                for result in results:
                    if result['status'] == 'success':
                        st.success(f"✅ {result['name']} - {result['phone']} - {result['message']}")
                    elif result['status'] == 'skipped':
                        st.info(f"⏭️ {result['name']} - {result['phone']} - {result['message']}")
                    else:
                        st.error(f"❌ {result['name']} - {result['phone']} - {result['message']}")
        else:
            st.success("🎉 Tüm mesajlar başarıyla gönderildi!")
            st.balloons()
        
        # Reset button
        if st.button("🔄 Yeni Mesaj Gönderimi", type="primary", use_container_width=True):
            st.session_state.messaging_step = 1
            st.session_state.selected_csv = None
            st.session_state.user_phone = None
            st.session_state.message_content = ""
            st.rerun()

def _show_individual_contacts(valid_phones, message, user_phone):
    """Show individual contact list with send buttons"""
    st.markdown("---")
    st.markdown("#### 📞 Kişiler Listesi")
    
    for i, item in enumerate(valid_phones):
        with st.expander(f"🏢 {item['name']} - {item['phone']}"):
            col_info, col_send = st.columns([3, 1])
            
            with col_info:
                st.write(f"**İsim:** {item['name']}")
                st.write(f"**Telefon:** {item['phone']}")
                if item['address']:
                    st.write(f"**Adres:** {item['address'][:100]}...")
            
            with col_send:
                if message:
                    if st.button(f"📱 Gönder", key=f"send_individual_{i}", use_container_width=True):
                        try:
                            with st.spinner("Gönderiliyor..."):
                                send_whatsapp_message(user_phone, item['phone'], message)
                            st.success("✅ Gönderildi!")
                        except Exception as e:
                            st.error(f"❌ Hata: {str(e)[:30]}...")
                else:
                    st.warning("Mesaj yazın")