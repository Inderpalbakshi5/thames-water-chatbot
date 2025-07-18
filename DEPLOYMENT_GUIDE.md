# 🚀 Water Company Chatbot - Deployment Guide

## 🔍 **How to Check the Bot**

### **1. Run Tests First**
```bash
python3 test_chatbot.py
```
✅ This verifies the chatbot logic is working correctly.

### **2. Check Dependencies**
```bash
python3 -c "import streamlit; print('✅ Streamlit available')"
```

### **3. Verify Files**
Make sure these files exist:
- `water_company_chatbot.py` (main application)
- `requirements.txt` (dependencies)
- `README.md` (documentation)
- `run_chatbot.sh` (startup script)

## 🚀 **Deployment Options**

### **Option 1: Local Development (Easiest)**

#### **Quick Start:**
```bash
# Make script executable
chmod +x run_chatbot.sh

# Run the bot
./run_chatbot.sh
```

#### **Manual Start:**
```bash
# Install dependencies (if not done)
pip install -r requirements.txt

# Start the bot
streamlit run water_company_chatbot.py
```

**Access at:** `http://localhost:8501`

---

### **Option 2: Production Server Deployment**

#### **A. Using PM2 (Process Manager)**
```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'water-chatbot',
    script: 'streamlit',
    args: 'run water_company_chatbot.py --server.port 8501 --server.address 0.0.0.0',
    interpreter: 'python3',
    instances: 1,
    autorestart: true,
    watch: false,
    max_memory_restart: '1G'
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### **B. Using systemd (Linux)**
```bash
# Create service file
sudo tee /etc/systemd/system/water-chatbot.service << 'EOF'
[Unit]
Description=Water Company Chatbot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/path/to/your/chatbot
Environment=PATH=/home/ubuntu/.local/bin:$PATH
ExecStart=/usr/bin/python3 -m streamlit run water_company_chatbot.py --server.port 8501 --server.address 0.0.0.0
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable water-chatbot
sudo systemctl start water-chatbot
sudo systemctl status water-chatbot
```

#### **C. Using Docker**
```bash
# Create Dockerfile
cat > Dockerfile << 'EOF'
FROM python:3.9-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

ENTRYPOINT ["streamlit", "run", "water_company_chatbot.py", "--server.port=8501", "--server.address=0.0.0.0"]
EOF

# Build and run
docker build -t water-chatbot .
docker run -d -p 8501:8501 --name water-chatbot water-chatbot
```

---

### **Option 3: Cloud Platform Deployment**

#### **A. Streamlit Cloud (Free)**
1. Push code to GitHub repository
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your GitHub account
4. Deploy from your repository
5. Select `water_company_chatbot.py` as main file

#### **B. Heroku**
```bash
# Install Heroku CLI, then:
echo "web: streamlit run water_company_chatbot.py --server.port \$PORT --server.address 0.0.0.0" > Procfile

# Add to requirements.txt
echo "streamlit>=1.28.0" > requirements.txt

# Deploy
heroku create your-water-chatbot
git add .
git commit -m "Deploy water chatbot"
git push heroku main
```

#### **C. AWS EC2**
```bash
# Launch EC2 instance (Ubuntu)
# SSH into instance, then:

# Install Python and dependencies
sudo apt update
sudo apt install python3-pip -y

# Clone your repository
git clone [your-repo-url]
cd [your-repo-name]

# Install dependencies
pip3 install -r requirements.txt

# Start with nohup
nohup python3 -m streamlit run water_company_chatbot.py --server.port 8501 --server.address 0.0.0.0 &

# Configure security group to allow port 8501
```

#### **D. Google Cloud Run**
```bash
# Create cloudbuild.yaml
cat > cloudbuild.yaml << 'EOF'
steps:
- name: 'gcr.io/cloud-builders/docker'
  args: ['build', '-t', 'gcr.io/$PROJECT_ID/water-chatbot', '.']
- name: 'gcr.io/cloud-builders/docker'
  args: ['push', 'gcr.io/$PROJECT_ID/water-chatbot']
- name: 'gcr.io/cloud-builders/gcloud'
  args: ['run', 'deploy', 'water-chatbot', '--image', 'gcr.io/$PROJECT_ID/water-chatbot', '--platform', 'managed', '--region', 'us-central1', '--allow-unauthenticated']
EOF

# Deploy
gcloud builds submit --config cloudbuild.yaml
```

---

## 🔧 **Configuration Options**

### **Environment Variables**
```bash
# Custom port
export STREAMLIT_SERVER_PORT=8080

# Custom address
export STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Disable telemetry
export STREAMLIT_BROWSER_GATHER_USAGE_STATS=false
```

### **Custom Configuration**
Create `.streamlit/config.toml`:
```toml
[server]
port = 8501
address = "0.0.0.0"
headless = true

[browser]
gatherUsageStats = false
```

---

## 🛡️ **Security Considerations**

### **For Production Deployment:**
1. **Use HTTPS**: Set up SSL certificate
2. **Firewall**: Only allow necessary ports
3. **Authentication**: Add login if needed
4. **Rate Limiting**: Implement request limits
5. **Monitoring**: Set up health checks

### **Nginx Reverse Proxy Example:**
```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 📊 **Monitoring & Maintenance**

### **Health Checks**
```bash
# Check if service is running
curl http://localhost:8501/_stcore/health

# Monitor logs
tail -f /var/log/water-chatbot.log

# Check process
ps aux | grep streamlit
```

### **Auto-restart Script**
```bash
#!/bin/bash
# auto-restart.sh
while true; do
    if ! pgrep -f "streamlit.*water_company_chatbot.py" > /dev/null; then
        echo "Restarting chatbot..."
        cd /path/to/chatbot
        nohup streamlit run water_company_chatbot.py &
    fi
    sleep 30
done
```

---

## 🎯 **Quick Troubleshooting**

### **Common Issues:**
1. **Port already in use**: `lsof -i :8501` and kill process
2. **Permission denied**: Check file permissions and user
3. **Module not found**: Verify Python path and virtual environment
4. **Browser doesn't open**: Check firewall and server address

### **Logs Location:**
- **Streamlit logs**: `~/.streamlit/logs/`
- **System logs**: `/var/log/syslog`
- **Custom logs**: Check your deployment method

---

## ✅ **Deployment Checklist**

- [ ] Tests pass (`python3 test_chatbot.py`)
- [ ] Dependencies installed
- [ ] Firewall configured (port 8501)
- [ ] SSL certificate (for production)
- [ ] Monitoring set up
- [ ] Backup strategy
- [ ] Auto-restart configured
- [ ] Health checks working
- [ ] Documentation updated

---

## 📞 **Support**

If you encounter issues:
1. Check the logs
2. Verify all dependencies are installed
3. Ensure the correct Python version (3.7+)
4. Check firewall settings
5. Review the configuration files

**Remember**: The chatbot is designed to be simple and secure with no external API dependencies, making deployment straightforward!