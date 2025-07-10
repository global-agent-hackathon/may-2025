# Kippr - AI-Powered E-commerce Shopping Assistant

Kippr is an intelligent shopping assistant that allows users to shop through natural conversation instead of traditional click-and-navigate interfaces. It's like having a personal shopping assistant who understands your needs and helps you find, compare, and purchase products through a simple chat interface.

## Prerequisites

- Python 3.9 or higher
- MongoDB
- Razorpay Account
- Cal.com Account
- Groq API Key
- Cohere API Key

## Setup Instructions

### 1. Create and Activate Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Set Up MongoDB

1. Create a new database named 'kippr'
2. Create a 'products' collection
3. (Optional) Run the sample products script to populate the database with sample data:
```bash
python sample_products.py
```

### 4. Environment Variables
Create a `.env` file in the project root with the following variables:
```env
MONGODB_URI=mongodb://localhost:27017/kippr
RAZORPAY_KEY_ID=your_razorpay_key_id
RAZORPAY_KEY_SECRET=your_razorpay_key_secret
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL_ID=your_groq_model_id
COHERE_API_KEY=your_cohere_api_key
CALCOM_API_KEY=your_calcom_api_key
CALCOM_EVENT_TYPE_ID=your_calcom_event_type_id
```

### 5. Run the Application

1. Start the local server:
```bash
python playground.py
```
This will start the server at `http://localhost:7777`

2. Access the Agno Playground:
   - Go to [https://app.agno.com/playground/agents](https://app.agno.com/playground/agents)
   - Select the endpoint: `http://localhost:7777`


## Features

- **Product Discovery**: Ask about products in natural language
- **Order Management**: Create and track orders through conversation
- **Payment Processing**: Secure payment links through Razorpay
- **Customer Support**: Book meetings with human agents via Cal.com
- **Smart Recommendations**: AI-powered product suggestions

## Project Structure

```
Kippr/
├── agent.py          # Main agent configuration
├── tools.py          # Custom tools implementation
├── playground.py     # Server setup
├── requirements.txt  # Project dependencies
├── .env              # Environment variables
└── data/             # Knowledge base data
```
