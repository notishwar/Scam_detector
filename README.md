# Agentic Honey-Pot – Scam Intelligence Dashboard 🍯

A fully working, responsive, multi-user, API-key-driven web application designed to waste scammers' time while extracting actionable intelligence.

## Features

### 🤖 Intelligent AI Agent System
- **3 Distinct AI Personas:**
  - **Elderly (Earl)** - 78-year-old retired gardener, slow, confused, asks for backup contact details
  - **Student (Alex)** - 22-year-old college student, skeptical, demands proof and verification
  - **Naive (Jamie)** - Overly trusting, makes mistakes, gets easily distracted
- **Intelligence-Gathering Tactics:**
  - Asks for "all payment options" to extract multiple UPI/bank details
  - Requests backup numbers, alternative links, verification codes
  - Pretends to have technical difficulties to waste scammer time
  - Acts incompetent to force scammers to repeat information

### 🔍 Advanced Intelligence Extraction
- 💳 **UPI IDs** (e.g., `scammer@paytm`, `fraudster@ybl`)
- 🏦 **Bank Account Numbers** (context-aware filtering)
- 📱 **Phone Numbers** (Indian, US, international formats)
- 💰 **Cryptocurrency Wallets** (Bitcoin, Ethereum, Litecoin, Dogecoin)
- 🔗 **Phishing URLs** (suspicious TLDs, shortened links)
- 📧 **Email Addresses**
- 🌐 **IP Addresses** (with validation)

### 📊 Smart Fraud Detection
- **Context-Aware Scoring:** "Pay the bill" = 15% vs "Police! Pay to UPI now!" = 100%
- **Real-Time Risk Tags:** `CRYPTO_SCAM`, `PHISHING_LINK`, `FINANCIAL_FRAUD`
- **No False Positives:** Differentiates normal conversations from scams

### 🎨 Premium UI
- **Modern dark/light themes** with smooth transitions
- **Responsive design** (Desktop, Tablet, Mobile)
- **Real-time intelligence panel** displaying extracted data as JSON
- **Live fraud risk meter** (0-100% with color coding)

### 🔒 Security & Privacy
- User-provided API keys (stored in browser session only)
- No data persistence - sessions are in-memory
- Isolated sessions by API key


## Prerequisites
- Python 3.8+
- An LLM API Key (e.g., OpenAI `sk-...`).

## Setup & Running

### 1. Backend
Navigate to the `backend` directory and install dependencies:
```bash
cd backend
pip install -r requirements.txt
```

Run the FastAPI server:
```bash
cd app
uvicorn main:app --reload
```
*Server will start at `http://127.0.0.1:8000`*

### 2. Frontend
Open `frontend/index.html` in your browser.
*No build build step required! It uses Vanilla JS.*

## How to Use
1. Open the Frontend.
2. Enter your **OpenAI API Key** in the top bar settings.
3. Select a **Persona** (e.g., "Earl - 78yo Retired").
4. Paste a **Scammer's Message** in the input box.
5. Click **Analyze & Reply**.
6. Watch the agent reply and extract intelligence in the right panel!

## Project Structure
```
project/
│── backend/
│   │── app/
│   │   │── main.py       # API Entry point
│   │   │── agent.py      # LLM Agent Logic
│   │   │── detector.py   # Scam Detection
│   │   │── extractor.py  # Regex Intel Extraction
│   │   │── ...
│   │── requirements.txt
│
│── frontend/
│   │── index.html
│   │── styles.css
│   │── app.js
```

## Security Notes
- API Keys are sent via `X-LLM-API-KEY` header.
- The backend does **not** store your API key.
- Sessions are in-memory and isolated by API key.
