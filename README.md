# AquaCorp Water Company Chatbot 💧

A simple, interactive chatbot for a water utility company built with Streamlit. This chatbot helps customers with common inquiries about billing, water services, emergencies, and account management.

## Features

- **Smart Intent Detection**: Automatically understands customer queries and provides relevant responses
- **Emergency Response**: Special handling for urgent water-related issues
- **Billing Support**: Help with payments, high bills, and billing cycles  
- **Service Issues**: Assistance with water pressure, outages, and quality concerns
- **Account Management**: Information about online accounts and mobile app
- **Quick Actions**: One-click buttons for common tasks
- **Service Status**: Real-time display of system status
- **Modern UI**: Clean, professional interface with water company branding

## Installation

1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. Run the chatbot:
   ```bash
   streamlit run water_company_chatbot.py
   ```

2. Open your web browser and go to `http://localhost:8501`

3. Start chatting with the assistant! Try asking:
   - "How do I pay my bill?"
   - "I have no water pressure"
   - "My water bill is high"
   - "How do I report a leak?"
   - "Customer service hours"

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

## Requirements

- Python 3.7+
- Streamlit 1.28.0+

## License

This is a demo project. Feel free to modify and use for your water utility company's needs.