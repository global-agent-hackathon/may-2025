# Arxivicles - AI-Powered Research Paper Newsletter

## Overview
Arxivicles is an intelligent newsletter system that automatically curates and summarizes the latest research papers from arXiv.org. It uses AI to generate human-readable summaries and delivers them to subscribers daily, making cutting-edge research more accessible to everyone.

## Project Goal
To bridge the gap between academic research and general audience by providing daily, AI-curated summaries of the latest research papers in an easily digestible format.

## How It Works

### User Flow
1. Users visit the website and subscribe with their email
2. They receive a welcome email confirming their subscription
3. Every day at 12:40 PM IST, subscribers receive a newsletter containing:
   - Summaries of the latest research papers
   - Direct links to the full papers
   - Key findings and implications
4. Users can unsubscribe at any time through the link in the newsletter

### Core Functionality
- Automated paper fetching from arXiv.org
- AI-powered paper summarization using Exa
- Daily newsletter generation and delivery
- Email subscription management
- Web interface for viewing current papers and managing subscriptions

### Technologies Used
- **Backend**: Node.js with Express
- **AI/ML**: Exa API for paper summarization
- **Database**: SQLite for subscriber management
- **Email**: Nodemailer for newsletter delivery
- **Scheduling**: node-cron for automated delivery
- **Frontend**: EJS templating engine

## Setup Instructions

### Prerequisites
- Node.js (v14 or higher)
- npm or yarn
- Gmail account for sending emails

### Environment Variables
Create a `.env` file with the following variables:
```
EXA_API_KEY=your_exa_api_key
EMAIL_USER=your_gmail_address
EMAIL_PASS=your_gmail_app_password
BASE_URL=your_application_url
PORT=3000
```

### Installation
1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Initialize the database:
   ```bash
   node db.js
   ```
4. Start the server:
   ```bash
   node index.js
   ```

### API Keys and Services
1. **Exa API**: Sign up at [exa.ai](https://exa.ai) to get your API key
2. **Gmail**: Enable 2-factor authentication and generate an app password for the email service

## Features
- Daily automated paper curation
- AI-generated paper summaries
- Email newsletter delivery
- Web interface for viewing papers
- Subscription management
- Welcome emails for new subscribers
- Unsubscribe functionality

## Future Enhancements
- Category-based paper filtering
- Custom delivery schedules
- Paper recommendation system
- Social sharing features
- User preferences for paper topics

## Team Information
- **Team Lead**: [Your GitHub Handle]
- **Role**: Full Stack Developer

## License
MIT License 