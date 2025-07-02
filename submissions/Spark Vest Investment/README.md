<div align="center">
    <h1><u>Spark Vest</u></h1>
    <p><strong>Your AI-Powered Investment Companion</strong></p>
    <p style="font-size: 1.2rem; font-weight: semi-bold;">
        <a href="#features" style="text-decoration: underline;">Features</a> •
        <a href="#architecture" style="text-decoration: underline;">Architecture</a> •
        <a href="#tech-stack" style="text-decoration: underline;">Tech Stack</a> •
        <a href="#getting-started" style="text-decoration: underline;">Getting Started</a> •
        <a href="#contributing" style="text-decoration: underline;">Contributing</a> •
        <a href="#team" style="text-decoration: underline;">Team</a>
    </p>
</div>

---

## 🚀 Project Overview

**Spark Vest** is a full-stack SaaS platform that empowers users with real-time, AI-driven investment insights, market analysis, and portfolio management. The system consists of a modern React frontend and a robust Python FastAPI backend agent, leveraging advanced AI (Agno) for stock predictions and analytics.

---

## Features

- 🤖 **AI-Powered Insights**: Real-time investment insights and market analysis powered by advanced AI (Agno)
- 📊 **Market Trends**: Comprehensive market trend summaries and analysis
- 📈 **Stock Market Tracking**: Real-time stock market data and personalized insights
- 🔍 **Smart Query System**: Instant answers to investment-related questions
- 🗂️ **Portfolio & Watchlist**: Manage your investments and watchlist seamlessly
- 🔐 **Authentication & Security**: Secure user authentication and data storage via Supabase

---

## 🏗️ Architecture & Design

The Spark Vest platform is composed of two main components:

1. **Frontend (React + Vite + TailwindCSS)**
2. **Backend Agent Server (FastAPI + Agno + Redis)**

### System Flow

<div align="center">
    <img src="./public/flowchart-design.png" alt="System Flowchart" width="400" />
</div>

### Sequence Diagram

<div align="center">
    <img src="./public/sequence-design.png" alt="Sequence Diagram" width="400" />
</div>

### Database Design

- PostgreSQL database hosted on Supabase
- Uses `auth.users.id` as the primary user identifier

<div align="center">
    <img src="./public/db-design.png" alt="Database Design" width="400" />
</div>

---

## 🛠️ Tech Stack

### Frontend

| Technology | Description |
|------------|-------------|
| [TypeScript](https://www.typescriptlang.org/) | Strongly typed language for scalable development |
| [Vite.js](https://vitejs.dev/) | Fast frontend build tool |
| [React](https://react.dev/) | UI library |
| [TailwindCSS](https://tailwindcss.com/) | Utility-first CSS framework |
| [Shadcn UI](https://ui.shadcn.com/) | Accessible UI components |
| [Supabase](https://supabase.com/) | Auth & database |
| [Vercel](https://vercel.com/home) | Deployment platform |

### Backend (Agent Server)

| Technology | Description |
|------------|-------------|
| [FastAPI](https://fastapi.tiangolo.com/) | High-performance Python API framework |
| [Agno](https://github.com/agnolabs/agno) | Multi-modal AI agent library |
| [Redis](https://redis.io/) | In-memory cache & message broker |
| [Docker](https://www.docker.com/) | Containerization |
| [Render](https://render.com/) | Cloud deployment |

---

## 🏁 Getting Started

### Prerequisites
- Node.js (v16 or higher)
- npm or yarn
- Python 3.8+
- (Optional) Docker

### 1. Clone the Repository

```bash
git clone https://github.com/yashksaini-coder/global-agent-hackathon-may-2025.git
cd global-agent-hackathon-may-2025
```

### 2. Frontend Setup

```bash
npm install
# or
yarn install
```

#### Start the Frontend Dev Server

```bash
npm run dev
# or
yarn dev
```

Open [http://localhost:5173](http://localhost:5173) in your browser.

### 3. Backend (Agent Server) Setup

```bash
cd agent-server
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### Start the Agent Server

```bash
uvicorn app:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at [http://localhost:8000](http://localhost:8000)

> **Note:** Ensure Redis is running and any required environment variables are set (see `.env` or documentation for details).

---

## 🤝 Contributing

We welcome contributions! Please:
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

For major changes, open an issue first to discuss your ideas.

---

## 🙏 Acknowledgments
- Thanks to all contributors who have helped shape Spark Vest
- Special thanks to the open-source community for the amazing tools and libraries

---

## 👥 Team

<div align="center">
    <table>
        <tbody>
            <tr>
                <td align="center" width="33.33%">
                    <img src="https://avatars.githubusercontent.com/u/115717039?v=4" width="130px;"/>
                    <br/>
                    <h4 align="center">
                        <b>Yash K. Saini</b>
                    </h4>
                    <div align="center">
                        <p>Lead Developer</p>
                        <a href="https://linkedin.com/in/yashksaini"><img src="https://skillicons.dev/icons?i=linkedin" width="25" alt="LinkedIn"/></a>
                        <a href="https://twitter.com/yash_k_saini"><img src="https://skillicons.dev/icons?i=twitter" width="25" alt="Twitter"/></a>
                        <a href="https://github.com/yashksaini-coder"><img src="https://skillicons.dev/icons?i=github" width="25" alt="GitHub"/></a>
                    </div>
                </td>
            </tr>
        </tbody>
    </table>
    <p><strong>Made with ❤️ and ☕ by the Spark Vest Team</strong></p>
</div>