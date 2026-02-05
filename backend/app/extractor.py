import re
from typing import List, Dict, Any
from .models import ExtractedIntel

def extract_intelligence(text: str) -> ExtractedIntel:
    """Extract all scammer intelligence from text with advanced patterns."""
    intel = ExtractedIntel()
    
    # Make text searchable (case-insensitive for some patterns)
    text_lower = text.lower()
    
    # ==================== UPI IDs ====================
    # Pattern: username@bankname (e.g., scammer@paytm, victim123@ybl)
    upi_pattern = r'\b[a-zA-Z0-9._-]{2,256}@[a-zA-Z]{2,64}\b'
    upi_matches = re.findall(upi_pattern, text, re.IGNORECASE)
    # Filter out email-like false positives (keep common UPI handles)
    upi_handles = ['paytm', 'ybl', 'oksbi', 'okaxis', 'okicici', 'okhdfcbank', 'ibl', 'upi', 'axl', 'waicici', 'yapl']
    intel.upi_ids = list(set([
        upi for upi in upi_matches 
        if any(handle in upi.lower() for handle in upi_handles)
    ]))
    
    # ==================== PHONE NUMBERS ====================
    # International and Indian formats
    phone_patterns = [
        r'\+?\d{1,4}[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}',  # International
        r'\b[6-9]\d{9}\b',  # Indian 10-digit
        r'\+91[-.\s]?[6-9]\d{9}\b',  # +91 prefix
        r'\b\d{3}[-.\s]\d{3}[-.\s]\d{4}\b',  # US format
    ]
    phone_numbers = []
    for pattern in phone_patterns:
        phone_numbers.extend(re.findall(pattern, text))
    
    # Clean and deduplicate phone numbers
    cleaned_phones = []
    for phone in phone_numbers:
        # Remove common separators
        clean = re.sub(r'[-.\s()]', '', phone)
        # Keep if reasonable length (8-15 digits)
        if 8 <= len(clean) <= 15 and clean.isdigit():
            cleaned_phones.append(clean)
    intel.phone_numbers = list(set(cleaned_phones))
    
    # ==================== BANK ACCOUNT NUMBERS ====================
    # Indian bank accounts: 9-18 digits
    # Look for context clues: "account", "a/c", "ac no", etc.
    account_pattern = r'\b\d{9,18}\b'
    potential_accounts = re.findall(account_pattern, text)
    
    # Context-aware filtering
    bank_keywords = ['account', 'a/c', 'ac no', 'acc', 'bank', 'ifsc', 'transfer']
    accounts = []
    for match in potential_accounts:
        # Find position of match in text
        pos = text.find(match)
        if pos != -1:
            # Check 50 chars before and after for bank keywords
            context = text[max(0, pos-50):min(len(text), pos+50)].lower()
            if any(keyword in context for keyword in bank_keywords):
                accounts.append(match)
    intel.bank_accounts = list(set(accounts))
    
    # ==================== CRYPTOCURRENCY WALLETS ====================
    crypto_wallets = []
    
    # Bitcoin: 26-35 alphanumeric, starts with 1, 3, or bc1
    # Use non-capturing group (?:...) for the prefix
    btc_pattern = r'\b(?:1|3|bc1)[a-zA-Z0-9]{25,34}\b'
    crypto_wallets.extend(re.findall(btc_pattern, text))
    
    # Ethereum: 0x followed by 40 hex characters
    eth_pattern = r'\b0x[a-fA-F0-9]{40}\b'
    crypto_wallets.extend(re.findall(eth_pattern, text))
    
    # Litecoin: Starts with L or M, 26-33 characters
    ltc_pattern = r'\b[LM][a-zA-Z0-9]{25,33}\b'
    crypto_wallets.extend(re.findall(ltc_pattern, text))
    
    # Dogecoin: Starts with D, 33-34 characters
    doge_pattern = r'\bD[a-zA-Z0-9]{32,33}\b'
    crypto_wallets.extend(re.findall(doge_pattern, text))
    
    intel.crypto_wallets = list(set(crypto_wallets))
    
    # ==================== URLs & PHISHING LINKS ====================
    # Comprehensive URL patterns
    url_patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',  # Standard HTTP/HTTPS
        r'www\.[^\s<>"{}|\\^`\[\]]+',  # www without protocol
        # Use non-capturing group for TLDs
        r'\b[a-zA-Z0-9-]+\.(?:com|net|org|info|xyz|tk|ml|ga|cf|gq|top|online|site|live|click|link)[^\s<>"{}|\\^`\[\]]*',  # Suspicious TLDs
    ]
    urls = []
    for pattern in url_patterns:
        urls.extend(re.findall(pattern, text, re.IGNORECASE))
    
    # Deduplicate and clean URLs
    cleaned_urls = []
    for url in urls:
        # Remove trailing punctuation
        url = re.sub(r'[.,;:\'\")]+$', '', url)
        # Add http:// if missing for www links
        if url.startswith('www.') and not url.startswith(('http://', 'https://')):
            url = 'http://' + url
        cleaned_urls.append(url)
    intel.urls = list(set(cleaned_urls))
    
    # ==================== EMAIL ADDRESSES ====================
    # Standard email pattern
    email_pattern = r'\b[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}\b'
    emails = re.findall(email_pattern, text, re.IGNORECASE)
    # Exclude UPI IDs already captured
    intel.emails = list(set([
        email for email in emails 
        if email not in intel.upi_ids
    ]))
    
    # ==================== LOCATION DATA ====================
    # Extract IP addresses
    ip_pattern = r'\b(?:\d{1,3}\.){3}\d{1,3}\b'
    potential_ips = re.findall(ip_pattern, text)
    # Validate IPs
    valid_ips = []
    for ip in potential_ips:
        try:
            if all(0 <= int(octet) <= 255 for octet in ip.split('.')):
                valid_ips.append(ip)
        except ValueError:
            pass
    intel.ip_addresses = list(set(valid_ips))
    
    return intel
