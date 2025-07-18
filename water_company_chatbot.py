import streamlit as st
import re
import json
from datetime import datetime, timedelta
import random

# Configure page
st.set_page_config(
    page_title="AquaCorp Assistant", 
    page_icon="💧", 
    layout="wide"
)

# Knowledge base for the water company
WATER_COMPANY_KB = {
    "services": {
        "water_supply": "We provide clean, safe drinking water to over 2 million customers across the region.",
        "wastewater": "Our wastewater treatment facilities process over 500 million gallons daily.",
        "emergency_repairs": "24/7 emergency repair service for water main breaks and urgent issues.",
        "water_quality": "Regular testing ensures your water meets all safety standards.",
        "meter_reading": "Smart meters provide accurate billing and help detect leaks early."
    },
    "billing": {
        "payment_methods": "Pay online, by phone, automatic debit, or mail. Set up autopay for convenience.",
        "billing_cycle": "Bills are sent monthly. Your billing period runs from the 1st to the last day of each month.",
        "late_fees": "Late fees of $25 apply to overdue accounts. Contact us if you need payment assistance.",
        "estimated_bills": "If we can't read your meter, we'll estimate based on previous usage.",
        "budget_billing": "Spread costs evenly throughout the year with our budget billing program."
    },
    "support": {
        "hours": "Customer service: Monday-Friday 7AM-7PM, Saturday 8AM-5PM",
        "emergency": "Emergency line available 24/7 for water outages and major leaks",
        "online_account": "Manage your account online: view bills, make payments, report issues",
        "mobile_app": "Download our mobile app for quick access to your account and services"
    },
    "common_issues": {
        "no_water": "Check if neighbors have water. If not, there may be a main break. Report immediately.",
        "low_pressure": "Clean faucet aerators, check for leaks, or it could be a system issue.",
        "discolored_water": "Run cold water for 5-10 minutes. If it persists, contact us immediately.",
        "high_bill": "Check for leaks, unusual usage, or meter reading errors. We can investigate.",
        "leak_detection": "Look for wet spots, running water sounds, or unexpectedly high bills."
    }
}

# Response patterns and keywords
INTENT_PATTERNS = {
    "billing": ["bill", "payment", "cost", "charge", "fee", "money", "pay", "account", "balance"],
    "service": ["water", "service", "supply", "pressure", "outage", "quality"],
    "emergency": ["emergency", "leak", "break", "no water", "urgent", "flooding"],
    "support": ["help", "contact", "phone", "hours", "customer service"],
    "account": ["account", "login", "password", "online", "app", "register"]
}

class WaterCompanyChatbot:
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
        if intent == "emergency" or any(word in user_input_lower for word in ["emergency", "urgent", "flooding", "burst"]):
            return """🚨 **EMERGENCY RESPONSE**
            
If this is a water emergency:
- **Water main break or flooding**: Call our 24/7 emergency line immediately
- **No water service**: Check if neighbors are affected, then report the outage
- **Gas smell near water lines**: Leave the area and call emergency services

For non-emergencies, I can help you with billing, service questions, or account management."""

        # Billing related
        elif intent == "billing":
            if "payment" in user_input_lower or "pay" in user_input_lower:
                return f"""💳 **Payment Information**
                
{WATER_COMPANY_KB['billing']['payment_methods']}

**Quick payment options:**
- Online: Log into your account portal
- Phone: Call our automated payment line
- Auto-pay: Never miss a payment again
- Mobile app: Pay on the go

{WATER_COMPANY_KB['billing']['billing_cycle']}"""
            
            elif "high" in user_input_lower or "expensive" in user_input_lower:
                return f"""📊 **High Bill Assistance**
                
{WATER_COMPANY_KB['common_issues']['high_bill']}

**Common causes of high bills:**
- Hidden leaks (toilets, pipes, faucets)
- Seasonal usage changes
- Pool filling or landscaping
- Meter reading errors

**Next steps:**
1. Check your property for leaks
2. Compare to previous bills
3. Contact us for a usage analysis"""
            
            else:
                return f"""💰 **Billing Information**
                
{WATER_COMPANY_KB['billing']['billing_cycle']}
{WATER_COMPANY_KB['billing']['budget_billing']}

**Need help with your bill?**
- View current balance and payment history online
- Set up payment plans if needed
- Learn about assistance programs"""

        # Service related
        elif intent == "service":
            if "no water" in user_input_lower or "outage" in user_input_lower:
                return f"""🚰 **Water Outage Information**
                
{WATER_COMPANY_KB['common_issues']['no_water']}

**Steps to take:**
1. Check if neighbors have water
2. Look for notices about planned maintenance
3. Report the outage if it's unexpected
4. Keep emergency water supplies handy

**Estimated restoration:** Most outages are resolved within 4-6 hours."""
            
            elif "pressure" in user_input_lower or "low" in user_input_lower:
                return f"""🔧 **Low Water Pressure**
                
{WATER_COMPANY_KB['common_issues']['low_pressure']}

**Try these steps:**
1. Clean faucet aerators and showerheads
2. Check if problem affects hot, cold, or both
3. See if neighbors have similar issues
4. Look for visible leaks in your property

If problems persist, we can test system pressure in your area."""
            
            elif "quality" in user_input_lower or "taste" in user_input_lower or "color" in user_input_lower:
                return f"""🧪 **Water Quality**
                
{WATER_COMPANY_KB['services']['water_quality']}
{WATER_COMPANY_KB['common_issues']['discolored_water']}

**Water quality concerns:**
- Discolored water: Usually from pipe disturbances
- Taste/odor: Often from chlorine (safe but treatable)
- Particles: May indicate plumbing issues

**Free water testing available** - Contact us to schedule."""
            
            else:
                return f"""🏢 **Our Services**
                
{WATER_COMPANY_KB['services']['water_supply']}
{WATER_COMPANY_KB['services']['wastewater']}

**Additional services:**
- {WATER_COMPANY_KB['services']['emergency_repairs']}
- {WATER_COMPANY_KB['services']['meter_reading']}

How can I help you with your water service today?"""

        # Support and contact
        elif intent == "support":
            return f"""📞 **Customer Support**
            
{WATER_COMPANY_KB['support']['hours']}
{WATER_COMPANY_KB['support']['emergency']}

**Contact options:**
- {WATER_COMPANY_KB['support']['online_account']}
- {WATER_COMPANY_KB['support']['mobile_app']}
- Live chat available during business hours
- Email support with 24-hour response time"""

        # Account management
        elif intent == "account":
            return f"""👤 **Account Management**
            
{WATER_COMPANY_KB['support']['online_account']}
{WATER_COMPANY_KB['support']['mobile_app']}

**Online account features:**
- View and pay bills
- Report service issues
- Track water usage
- Update contact information
- Set up account alerts

**Need help logging in?** Use the 'Forgot Password' link or contact customer service."""

        # General response
        else:
            return """👋 **Welcome to AquaCorp Customer Service**
            
I'm here to help you with:
- 💳 **Billing and payments**
- 🚰 **Water service issues**  
- 🚨 **Emergency reporting**
- 👤 **Account management**
- 📞 **Customer support**

What can I help you with today? Try asking about:
- "How do I pay my bill?"
- "I have no water pressure"
- "My water bill is high"
- "How do I report a leak?"
- "Customer service hours" """

# Initialize chatbot
if 'chatbot' not in st.session_state:
    st.session_state.chatbot = WaterCompanyChatbot()
if 'messages' not in st.session_state:
    st.session_state.messages = []

# Header
st.markdown("""
    <div style='background: linear-gradient(90deg, #1e3c72 0%, #2a5298 100%); 
                padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
        <div style='display: flex; align-items: center; gap: 1rem;'>
            <div style='font-size: 3rem;'>💧</div>
            <div>
                <h1 style='color: white; margin: 0; font-size: 2.5rem;'>AquaCorp</h1>
                <p style='color: #87CEEB; margin: 0; font-size: 1.2rem;'>Virtual Customer Assistant</p>
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
    
    st.markdown("---")
    st.header("📊 Service Status")
    st.success("🟢 Water Supply: Normal")
    st.success("🟢 System Pressure: Normal") 
    st.info("🔧 Planned Maintenance: None scheduled")
    
    st.markdown("---")
    st.markdown("""
    **Emergency?** 
    🚨 Call 911 for gas leaks or flooding
    
    **24/7 Water Emergency Line:**
    📞 1-800-WATER-NOW
    """)

# Main chat interface
st.header("💬 Chat with our Assistant")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if prompt := st.chat_input("Ask about billing, water service, or account management..."):
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
        <p>AquaCorp - Serving the community with reliable water services since 1995</p>
        <p>This is a demo chatbot. For real emergencies, contact emergency services.</p>
    </div>
""", unsafe_allow_html=True)