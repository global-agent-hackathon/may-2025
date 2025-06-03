
# 🔐 ZeroMesh  

**ZeroMesh** is a zero-trust security layer for agentic communication. It manages trust scores, access controls, and real-time alerts across a distributed ecosystem of agents, all visualized through a clean, interactive Streamlit dashboard 

Built using **Agno** for agent orchestration and **Mem0** for immutable audit logging 🧠📜

---

## System Architecture

![System arch](https://github.com/user-attachments/assets/2052daea-7f11-465b-9e59-193e9ce70f0c)


## 🤖 Agents at Work

ZeroMesh uses Agno-powered agents — each with a focused responsibility, working in sync under the zero-trust model.

### 🧠 Core Agents  
- **TrustAgent** – Calculates and keeps track of agent trust scores 📊  
- **AuditAgent** – Records all agent activity and system events using **Mem0** for tamper-proof logging  
- **PolicyAgent** – Enforces security rules and access control policies 🔐  

### 🩺 Monitoring Agents  
- **HealthMonitorAgent** – Keeps an eye on system metrics and resource usage 🖥️  
- **AlertAgent** – Flags suspicious activity and security anomalies in real-time 🚨  

All agents communicate securely through **Agno**, enabling fast and private coordination without assumptions of trust.

---

## 🌟 Key Features  

### 🧩 Agent Management  
- View real-time status: active/quarantined   🛑
- Visualize trust score history 📈  
- Classify by type (service, user, system)  
- Track agents by location 📍  
- Quarantine or reactivate with a click 🧼  

### 🛡️ Security Monitoring  
- Instant alerts with severity levels  
- Detect unauthorized access  
- Monitor policy violations  
- Trust score anomaly detection  
- System fault & error tracking  

### 📚 Audit Logging with Mem0  
- Immutable event logging with **Mem0** 🔐  
- Filter logs by event type and status  
- Timeline-based search  
- Track every user action and system change  
- Auditable by design — no tampering allowed 🧾  

### ⚙️ Config Panel  
- Set trust score thresholds  
- Alert routing preferences  
- Schedule automatic backups  
- Maintenance window settings  
- System health parameter tuning  

---

## 📊 Dashboard Overview  

Powered by Streamlit for smooth UX:  
- Live metrics and KPIs  
- Interactive visualizations  
- Fast filtering & search  
- Color-coded agent status  
- Fully responsive layout 📱💻

---

## 🚀 Quick Start Guide

### One-Time Setup
```bash
# Clone and set up an environment
git clone https://github.com/yourusername/zeromesh.git
cd zeromesh
python -m venv venv

# Activate venv (Choose your OS)
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install everything you need
pip install -r requirements.txt

### Environment Variables 🔑
Set up your .env file in the /core folder
```env
# Mem0 Configuration
MEM0_API_KEY=<your-api-key>
MEM0_ENDPOINT=https://api.mem0.ai/v1  # Default endpoint, can be changed

# Server Configuration
MCP_HOST=localhost
MCP_PORT=8000

# AZTP Security
AZTP_CERT_PATH=./certs/aztp.crt
AZTP_KEY_PATH=./certs/aztp.key

```

### Running ZeroMesh
```bash
# 1. Start everything with one command
python start.py

# OR start services individually:

# 2a. Start core services
python init_zeromesh.py

# 2b. Launch dashboard
streamlit run dashboard.py
```
Open your browser and go to: [http://localhost:8501](http://localhost:8501)

### Try Demo Mode 🎮
```bash
# Run full security demo
python -m core.demo.security_demo

# Or try with sample agents
python -m core.demo.agno_simulation
```

### Useful Commands
```bash
# View logs
tail -f logs/zeromesh.log

# Run tests
python -m pytest

# Clear dashboard cache
streamlit cache clear
```
--- 

## 🗂️ Project Structure  
```
zeromesh/
├── dashboard.py         # Main Streamlit app
├── requirements.txt     # Dependencies
├── core/                
│   ├── api/             # API routes
│   ├── services/        # Core agent logic
│   └── utils/           # Helper functions
└── README.md            # This file:)
```

---
## ⚙️ Configuration Options  

You can configure all key system parameters directly from the dashboard:  
- Trust score thresholds  
- Alert delivery methods (e.g., Slack, email, etc.)  
- Backup settings  
- Maintenance timing  
- Health metrics preferences  

---

## 🧠 Usage Scenarios  

1. **Monitor Overview**  
   - View system stats, alerts, and trust score trends  

2. **Manage Agents**  
   - Filter by status, type, and location  
   - Quarantine/reactivate agents with ease  
   - Check individual trust levels  

3. **Review Alerts**  
   - View alerts with severity tagging  
   - Investigate impacted agents and systems  

4. **Audit Logs**  
   - Search full activity history  
   - Validate data with Mem0-backed logs  
   - Filter by agent or action  

5. **Customize System Settings**  
   - Adjust thresholds, notification routes, backups, etc.  

---

## 🔒 Powered by Agno + Mem0  
- **Agno** enables secure, modular agent orchestration 🔄  
- **Mem0** ensures all logs are immutable and audit-ready 🪵  

ZeroMesh brings together trustless design + secure logging, so you can sleep better knowing your agents are behaving 😌💻

---

Made with 🖤 for devs building secure agentic systems.
