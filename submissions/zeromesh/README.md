
# 🔐 ZeroMesh  

**ZeroMesh** is a zero-trust security layer for agentic communication. It manages trust scores, access controls, and real-time alerts across a distributed ecosystem of agents, all visualized through a clean, interactive Streamlit dashboard 

Built using **Agno** for agent orchestration and **Mem0** for immutable audit logging 🧠📜

---

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
└── README.md            # This file:)
```

---

## 📁 Environment Variables

Before running the dashboard, make sure to create a `.env` file in the `/core ` directory of the project with the following fields:

```bash
# MEM0 API
MEM0_API_KEY=<your-api-key>
MEM0_ENDPOINT=https://api.mem0.ai/v1
MEM0_COLLECTION=<collection-name>
MEM0_BATCH_SIZE=50
MEM0_FLUSH_INTERVAL=60

# OpenAI API
OPENAI_API_KEY=<your-api-key>

# Server Configuration
MCP_HOST=localhost
MCP_PORT=8000

# Security Configuration
AZTP_CERT_PATH=./certs/aztp.crt
AZTP_KEY_PATH=./certs/aztp.key
```

Make sure to keep your API keys safe and do not commit the `.env` file to version control. 🚫🔑


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

## 🤝 Contributions

We welcome contributions from developers passionate about security, agents, and zero-trust systems! Whether you're fixing a bug, suggesting an enhancement, or building a new feature — we’d love your help.

### 🛠️ How to Contribute

1. **Fork the repo** and create your branch:  
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write clear, well-documented code**  
   - Follow existing naming conventions  
   - Keep functions modular and readable  
   - Add docstrings and comments where needed  

3. **Add tests if applicable**  
   - Ensure your changes don't break existing functionality  
   - Tests are located in `core/tests/`

4. **Commit with meaningful messages**  
   ```bash
   git commit -m "Add: trust score normalization method"
   ```

5. **Push to your fork and open a Pull Request**  
   - Describe what your PR does and why it matters  
   - Link to related issues (if any)

---

Made with 🖤 for devs building secure agentic systems.
