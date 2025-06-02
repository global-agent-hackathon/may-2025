
# 🔐 ZeroMesh  

**ZeroMesh** is a zero-trust security layer for agentic communication. It manages trust scores, access controls, and real-time alerts across a distributed ecosystem of agents — all visualized through a clean, interactive Streamlit dashboard 🎛️

Built using **Agno** for agent orchestration and **Mem0** for immutable audit logging 🧠📜

---

## 🤖 Agents at Work

ZeroMesh uses Agno-powered agents — each with a focused responsibility — working in sync under the zero-trust model.

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
- View real-time status: active / quarantined  
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

## 🧪 Setup Guide  

### ✅ Prerequisites  
- Python 3.9+  
- pip (Python package installer)

### 🚀 Installation Steps  
```bash
git clone https://github.com/yourusername/zeromesh.git
cd zeromesh
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt
streamlit run dashboard.py
```

Open your browser and go to: [http://localhost:8501](http://localhost:8501)

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
└── README.md            # This file!
```

---

## ⚙️ Configuration Options  

You can configure all key system parameters directly from the dashboard:  
- Trust score thresholds  
- Alert delivery methods (Slack/email/etc.)  
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
