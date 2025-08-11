# Google Maps Business Scraper & WhatsApp Messenger

A Streamlit application that scrapes business information from Google Maps and sends WhatsApp messages to Turkish mobile numbers.

## Features

- 🔍 Scrape business information from Google Maps
- 📊 View and filter CSV files
- 📱 Send WhatsApp messages to Turkish mobile numbers (starting with 05)
- 🇹🇷 Turkish interface
- 📁 Automatic CSV saving

## Installation

1. Install required packages:
```bash
pip install -r requirements.txt
```

2. Run the application:
```bash
streamlit run app.py
```

## Usage

### 1. WhatsApp Settings
- Enter your phone number in the sidebar (start with +90)

### 2. CSV Selection
- Select an existing CSV file
- Write your message
- Click "Send to All Businesses" or send individually

### 3. Google Maps Scraping
- Enter country and search type
- Set maximum results
- Click "Start Scraping"

## Important Notes

- ⚠️ Only **Turkish mobile numbers starting with 05** can receive messages
- 📞 Landline numbers (0242, 0338 etc.) are not supported
- ⏱️ Messages are scheduled to be sent 2 minutes later
- 🔄 2-second delay between messages in bulk sending

## File Structure

```
google-maps-automation/
├── app.py                 # Main Streamlit application
├── wp_message_sender.py   # WhatsApp messaging functions
├── scraper.py            # Google Maps scraper (optional)
├── requirements.txt      # Required packages
├── csv_files/           # CSV files directory
└── README.md           # This file
```

## Requirements

- Python 3.7+
- Chrome/Chromium browser (for scraping)
- WhatsApp Web access