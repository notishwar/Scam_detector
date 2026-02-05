from typing import List, Tuple, Dict
from .models import ExtractedIntel

# Weighted scoring system
SCAM_INDICATORS = {
    # HARD EVIDENCE - Almost certainly a scam in this context
    "crypto_wallet": 85.0,
    "phishing_link": 80.0,
    "upi_id": 70.0,      # Slightly lowered as sharing UPI can be normal, depends on context
    "bank_details": 60.0,
    
    # CONTEXTUAL RISKS - Needs combination
    "remote_access": 60.0,    # Very suspicious (AnyDesk etc)
    "money_request": 15.0,    # Lowered: "Pay me" happens in normal life
    "impersonation": 15.0,    # Lowered: "I am from the bank" happens
    "urgency": 15.0,          # Lowered: "Do it now" happens
    "suspicious_request": 25.0 # asking for OTP/Pin is always bad
}

KEYWORDS = {
    "urgency": [
        "urgently", "immediately", "as soon as possible", "right now", "expires", 
        "limited time", "act now", "last chance", "blocked", "suspended", "deadline"
    ],
    "money_request": [
        "pay", "transfer", "send money", "deposit", "fee", "tax", "charge", 
        "refund", "investment", "profit", "earn", "salary", "prize", "winner"
    ],
    "impersonation": [
        "customer support", "police", "irs", "tax department", "cbi", "fbi", 
        "customs", "amazon", "microsoft", "apple", "google", "bank manager"
    ],
    "remote_access": [
        "anydesk", "teamviewer", "quicksupport", "screen share", "download this app", 
        "apk", "install"
    ],
    "suspicious_request": [
        "verify otp", "share otp", "password", "pin", "cvv", "card details", 
        "login credentials", "verify account", "update kyc"
    ]
}

def detect_scam_heuristics(message: str, intel: ExtractedIntel = None) -> Tuple[float, List[str]]:
    """
    Returns (confidence_score, risk_tags) based on extracted intel and keyword analysis.
    Confidence is 0-100.
    """
    message_lower = message.lower()
    risk_tags = set()
    score = 0.0
    
    # 1. Check Extracted Intelligence (Hard Evidence)
    if intel:
        if intel.crypto_wallets:
            score += SCAM_INDICATORS["crypto_wallet"]
            risk_tags.add("CRYPTO_SCAM")
            
        if intel.upi_ids:
            # UPI check needs context. 
            # If accompanied by "urgency" or "money_request", it's high risk.
            # Isolated UPI might just be a friend sharing an ID.
            if "urgency" in risk_tags or "money_request" in risk_tags or "impersonation" in risk_tags:
                score += SCAM_INDICATORS["upi_id"]
                risk_tags.add("FINANCIAL_FRAUD")
            else:
                score += 30.0 # Moderate risk for just a UPI ID without context
            
        if intel.bank_accounts:
            if "urgency" in risk_tags or "money_request" in risk_tags:
                score += SCAM_INDICATORS["bank_details"]
                risk_tags.add("BANK_FRAUD")
            else:
                score += 20.0 # Low risk for just an account number
            
        if intel.urls:
            # Check for suspicious URLs
            # If it's a known benign domain (google, youtube, etc), maybe ignore? 
            # For now, we assume extracted.urls contains mostly suspicious ones based on regex
            score += SCAM_INDICATORS["phishing_link"]
            risk_tags.add("PHISHING_LINK")
            
        if intel.phone_numbers:
            # Phone number alone is not a scam
            pass
            
    # 2. Keyword Analysis (Contextual Evidence)
    for category, keywords in KEYWORDS.items():
        if any(kw in message_lower for kw in keywords):
            risk_tags.add(category) # Use lowercase tag for internal logic
            score += SCAM_INDICATORS.get(category, 10.0)
            
    # 3. Apply Multiplier for Combinations
    # Real scams combine Urgency + Authority + Payment
    risk_factors = 0
    if "urgency" in risk_tags: risk_factors += 1
    if "money_request" in risk_tags: risk_factors += 1
    if "impersonation" in risk_tags: risk_factors += 1
    if "remote_access" in risk_tags: risk_factors += 2
    
    if risk_factors >= 2:
        score *= 1.5 # High booster for combinations
    
    # 4. Length & Safety Checks
    if len(message.split()) < 3 and score < 50:
        score = 0.0
        risk_tags.clear()
        
    # Cap score at 100
    score = min(round(score, 1), 100.0)
    
    # Ensure High Risk items push score effectively
    if "CRYPTO_SCAM" in risk_tags or "PHISHING_LINK" in risk_tags or "remote_access" in risk_tags:
        score = max(score, 80.0)
    
    # Format tags for display (Uppercase)
    display_tags = [tag.upper() for tag in risk_tags if "_" not in tag] # Keywords
    display_tags.extend([tag for tag in risk_tags if "_" in tag]) # Hard evidence tags
        
    return score, list(set(display_tags))
