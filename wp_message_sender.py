import pywhatkit

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
    # Validate Turkish mobile number
    if not is_valid_turkish_mobile(recipient_phone):
        raise Exception(f"Geçersiz numara: {recipient_phone} - Sadece 05 ile başlayan Türk cep telefonu numaralarına mesaj gönderilebilir")
    
    try:
        # Format phone number for WhatsApp
        formatted_phone = format_turkish_mobile(recipient_phone)
        
        # Send message instantly
        pywhatkit.sendwhatmsg_instantly(
            formatted_phone, 
            message,
            wait_time=10,
            tab_close=True
        )
        return True
    except Exception as e:
        raise Exception(f"WhatsApp mesajı gönderilemedi: {str(e)}")

# Example usage (commented out)
# send_whatsapp_message("+905349127082", "+905551234567", "Merhaba, bu bir test mesajıdır!")