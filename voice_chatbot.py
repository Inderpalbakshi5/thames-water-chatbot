import streamlit as st
import re
import json
from datetime import datetime, timedelta
import random
import base64
import io
import os
from pathlib import Path

# Configure page
st.set_page_config(
    page_title="Thames Water Voice Assistant",
    page_icon="💧",
    layout="wide"
)

# Knowledge base for Thames Water
THAMES_WATER_KB = {
    "services": {
        "water_supply": "Thames Water provides clean, safe drinking water to 15 million customers across London and the Thames Valley.",
        "wastewater": "We treat over 4.4 billion litres of wastewater every day across our 350 sewage treatment works.",
        "emergency_repairs": "24/7 emergency repair service for water main breaks and urgent issues. Call 0800 714 614.",
        "water_quality": "We carry out over 500,000 tests every year to ensure your water meets strict safety standards.",
        "meter_reading": "Smart meters provide accurate billing and help detect leaks early, saving you money."
    },
    "billing": {
        "payment_methods": "Pay online at thameswater.co.uk, by phone on 0800 980 8800, Direct Debit, or at PayPoint stores.",
        "billing_cycle": "Bills are sent every six months. You can switch to monthly payments with WaterSure Plus.",
        "late_fees": "We understand financial difficulties. Contact us on 0800 009 3652 for payment support and assistance schemes.",
        "estimated_bills": "If we can't read your meter, we'll estimate based on your previous usage.",
        "budget_billing": "WaterSure Plus spreads your costs evenly throughout the year with monthly payments."
    },
    "support": {
        "hours": "Customer service: Monday-Friday 8AM-8PM, Saturday 8AM-6PM",
        "emergency": "Emergency line available 24/7 on 0800 714 614 for water outages and major leaks",
        "online_account": "Manage your account online at thameswater.co.uk: view bills, make payments, report issues",
        "mobile_app": "Download the MyThamesWater app for quick access to your account and services"
    },
    "common_issues": {
        "no_water": "Check if neighbors have water. If not, there may be a main break. Report on 0800 714 614.",
        "low_pressure": "Clean faucet aerators, check for leaks, or it could be a system issue. We can investigate.",
        "discolored_water": "Run cold water for 5-10 minutes. If it persists, call us on 0800 316 9800.",
        "high_bill": "Check for leaks, unusual usage, or meter reading errors. We offer free leak detection.",
        "leak_detection": "Look for wet spots, running water sounds, or unexpectedly high bills. Report leaks on 0800 714 614."
    },
    "thames_specific": {
        "hardness": "Thames Water supplies hard water to most areas as it comes from chalk aquifers. This is safe to drink.",
        "lead_pipes": "We've replaced most lead pipes in our network. Check if your property has lead pipes and we can help.",
        "hosepipe_bans": "Check thameswater.co.uk for current water restrictions and drought status.",
        "sewer_flooding": "Report internal or external sewer flooding immediately on 0800 316 9800."
    }
}

# Response patterns and keywords
INTENT_PATTERNS = {
    "billing": ["bill", "payment", "cost", "charge", "fee", "money", "pay", "account", "balance", "direct debit"],
    "service": ["water", "service", "supply", "pressure", "outage", "quality", "hard water", "hardness"],
    "emergency": ["emergency", "leak", "break", "no water", "urgent", "flooding", "burst"],
    "support": ["help", "contact", "phone", "hours", "customer service", "speak to someone"],
    "account": ["account", "login", "password", "online", "app", "register", "myaccount"],
    "meter": ["meter", "reading", "smart meter", "usage", "consumption"],
    "leak": ["leak", "dripping", "waste", "running water"]
}

class ThamesWaterVoiceChatbot:
    def __init__(self):
        self.conversation_history = []

    def detect_intent(self, user_input):
        user_input_lower = user_input.lower()
        intent_scores = {}

        for intent, keywords in INTENT_PATTERNS.items():
            score = sum(1 for keyword in keywords if keyword in user_input_lower)
            if score > 0:
                intent_scores[intent] = score

        if intent_scores:
            return max(intent_scores, key=intent_scores.get)
        return "general"

    def get_response(self, user_input):
        intent = self.detect_intent(user_input)
        user_input_lower = user_input.lower()

        # Emergency responses
        if intent == "emergency" or any(word in user_input_lower for word in ["emergency", "urgent", "flooding", "burst", "no water"]):
            return """🚨 EMERGENCY RESPONSE

If this is a water emergency:
- Water main break or flooding: Call 0800 714 614 immediately (24/7)
- No water service: Check if neighbors are affected, then call our emergency line
- Sewer flooding: Call 0800 316 9800 right away
- Gas smell near water lines: Leave the area and call National Gas Emergency on 0800 111 999

For non-emergencies, I can help you with billing, service questions, or account management."""

        # Leak related
        elif intent == "leak" or "leak" in user_input_lower:
            return f"""💧 LEAK INFORMATION

{THAMES_WATER_KB['common_issues']['leak_detection']}

TYPES OF LEAKS:
• Internal leaks (your property): You're responsible for repairs
• External leaks (street/pavement): Thames Water responsibility
• Supply pipe leaks: May be shared responsibility

REPORT A LEAK:
• Street/road leaks: 0800 714 614 (24/7)
• Free leak detection service available
• We can help identify if leak is on your property or our network

Check your stop tap location and how to turn off water in emergencies."""

        # Meter related
        elif intent == "meter":
            return f"""📊 METER INFORMATION

{THAMES_WATER_KB['services']['meter_reading']}

METER SERVICES:
• Submit meter readings online at thameswater.co.uk
• Get a free water meter installed to potentially save money
• Smart meters available - automatic readings, no estimates
• Check your daily usage through MyThamesWater app

FINDING YOUR METER:
• Usually under kitchen sink, in utility room, or outside
• Need help locating? We can arrange a visit

Most customers save money by switching to a meter."""

        # Billing related
        elif intent == "billing":
            if "payment" in user_input_lower or "pay" in user_input_lower:
                return f"""💳 PAYMENT INFORMATION

{THAMES_WATER_KB['billing']['payment_methods']}

QUICK PAYMENT OPTIONS:
• Online: thameswater.co.uk/my-account
• Phone: 0800 980 8800 (automated 24/7)
• Direct Debit: Set up online or call us
• PayPoint: Pay cash at local shops
• Mobile app: MyThamesWater app

{THAMES_WATER_KB['billing']['billing_cycle']}

STRUGGLING TO PAY?
Contact our payment support team: 0800 009 3652"""

            elif "high" in user_input_lower or "expensive" in user_input_lower:
                return f"""📊 HIGH BILL ASSISTANCE

{THAMES_WATER_KB['common_issues']['high_bill']}

COMMON CAUSES OF HIGH BILLS:
• Hidden leaks (toilets, pipes, faucets)
• Seasonal usage changes
• Garden watering or pool filling
• More people in household
• Meter reading errors

NEXT STEPS:
1. Check for leaks - we offer FREE leak detection
2. Submit a meter reading to ensure accuracy
3. Compare to previous bills
4. Contact us for a usage analysis

HELP AVAILABLE:
• WaterSure scheme for vulnerable customers
• Payment plans and support: 0800 009 3652
• Water efficiency advice to reduce usage"""

            else:
                return f"""💰 BILLING INFORMATION

{THAMES_WATER_KB['billing']['billing_cycle']}
{THAMES_WATER_KB['billing']['budget_billing']}

MANAGING YOUR BILL:
• View bills and payment history online
• Set up payment plans if needed
• WaterSure scheme for eligible customers
• Payment holidays available in hardship

CONTACT BILLING TEAM:
• Phone: 0800 980 8800
• Online: thameswater.co.uk/help
• Social Tariff enquiries: 0800 009 3652"""

        # Service related
        elif intent == "service":
            if "no water" in user_input_lower or "outage" in user_input_lower:
                return f"""🚰 WATER OUTAGE INFORMATION

{THAMES_WATER_KB['common_issues']['no_water']}

STEPS TO TAKE:
1. Check if neighbors have water
2. Look for notices at thameswater.co.uk/outages
3. Report unexpected outages: 0800 714 614
4. Keep emergency water supplies handy
5. Follow us on Twitter @thameswater for updates

PLANNED WORK:
• Check live outage map online
• We notify customers in advance
• Usually restored within 4-6 hours

COMPENSATION:
You may be eligible for compensation if we don't restore supply on time."""

            elif "pressure" in user_input_lower or "low" in user_input_lower:
                return f"""🔧 LOW WATER PRESSURE

{THAMES_WATER_KB['common_issues']['low_pressure']}

TRY THESE STEPS:
1. Clean faucet aerators and showerheads
2. Check if problem affects hot, cold, or both
3. See if neighbors have similar issues
4. Look for visible leaks on your property
5. Check your internal stop tap is fully open

THAMES WATER CAN HELP:
• Test system pressure in your area
• Investigate if it's a network issue
• Arrange engineer visit if needed

Call: 0800 980 8800 to report persistent low pressure."""

            elif "quality" in user_input_lower or "taste" in user_input_lower or "color" in user_input_lower or "discolored" in user_input_lower:
                return f"""🧪 WATER QUALITY

{THAMES_WATER_KB['services']['water_quality']}
{THAMES_WATER_KB['common_issues']['discolored_water']}

WATER QUALITY CONCERNS:
• Discolored water: Usually from pipe disturbances - run cold tap
• Taste/odor: Often from chlorine (safe) or pipes
• Particles: May indicate plumbing issues
• White/cloudy: Usually tiny air bubbles (harmless)

HARD WATER:
{THAMES_WATER_KB['thames_specific']['hardness']}

REPORT QUALITY ISSUES:
Call 0800 316 9800 for water quality concerns
FREE WATER TESTING available

We take water quality very seriously."""

            else:
                return f"""🏢 THAMES WATER SERVICES

{THAMES_WATER_KB['services']['water_supply']}
{THAMES_WATER_KB['services']['wastewater']}

ADDITIONAL SERVICES:
• {THAMES_WATER_KB['services']['emergency_repairs']}
• {THAMES_WATER_KB['services']['meter_reading']}
• Free water saving devices
• Education visits and tours

How can I help you with your water service today?"""

        # Support and contact
        elif intent == "support" or "hours" in user_input_lower or "contact" in user_input_lower or "enquiries" in user_input_lower:
            return f"""📞 THAMES WATER CUSTOMER SUPPORT

{THAMES_WATER_KB['support']['hours']}
{THAMES_WATER_KB['support']['emergency']}

CONTACT OPTIONS:
• General enquiries: 0800 980 8800
• {THAMES_WATER_KB['support']['online_account']}
• {THAMES_WATER_KB['support']['mobile_app']}
• Twitter: @thameswater
• Email: customer.services@thameswater.co.uk

SPECIALIST TEAMS:
• Payment support: 0800 009 3652
• Water quality: 0800 316 9800
• Developer services: 0800 009 3921
• Wholesale: 0800 634 444"""

        # Account management
        elif intent == "account":
            return f"""👤 ACCOUNT MANAGEMENT

{THAMES_WATER_KB['support']['online_account']}
{THAMES_WATER_KB['support']['mobile_app']}

ONLINE ACCOUNT FEATURES:
• View and pay bills
• Submit meter readings
• Report service issues
• Track water usage
• Update contact information
• Set up Direct Debit
• View payment history
• Download bills

REGISTER ONLINE:
Visit thameswater.co.uk and click 'Register' - you'll need:
• Your account number (on your bill)
• Postcode

NEED HELP LOGGING IN?
Use 'Forgot Password' or call 0800 980 8800"""

        # General response
        else:
            return """👋 WELCOME TO THAMES WATER VOICE ASSISTANT

I'm here to help you with:
💳 BILLING AND PAYMENTS
🚰 WATER SERVICE ISSUES
🚨 EMERGENCY REPORTING
👤 ACCOUNT MANAGEMENT
📞 CUSTOMER SUPPORT

WHAT CAN I HELP WITH?
Try asking about:
• "How do I pay my bill?"
• "I have low water pressure"
• "My water bill is high"
• "How do I report a leak?"
• "What are your contact hours?"

You can type or use voice input to speak with me!"""

# Initialize chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = ThamesWaterVoiceChatbot()
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Custom CSS for Thames Water branding
st.markdown("""
    <style>
    .thames-header {
        background: linear-gradient(135deg, #003087 0%, #00A9E0 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .thames-title {
        color: white;
        margin: 0;
        font-size: 2.5rem;
        font-weight: bold;
    }
    .thames-subtitle {
        color: #87CEEB;
        margin: 0;
        font-size: 1.2rem;
    }
    .voice-button {
        background-color: #00A9E0;
        color: white;
        padding: 1rem 2rem;
        border-radius: 50px;
        border: none;
        font-size: 1.1rem;
        cursor: pointer;
        transition: all 0.3s;
    }
    .voice-button:hover {
        background-color: #003087;
        transform: scale(1.05);
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
    <div class='thames-header'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>💧</div>
            <div>
                <h1 class='thames-title'>Thames Water</h1>
                <p class='thames-subtitle'>Voice-Enabled Customer Assistant</p>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Sidebar with quick actions
with st.sidebar:
    st.header("🔧 Quick Actions")

    if st.button("💳 Check Bill Status"):
        st.session_state.messages.append({"role": "user", "content": "How can I check my bill?"})
        response = st.session_state.chatbot.get_response("How can I check my bill?")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("🚰 Report Water Issue"):
        st.session_state.messages.append({"role": "user", "content": "I need to report a water problem"})
        response = st.session_state.chatbot.get_response("I need to report a water problem")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("📞 Contact Information"):
        st.session_state.messages.append({"role": "user", "content": "How can I contact customer service?"})
        response = st.session_state.chatbot.get_response("How can I contact customer service?")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    if st.button("💧 Report a Leak"):
        st.session_state.messages.append({"role": "user", "content": "How do I report a leak?"})
        response = st.session_state.chatbot.get_response("How do I report a leak?")
        st.session_state.messages.append({"role": "assistant", "content": response})
        st.rerun()

    st.markdown("---")
    st.header("📊 Service Status")
    st.success("🟢 Water Supply: Normal")
    st.success("🟢 System Pressure: Normal")
    st.info("🔧 Check live outage map online")

    st.markdown("---")
    st.markdown("""
    **Emergency Numbers:**

    🚨 **Water Emergency (24/7)**
    📞 0800 714 614

    🚽 **Sewer Flooding**
    📞 0800 316 9800

    ⚠️ **Gas Emergency**
    📞 0800 111 999

    **General Enquiries:**
    📞 0800 980 8800
    """)

# Main chat interface
st.header("💬 Voice & Text Chat")

# Voice Input Section
col1, col2 = st.columns([3, 1])
with col1:
    st.info("🎤 **Voice Input Available**: Use the audio recorder below to speak your question, or type in the chat box!")

# Audio recorder component (using streamlit-audio-recorder)
try:
    from audio_recorder_streamlit import audio_recorder

    st.markdown("### 🎤 Record Your Question")
    audio_bytes = audio_recorder(
        text="Click to record",
        recording_color="#e74c3c",
        neutral_color="#00A9E0",
        icon_size="3x",
        pause_threshold=2.0,
    )

    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")

        # Process audio
        if st.button("🔄 Process Voice Input", key="process_audio"):
            with st.spinner("Processing your voice input..."):
                try:
                    import speech_recognition as sr

                    # Save audio bytes to file
                    audio_file = io.BytesIO(audio_bytes)

                    # Convert to speech
                    recognizer = sr.Recognizer()

                    # Try to recognize speech
                    try:
                        with sr.AudioFile(audio_file) as source:
                            audio_data = recognizer.record(source)
                            text = recognizer.recognize_google(audio_data)

                            st.success(f"You said: {text}")

                            # Add to chat
                            st.session_state.messages.append({"role": "user", "content": text})
                            response = st.session_state.chatbot.get_response(text)
                            st.session_state.messages.append({"role": "assistant", "content": response})

                            st.rerun()

                    except sr.UnknownValueError:
                        st.error("Sorry, I couldn't understand the audio. Please try again or type your question.")
                    except sr.RequestError:
                        st.error("Voice recognition service is unavailable. Please type your question instead.")

                except ImportError:
                    st.warning("Voice recognition not available. Install speech_recognition library: pip install SpeechRecognition")
                except Exception as e:
                    st.error(f"Error processing audio: {str(e)}")

except ImportError:
    st.info("🎤 **Voice Input**: Install audio-recorder-streamlit for voice input: `pip install audio-recorder-streamlit`")
    st.markdown("For now, you can type your questions below!")

st.markdown("---")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Add text-to-speech for assistant messages
        if message["role"] == "assistant":
            try:
                from gtts import gTTS
                import tempfile

                # Create unique key for each message
                message_hash = hash(message["content"])

                if st.button(f"🔊 Listen to Response", key=f"tts_{message_hash}"):
                    with st.spinner("Generating speech..."):
                        try:
                            # Clean text for TTS (remove emojis and special formatting)
                            clean_text = re.sub(r'[^\w\s.,!?;:-]', '', message["content"])
                            clean_text = re.sub(r'\*+', '', clean_text)

                            # Generate speech
                            tts = gTTS(text=clean_text, lang='en', slow=False)

                            # Save to temporary file
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.mp3') as fp:
                                tts.save(fp.name)

                                # Read and play audio
                                with open(fp.name, 'rb') as audio_file:
                                    audio_bytes = audio_file.read()
                                    st.audio(audio_bytes, format='audio/mp3')

                                # Clean up temp file
                                os.unlink(fp.name)

                        except Exception as e:
                            st.error(f"Error generating speech: {str(e)}")

            except ImportError:
                pass  # TTS not available

# Chat input
if prompt := st.chat_input("Ask about billing, water service, leaks, or account management..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chatbot.get_response(prompt)
            st.markdown(response)

    # Add assistant response
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer
st.markdown("---")
st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p><strong>Thames Water</strong> - Serving London and the Thames Valley</p>
        <p>💧 15 million customers | 🏢 350 treatment works | 🔬 500,000+ quality tests/year</p>
        <p style='font-size: 0.9rem; color: #999;'>
            This is an AI-powered assistant. For emergencies, always call our emergency line.<br>
            Visit <a href='https://www.thameswater.co.uk' target='_blank'>thameswater.co.uk</a> for more information.
        </p>
    </div>
""", unsafe_allow_html=True)
