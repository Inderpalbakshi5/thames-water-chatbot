# pip install streamlit openai requests

import streamlit as st
import openai
import requests
import base64

# Set your OpenAI API key
openai.api_key = "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"
client = openai.OpenAI(api_key=openai.api_key)

# Define assistant behavior
system_prompt = """
You are a professional and polite virtual assistant for Thames Water, the UK's largest water and wastewater company.
You help customers with billing, account management, and operational issues like water supply, leaks, and service updates.

Always provide helpful, accurate, and courteous responses.
Do not provide or mention any phone numbers under any circumstances.
Instead, always direct users to the most relevant page on https://www.thameswater.co.uk/ for their issue.

Use these official links when appropriate:
- Moving home: https://www.thameswater.co.uk/help/account-and-billing/moving-home
- Report a leak: https://www.thameswater.co.uk/help/emergencies/report-a-leak
- No water or low pressure: https://www.thameswater.co.uk/help/emergencies/no-water-or-low-pressure
- Check your bill or account: https://www.thameswater.co.uk/my-account
- Payment help: https://www.thameswater.co.uk/help/account-and-billing/financial-support
- General help: https://www.thameswater.co.uk/help

If the user asks about something not listed, guide them to the homepage: https://www.thameswater.co.uk/
"""

# Function to analyze image using LLaVA
def analyze_image_with_llava(image_bytes, question):
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")
    response = requests.post(
        "https://llava.hf.space/run/predict",
        json={
            "data": [
                f"data:image/jpeg;base64,{image_b64}",
                question
            ]
        }
    )
    if response.status_code == 200:
        return response.json()["data"][0]
    else:
        return f"Error: {response.status_code} - {response.text}"

# Streamlit UI
st.set_page_config(page_title="Thames Water Assistant", page_icon="💧", layout="wide")

# Custom header with branding
st.markdown("""
    <div style='display: flex; align-items: center; gap: 1rem; background-color: #0072CE; padding: 1rem; border-radius: 8px;'>
        <img src='https://www.thameswater.co.uk/etc.clientlibs/thames-water/clientlibs/clientlib-site/resources/images/logo.svg' width='120'/>
        <h1 style='color: white; margin: 0;'>Thames Water Virtual Assistant</h1>
    </div>
    <br>
""", unsafe_allow_html=True)

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": system_prompt}]

# Sidebar for image upload
with st.sidebar:
    st.header("🖼️ Image Analysis")
    uploaded_image = st.file_uploader("Upload an image (e.g. bill, leak)", type=["jpg", "jpeg", "png"])
    image_question = st.text_input("Ask a question about the image")
    if uploaded_image and image_question:
        image_bytes = uploaded_image.read()
        with st.spinner("Analyzing image..."):
            result = analyze_image_with_llava(image_bytes, image_question)
        st.success("LLaVA says:")
        st.write(result)

# Chat input
user_input = st.chat_input("How can I help you today?")
if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=st.session_state.messages,
        temperature=0.5
    )
    reply = response.choices[0].message.content.strip()
    st.session_state.messages.append({"role": "assistant", "content": reply})

# Display chat history
for msg in st.session_state.messages[1:]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
