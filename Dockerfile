FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY water_company_chatbot.py .
COPY README.md .

# Create streamlit config directory
RUN mkdir -p ~/.streamlit

# Create streamlit config file
RUN echo '\
[server]\n\
port = 8501\n\
address = "0.0.0.0"\n\
headless = true\n\
\n\
[browser]\n\
gatherUsageStats = false\n\
' > ~/.streamlit/config.toml

# Expose the port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run the application
ENTRYPOINT ["streamlit", "run", "water_company_chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]