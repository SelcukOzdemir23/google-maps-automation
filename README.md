# Google Maps İşletme Kazıyıcı & WhatsApp Mesajlaşma

Google Maps'ten işletme bilgilerini kazıyan ve Türk cep telefonu numaralarına WhatsApp mesajı gönderen Streamlit uygulaması.

## Özellikler

- 🔍 Google Maps'ten işletme bilgilerini kazıma
- 📊 CSV dosyalarını görüntüleme ve filtreleme
- 📱 Türk cep telefonu numaralarına (05 ile başlayan) WhatsApp mesajı gönderme
- 🇹🇷 Tamamen Türkçe arayüz
- 📁 Otomatik CSV kaydetme

## Kurulum

1. Gerekli paketleri yükleyin:
```bash
pip install -r requirements.txt
```

2. Uygulamayı çalıştırın:
```bash
streamlit run app.py
```

## Kullanım

### 1. WhatsApp Ayarları
- Sol menüden telefon numaranızı girin (+90 ile başlayın)

### 2. CSV Seçme
- Mevcut CSV dosyalarından birini seçin
- Mesajınızı yazın
- "Tüm İşletmelere Gönder" veya tek tek gönder

### 3. Google Maps'ten Kazıma
- Ülke ve arama türünü girin
- Maksimum sonuç sayısını belirleyin
- "Kazımaya Başla" butonuna tıklayın

## Önemli Notlar

- ⚠️ Sadece **05 ile başlayan** Türk cep telefonu numaralarına mesaj gönderilebilir
- 📞 Sabit hat numaraları (0242, 0338 vb.) desteklenmez
- ⏱️ Mesajlar 2 dakika sonra gönderilmek üzere zamanlanır
- 🔄 Toplu gönderimde mesajlar arası 2 saniye bekleme vardır

## Dosya Yapısı

```
google-maps-automation/
├── app.py                 # Ana Streamlit uygulaması
├── wp_message_sender.py   # WhatsApp mesaj gönderme fonksiyonları
├── scraper.py            # Google Maps kazıyıcı (opsiyonel)
├── requirements.txt      # Gerekli paketler
├── csv_files/           # CSV dosyaları klasörü
└── README.md           # Bu dosya
```

## Gereksinimler

- Python 3.7+
- Chrome/Chromium tarayıcı (scraping için)
- WhatsApp Web erişimi