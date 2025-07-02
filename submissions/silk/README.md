# Silk - Your AI Course Platform

Silk is an innovative AI-powered platform designed to revolutionize how you learn. Forget rigid curriculums; with Silk, you can create personalized courses on **any topic, at any difficulty level, in no time.** Our intelligent system crafts comprehensive, section-wise course setups tailored to your exact learning needs. Beyond creation, Silk also provides intuitive analytics to track your learning progress.

https://www.loom.com/share/1a655c6d51644e63ac049107cd256a57?sid=10fc3807-352c-4e2a-9516-f7770b038d57

## ✨ Features

- **AI-Powered Course Generation:** Simply describe what you want to learn, and Silk's intelligent agents will instantly generate a structured course outline and detailed section content.
- **Customizable Learning:** Specify the topic, depth, and difficulty, and Silk adapts to your requirements.
- **Section-Wise Setup:** Courses are meticulously organized into logical sections, providing a complete and digestible learning path.
- **Real-time Interaction:** Engage with the course creation process in real-time via a responsive chat interface.
- **Progress Analytics:** Track your learning journey with built-in analytics, showing course completion rates, section progress, and more.
- **Minimalist & Responsive UI:** A clean, professional user interface powered by React and Tailwind CSS, ensuring a seamless experience across all devices.

## 🚀 Technologies Used

Silk is built with a modern, robust tech stack to deliver a smooth and scalable experience.

### Backend

- **Framework:** Flask
- **Real-time:** Flask-SocketIO
- **AI/LLM Integration:** Agno (for Google Gemini interaction)
- **Database:** SQLite

### Frontend

- **Framework:** React
- **Language:** TypeScript
- **Routing:** React Router DOM
- **Styling:** Tailwind CSS
- **Charting:** Recharts JS
- **Icons:** Lucide React

## 🏗️ Architecture Overview

Silk follows a clear separation of concerns, divided into a Flask backend and a React frontend:

**Backend:**
The Flask backend is initialized directly within `backend/main.py`, centralizing the application and SocketIO setup. It uses a dedicated **Flask-SocketIO namespace** for handling real-time AI course generation interactions. AI agents (powered by Google Gemini via `agno`) are integrated to perform course validation, outline generation, and content creation.

**Frontend:**
The React frontend, built with TypeScript, provides a dynamic and responsive user interface.

## ⚙️ Setup and Installation

Follow these steps to get Silk up and running on your local machine.

### Prerequisites

- Python 3.12+
- Node.js (LTS version recommended) & npm (or yarn)
- Git

### 🚀 1. Navigate to Silk project in `global-agent-hackathon-may-2-25` repository

```bash
cd submissions/silk
```

### ⚙️ 2. Install System Requirements (Python, Node.js)
Run the setup script from the project root:

```bash
bash setup.sh
```
This will:

- Check/install Python 3.12+
- Check/install Node.js (LTS) and npm
- Set up Environment Variables

### 📦 3. Install Project Dependencies
After system setup, run:

```bash
make install
```
This will:

- Create a Python virtual environment in backend/
- Install backend Python dependencies via pip
- Install frontend dependencies via npm in frontend/

### 📝 4. Configure Environment Variables


The setup file will configure the env but to change them simply do the following
a. Backend Environment Variables
Create a .env file in `backend` if not present:

```bash
touch backend/.env
```
Add:

```bash
GEMINI_MODEL=your_gemini_model_id_here_e.g._gemini-2.0-flash
GEMINI_API_KEY=your_google_gemini_api_key_here
DB_PATH=sqlite_db.db
```
b. Frontend Environment Variables
Create a .env file in `frontend` if not present:

```bash
touch frontend/.env
```

Add:
```bash
VITE_API_URL=http://localhost:8000
```
### ▶️ 5. Run the Application
To start both backend and frontend servers concurrently:

```bash
make run
```

Backend runs on: http://localhost:8000

Frontend runs on: http://localhost:5173

## 🚀 Usage

1. Once both the backend and frontend servers are running, open your web browser and navigate to the frontend URL (e.g., `http://localhost:5173/`).
2. Use the navigation links in the header (`Courses`, `Create Course`, `Analytics`) to explore the application.
3. In the "Create Course" section, you can start creating a new course by providing a description. Observe how Silk generates the course in real-time.
4. Visit the "Analytics" page to see your course progress and insights.

## 🤝 Contributing

Contributions are welcome\! Please feel free to open issues or submit pull requests.
