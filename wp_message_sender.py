# Lazy import to avoid X11 issues on startup

def is_valid_turkish_mobile(phone):
    """
    Check if phone number is a valid Turkish mobile number (starts with 05)
    """
    # Clean phone number
    clean_phone = phone.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    
    # Check if starts with 05 and has 11 digits total
    if clean_phone.startswith("05") and len(clean_phone) == 11:
        return True
    return False

def format_turkish_mobile(phone):
    """
    Format Turkish mobile number for WhatsApp (+90 prefix)
    """
    clean_phone = phone.replace(" ", "").replace("(", "").replace(")", "").replace("-", "")
    return "+90" + clean_phone[1:]  # Remove first 0 and add +90

def send_whatsapp_message(sender_phone, recipient_phone, message):
    """
    Send WhatsApp message using pywhatkit (only to Turkish mobile numbers)
    
    Args:
        sender_phone (str): Your phone number
        recipient_phone (str): Recipient's phone number
        message (str): Message to send
    """
    # Lazy import pywhatkit to avoid X11 issues on startup
    import pywhatkit
    
    # Validate Turkish mobile number
    if not is_valid_turkish_mobile(recipient_phone):
        raise Exception(f"Geçersiz numara: {recipient_phone} - Sadece 05 ile başlayan Türk cep telefonu numaralarına mesaj gönderilebilir")
    
    try:
        # Format phone number for WhatsApp
        formatted_phone = format_turkish_mobile(recipient_phone)
        
        # Send message instantly with proper timing and tab close
        pywhatkit.sendwhatmsg_instantly(
            formatted_phone, 
            message,
            wait_time=15,
            tab_close=True,
            close_time=5
        )
        return True
    except Exception as e:
        raise Exception(f"WhatsApp mesajı gönderilemedi: {str(e)}")

def create_sent_log():
    """Create or load sent messages log to prevent duplicates"""
    import os
    import json
    from datetime import datetime
    
    log_file = os.path.join(os.getcwd(), "sent_messages.json")
    
    if not os.path.exists(log_file):
        with open(log_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)
        return {}
    
    try:
        with open(log_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    except:
        return {}

def log_sent_message(phone, message_hash):
    """Log sent message to prevent duplicates"""
    import os
    import json
    import hashlib
    from datetime import datetime
    
    log_file = os.path.join(os.getcwd(), "sent_messages.json")
    sent_log = create_sent_log()
    
    # Create unique key for this phone-message combination
    key = f"{phone}_{message_hash}"
    sent_log[key] = datetime.now().isoformat()
    
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump(sent_log, f, ensure_ascii=False, indent=2)

def is_message_already_sent(phone, message):
    """Check if message was already sent to this phone"""
    import hashlib
    
    sent_log = create_sent_log()
    message_hash = hashlib.md5(message.encode()).hexdigest()[:8]
    key = f"{phone}_{message_hash}"
    
    return key in sent_log

# Example usage (commented out)
# send_whatsapp_message("+905349127082", "+905551234567", "Merhaba, bu bir test mesajıdır!")