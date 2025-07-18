#!/bin/bash

# Add the local bin directory to PATH to access streamlit
export PATH="/home/ubuntu/.local/bin:$PATH"

echo "🚀 Starting AquaCorp Water Company Chatbot..."
echo "💧 The chatbot will be available at http://localhost:8501"
echo "🔧 Press Ctrl+C to stop the server"
echo ""

# Run the chatbot
python3 -m streamlit run water_company_chatbot.py --server.port 8501 --server.address 0.0.0.0