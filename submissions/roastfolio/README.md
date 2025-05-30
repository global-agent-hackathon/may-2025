# Roastfolio - AI Portfolio Roaster 🔥

![Roastfolio Screenshot](https://i.ibb.co/LhqZWvD7/Screenshot-2025-05-30-at-10-54-24-PM.png)

<div style="text-align: center;">
  <a href="https://roastfolio.vercel.app/">
    <img src="https://img.shields.io/badge/Try%20Roastfolio-Online-brightgreen?style=for-the-badge&logo=rocket" alt="Roast My Portfolio!" />
  </a>
</div>
<br>

**Roastfolio** is a fun, AI-powered web application that brutally (but lovingly!) analyzes your personal portfolio website. Paste your portfolio URL, and let our AI serve you a witty roast, identify your personality traits, suggest career options, and more!

Built for the **May 2025 Global Agent Hackathon**.

## ✨ Features

*   **Personalized Roast:** Get a unique, humorous roast based on your digital presence.
*   **Personality Insights:** Discover AI-guessed personality traits and your unique "vibe."
*   **Career Suggestions:** Receive potential career paths based on your portfolio.
*   **Archetype Identification:** Find out if you're "The Visionary Entrepreneur," "The Meticulous Researcher," or another cool archetype!
*   **Contact Extraction:** (Attempts to) find your public contact details.
*   **Clean & Simple UI:** Easy-to-use interface, inspired by minimalist design.
*   **Shareable Results:** Easily copy and share your roast and archetype.

## 🚀 How It Works

1.  **Input URL:** You paste the URL of your personal portfolio website.
2.  **Content Crawling:** We use **Firecrawl** to fetch and parse the content of your portfolio (up to 10 pages, focusing on main content as Markdown).
3.  **AI Analysis with Gemini:** The crawled content is sent to the **Google Gemini 1.5 Flash** model.
    *   A detailed system prompt guides the AI to extract specific information, generate the roast, traits, vibes, career options, and personality archetype.
    *   The AI is instructed to return this information in a strict JSON format.
4.  **Display Results:** The application parses the JSON response and displays the witty and insightful analysis on a clean, user-friendly interface.
5.  **Share the Fun:** You can then share your hilarious (or eye-opening) results!

## 🛠️ Tech Stack

*   **Frontend:** React with Vite, TypeScript
*   **Styling:** Tailwind CSS, shadcn/ui (for some components, adapted)
*   **Crawling Service:** [Firecrawl](https://firecrawl.dev/)
*   **AI Model:** [Google Gemini 1.5 Flash](https://ai.google.dev/models/gemini)
*   **Deployment:** Vercel

## ⚙️ Local Setup & Installation

Follow these steps to run Roastfolio locally:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/chiragjoshi12/global-agent-hackathon-may-2025.git
    cd global-agent-hackathon-may-2025/submissions/roastfolio
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    ```

3.  **Create an Environment File (`.env`):**
    ```env
    VITE_GEMINI_API_KEY=YOUR_GOOGLE_GEMINI_API_KEY
    VITE_FIRECRAWL_API_KEY=YOUR_FIRECRAWL_API_KEY
    ```
    *   Replace `YOUR_GOOGLE_GEMINI_API_KEY` with your actual API key from [Google AI Studio](https://aistudio.google.com/app/apikey).
    *   Replace `YOUR_FIRECRAWL_API_KEY` with your actual API key from [Firecrawl](https://firecrawl.dev/).

4.  **Run the development server:**
    ```bash
    npm run dev
    ```
    The application should now be running on `http://localhost:8080` (or another port if 8080 is busy).

## 💡 Future Ideas & Enhancements

*   **Shareable Image/GIF Generation:** Automatically create a visually appealing card (image or GIF) with the roast and archetype for easy social media sharing.
*   **Deeper Analysis Options:** Allow users to select specific areas of their portfolio for more targeted feedback.
*   **Tone Customization:** Let users choose the "roast intensity" (e.g., mild, spicy, inferno).
*   **Historical Roasts:** If users create accounts, allow them to see how their portfolio roast changes over time.
*   **Leaderboard/Trending Roasts:** (With privacy considerations) a fun section for popular or particularly witty roasts.
*   **Direct GitHub Repo Analysis:** Allow pasting a GitHub repository URL for analysis of READMEs and project descriptions.
*   **Browser Extension:** For quick portfolio roasting on the go.

## 🔗 Try It Out!

[https://roastfolio.vercel.app/](https://roastfolio.vercel.app/)

---

We hope you enjoy Roastfolio! Let the AI tell you what it *really* thinks. 😉