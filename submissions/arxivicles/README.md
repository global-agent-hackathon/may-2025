# Arxivicles 📚

A daily research papers newsletter that automatically curates and summarizes the latest papers from arXiv.org, delivering them directly to subscribers' inboxes.

## Overview

Arxivicles is a web application that:
- Fetches the latest research papers from arXiv.org
- Uses AI to generate concise summaries of each paper
- Delivers daily newsletters to subscribers via email
- Provides a clean web interface to view papers and manage subscriptions
- Automatically sends newsletters at 12:40 PM IST daily

## How It Works

1. **Paper Collection**: The application uses the Exa API to search and fetch the latest papers from arXiv.org
2. **AI Summarization**: Each paper is processed through an AI model to generate reader-friendly summaries
3. **Newsletter Delivery**: Subscribers receive daily emails containing:
   - Paper titles and summaries
   - Direct links to full papers
   - Key findings and implications
4. **Web Interface**: Users can:
   - View the latest papers
   - Subscribe/unsubscribe to the newsletter
   - Manually trigger newsletter delivery (admin feature)

## Technologies Used

- **Backend**: Node.js with Express.js
- **Database**: PostgreSQL
- **Frontend**: EJS templates with Tailwind CSS and DaisyUI
- **APIs**: 
  - Exa API for paper search and summarization
  - Nodemailer for email delivery
- **Scheduling**: node-cron for automated newsletter delivery
- **Development**: nodemon for development server

## Setup Instructions

### Prerequisites

- Node.js (v14 or higher)
- PostgreSQL database
- Gmail account (for sending emails)

### Installation

1. Clone the hackathon repository:
   ```bash
   git clone https://github.com/agno-ai/global-agent-hackathon-may-2025.git
   cd global-agent-hackathon-may-2025/submissions/arxivicles
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create a `.env` file in the project directory with the following variables:
   ```
   # Database
   DATABASE_URL=postgresql://username:password@localhost:5432/arxivicles

   # Email Configuration
   EMAIL_USER=your-gmail@gmail.com
   EMAIL_PASS=your-app-specific-password

   # Exa API
   EXA_API_KEY=your-exa-api-key

   # Application
   PORT=3000
   BASE_URL=http://localhost:3000
   ```

### Required API Keys and Services

1. **Exa API**
   - Sign up at [exa.ai](https://exa.ai)
   - Get your API key from the dashboard
   - Add it to your `.env` file

2. **Gmail Setup**
   - Enable 2-factor authentication in your Gmail account
   - Generate an App Password:
     1. Go to Google Account Settings
     2. Security → App Passwords
     3. Generate a new app password for "Mail"
   - Use this password in your `.env` file

3. **PostgreSQL**
   - Install PostgreSQL if not already installed
   - Create a new database named `arxivicles`
   - Update the `DATABASE_URL` in your `.env` file

### Running the Application

1. Start the development server:
   ```bash
   npm start
   ```

2. The application will be available at `http://localhost:3000`

## Features

- **Daily Newsletter**: Automated delivery of research paper summaries
- **Web Interface**: Clean, responsive design for viewing papers
- **Subscription Management**: Easy subscribe/unsubscribe functionality
- **Admin Panel**: Manual newsletter trigger option
- **Email Notifications**: Welcome emails for new subscribers
- **Paper Caching**: Efficient paper storage and retrieval
- **Error Handling**: Robust error management and logging

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the ISC License.

## Support

For support, please open an issue in the GitHub repository or contact the maintainers. 