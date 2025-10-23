# Thames Water Customer Chatbot 💧

An interactive AI chatbot for Thames Water customers built with Streamlit. Available in both **voice-enabled** and **text-only** versions to help customers with billing, water services, emergencies, and account management.

## 🆕 Voice-Enabled Version Available!

We now offer a **voice chatbot** with speech-to-text and text-to-speech capabilities! See [VOICE_CHATBOT_README.md](VOICE_CHATBOT_README.md) for details.

### Choose Your Version:
- **🎤 Voice Chatbot** (`voice_chatbot.py`) - Full voice interaction with microphone input and audio responses
- **💬 Text Chatbot** (`water_company_chatbot.py`) - Classic text-based chat interface

## Features

### Core Features (Both Versions)
- **Smart Intent Detection**: Automatically understands customer queries and provides relevant responses
- **Thames Water Specific**: Real contact numbers, services, and information for Thames Water customers
- **Emergency Response**: Special handling for urgent water-related issues with correct emergency numbers (0800 714 614)
- **Billing Support**: Help with payments, Direct Debit, high bills, WaterSure schemes
- **Service Issues**: Assistance with water pressure, outages, quality concerns, and leaks
- **Account Management**: MyThamesWater account and mobile app information
- **Quick Actions**: One-click buttons for common tasks
- **Service Status**: Real-time display of system status
- **Modern UI**: Clean, professional Thames Water branding

### Voice Chatbot Additional Features
- **🎤 Voice Input**: Speak your questions using your microphone
- **🔊 Voice Output**: Listen to responses with text-to-speech
- **🔄 Dual Mode**: Switch between voice and text seamlessly
- **Real-time Processing**: Fast speech recognition and response generation

## Quick Start

### Option 1: Voice Chatbot (Recommended)
```bash
# Linux/Mac
./install_voice.sh

# Windows
install_voice.bat

# Run the voice chatbot
streamlit run voice_chatbot.py
```

### Option 2: Text-Only Chatbot
```bash
# Install minimal dependencies
pip install streamlit

# Run the text chatbot
streamlit run water_company_chatbot.py
```

Open your browser at `http://localhost:8501` and start chatting!

## Installation

### Text-Only Version
```bash
pip install streamlit>=1.28.0
streamlit run water_company_chatbot.py
```

### Voice-Enabled Version
See detailed instructions in [VOICE_CHATBOT_README.md](VOICE_CHATBOT_README.md)

**Quick install:**
```bash
pip install -r requirements.txt
streamlit run voice_chatbot.py
```

## Usage Examples

Try asking either chatbot:
- "How do I pay my bill?"
- "I have low water pressure"
- "My water bill is very high"
- "How do I report a leak?"
- "What are your customer service hours?"
- "I have no water supply"
- "Tell me about the MyThamesWater app"

## Features Overview

### 🤖 Smart Responses
The chatbot uses keyword detection to understand user intent and provide contextually relevant responses for:
- Billing and payment questions
- Water service issues
- Emergency situations
- Customer support inquiries
- Account management

### 🔧 Quick Actions Sidebar
- Check bill status
- Report water issues
- Get contact information
- View service status

### 🚨 Emergency Handling
Special responses for urgent situations like:
- Water main breaks
- Flooding
- No water service
- Gas leaks near water lines

### 📊 Service Status
Real-time display showing:
- Water supply status
- System pressure
- Planned maintenance notifications

## Customization

You can easily customize the chatbot by modifying:

- **Company Information**: Update the `WATER_COMPANY_KB` dictionary with your company's specific information
- **Intent Keywords**: Modify `INTENT_PATTERNS` to include terms specific to your customer base
- **Branding**: Change colors, company name, and styling in the Streamlit interface
- **Contact Information**: Update phone numbers, websites, and service hours

## Security Features

- No external API dependencies (runs completely offline)
- No hardcoded API keys or sensitive information
- Safe for deployment without security concerns

## Thames Water Contact Information

The chatbot provides accurate Thames Water contact numbers:

| Service | Number | Hours |
|---------|--------|-------|
| General Enquiries | 0800 980 8800 | Mon-Fri 8AM-8PM, Sat 8AM-6PM |
| Water Emergency | 0800 714 614 | 24/7 |
| Sewer Flooding | 0800 316 9800 | 24/7 |
| Payment Support | 0800 009 3652 | Business hours |

## Requirements

### Text-Only Chatbot
- Python 3.8+
- Streamlit 1.28.0+

### Voice Chatbot
- Python 3.8+
- Streamlit 1.28.0+
- SpeechRecognition 3.10.0+
- gTTS 2.5.0+
- audio-recorder-streamlit 0.0.8+
- Microphone and speakers

See [requirements.txt](requirements.txt) for full list.

## Documentation

- **Voice Chatbot Guide**: [VOICE_CHATBOT_README.md](VOICE_CHATBOT_README.md)
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)

## License

This is a demo project for Thames Water customer service automation. Feel free to modify and customize.