
---

# 🚀 Job Orbit – *Your AI Hiring Companion*

## 📘 Table of Contents

* [🔍 Overview of the Idea](#overview-of-the-idea)
* [🎯 Project Goal](#project-goal)
* [⚙️ How It Works](#how-it-works)

  * [👤 User Flow](#user-flow)
  * [🧠 Core Functionality](#core-functionality)
  * [🖼️ Multimodal Elements](#multimodal-elements)
  * [🛠️ Tools Used](#tools-used)
* [🎨 UI Approach](#ui-approach)
* [🎥 Demo Video](#demo-video)
* [👥 Team Information](#team-information)
* [🧪 Setup Instructions](#setup-instruction)

  * [🔧 Step 1: Setup environment variables](#step-1-setup-environment-variables-for-agno-agent-and-linkedinapi-in-the-terminal)
  * [📄 Step 2: Storing environment variables](#step-2-storing-environment-variables-in-env-file)
  * [🧠 Step 3: Ollama models setup](#step-3-if-using-ollam-models)
  * [📦 Step 4: Virtual Environment setup](#step-4-creating-virtual-environment-and-installing-the-dependencies)
  * [🚀 Step 5: Launch Application](#step-5-launch-joborbit-application)
* [🌟 Features to Explore](#features-to-explore)

  * [🛠️ Current Features](#current-features)
  * [🔮 Future Scope](#future-scope)

---

## 🔍 Overview of the Idea

**Job Orbit** is an AI-powered assistant that revolutionizes the job hunt—from discovery to application—by automating time-consuming tasks like job search, resume tailoring, and referral requests.

Busy professionals often lack the time to conduct thorough job searches or tailor resumes for each application. Networking for referrals can also be daunting. Job Orbit eliminates these hurdles with intelligent automation—freeing you to focus on what matters: **preparing for interviews** and **securing your next role**.

---

## 🎯 Project Goal

The mission of Job Orbit is to **automate and personalize the entire job search lifecycle**. This project showcases how AI agents can seamlessly integrate across platforms—like LinkedIn, resume tools, and document generators—to deliver real-world value to job seekers.

---

## ⚙️ How It Works

### 👤 User Flow:

1. **Upload Resume** – Start by uploading your current resume
2. **Review Extracted Details** – Confirm and edit parsed information
3. **Configure Search Parameters** – Define your job preferences
4. **Initiate Job Search** – Activate AI to scan LinkedIn for matches
5. **Review Discovered Opportunities** – View AI-found listings with detailed insights
6. **Generate Customized Resumes** – Automatically tailor resumes for each role
7. **Request Referrals** – Let the AI contact potential referrals
8. **Apply to Jobs** – Submit applications with one click

### 🧠 Core Functionality:

* **Resume Parsing** – Extracts structured data from PDFs
* **AI Job Search** – Scans LinkedIn for relevant roles
* **Resume Optimization** – Inserts role-specific keywords
* **Referral Outreach** – Sends context-aware messages to connections
* **Automated Applications** – Applies using prefilled job forms
* **Model Flexibility** – Compatible with AWS Bedrock & Ollama models

### 🖼️ Multimodal Elements:

* 📄 **Document Parsing** – Resume extraction and generation
* 🌐 **Web Automation** – AI-driven LinkedIn interaction
* ✍️ **Text Generation** – Personalized messaging for networking
* 🧾 **Form Completion** – Smart autofill for applications

### 🛠️ Tools Used:

* **Agno Agents** – AI orchestration backbone
* **AWS Bedrock** – NLP and text generation models
* **BrowserUse Agent** – For automated browser tasks
* **LaTeX** – For resume formatting
* **PDF Libraries** – Resume data extraction
* **LinkedIn API** – Search and application integration

---

## 🎨 UI Approach

Job Orbit’s interface is designed for clarity and usability:

* 📤 **Upload Panel** – Drag-and-drop for easy resume submission
* 🧾 **Information Review** – Clean, editable view of resume details
* 🔍 **Search Config** – Straightforward job preference forms
* 📊 **Results Dashboard** – Insightful job listing display
* 📝 **Resume Preview** – Compare original vs. customized resumes
* ⏳ **Agent Monitor** – Real-time process indicators
* 🧭 **Control Panel** – Simple, prominent action buttons

---

## 🎥 Demo Video

▶️ **Watch Job Orbit in Action** → [Click to View Demo](https://drive.google.com/file/d/1_eeGdMl-dlULm2U4D-6t0JfBoD8_j33n/view?usp=sharing)

---

## 👥 Team Information

### 🧑‍💼 Team Lead:

* **GitHub:** [Rishi-Raj-Kalita](https://github.com/Rishi-Raj-Kalita)
* **Role:** Data/AI Consultant at AWS

---

## 🧪 Setup Instruction

### 🔧 Step 1: Setup environment variables for Agno Agent and LinkedIn API

```bash
export AWS_ACCESS_KEY_ID=***
export AWS_SECRET_ACCESS_KEY=***
export AWS_REGION=***
```

> **Note**: Ensure `Claude 3 Sonnet` and `Claude 3.7 Sonnet` are enabled in the AWS Console.

---

### 📄 Step 2: Storing environment variables in `.env` file

Create a `.env` file at the root level and add:

```env
ACCESS_KEY=*** 
SECRET_KEY=*** 
LINKEDIN_NAME=*** 
LINKEDIN_PASSWORD=***
```

---

### 🧠 Step 3: If using Ollama models

Start the Ollama server:

```bash
ollama serve
```

> **Note**: This project uses `llama3.1`—ensure it is downloaded beforehand.

---

### 📦 Step 4: Creating Virtual Environment and Installing Dependencies

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

---

### 🚀 Step 5: Launch JobOrbit Application

```bash
cd job_orbit_issue33
streamlit run App.py
```

> 🎉 This will launch the **Job Orbit UI** on your local browser.

---

## 🌟 Features to Explore

### 🛠️ Current Features

* ✅ **PDF Resume Upload & Parsing**
* ✅ **LinkedIn Job Search with AI**
* ✅ **Dynamic Resume Customization**
* ✅ **Referral Outreach via LinkedIn**
* ✅ **One-Click Job Applications**

---

### 🔮 Future Scope

* 🧠 **Memory Integration** – Add contextual memory with Mem0
* 🕸️ **Company Portal Applications** – Use FireCrawl + BrowserUse for non-LinkedIn sites

---

