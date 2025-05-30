# Crypto Agent - Local Development Setup Guide

**Crypto Agent** is your AI-powered assistant for real-time crypto news, social sentiment, token analytics, and web search.  
It leverages LLMs and a suite of specialized tools to deliver actionable insights for any crypto query.

---

## 1. Clone the Repository

```sh
git clone https://github.com/deployer117/global-agent-hackathon-may-2025
cd global-agent-hackathon-may-2025/submissions/crypto-agent
```

---

## 2. Install Python & Dependencies

- Requires **Python 3.10+** (3.12 recommended).
- Install dependencies:

```sh
pip install -r requirements.txt
```

---

## 3. Configure Environment Variables

Create a `.env` file in your project root (or export these in your shell).

**Required environment variables:**

| Variable              | Description                                      | Example/Default                      |
|-----------------------|--------------------------------------------------|--------------------------------------|
| `GOOGLE_API_KEY`      | Google Generative AI API key                     | (your key)                           |
| `RAPIDAPI_KEY`        | RapidAPI key for crypto news/search              | (your key)                           |
| `RAPIDAPI_HOST`       | RapidAPI host for crypto news/search             | crypto-news51.p.rapidapi.com         |
| `TWEETSCOUT_API_KEY`  | TweetScout API key for Twitter tool              | (your key)                           |
| `TAVILY_API_KEY`      | Tavily API key for web search                    | (your key)                           |
| `EXA_API_KEY`         | Exa API key for Exa web search                   | (your key)                           |
| `REDIS_HOST`          | Redis host                                       | localhost                            |
| `REDIS_PORT`          | Redis port                                       | 6379                                 |
| `REDIS_DB`            | Redis DB index                                   | 0                                    |
| `REDIS_PASSWORD`      | Redis password                                   | (blank by default)                   |
| `LOG_LEVEL`           | Logging level                                    | INFO                                 |
| `CACHE_TTL`           | Cache time-to-live (seconds)                     | 86400 (24h)                          |
| `CRON_INTERVAL`       | Cache update interval (minutes)                  | 60                                   |
| `API_RATE_LIMIT`      | API rate limit                                   | 100                                  |

**Example `.env` file:**
```
GOOGLE_API_KEY=your_google_api_key
RAPIDAPI_KEY=your_rapidapi_key
TWEETSCOUT_API_KEY=your_tweetscout_key
TAVILY_API_KEY=your_tavily_key
EXA_API_KEY=your_exa_key
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=
LOG_LEVEL=INFO
CACHE_TTL=86400
CRON_INTERVAL=60
API_RATE_LIMIT=100
```

---

## 4. Start Redis (Required for Caching)

Make sure you have a Redis server running locally or accessible at the host/port you set above.

- **Install Redis:**  
  - On Mac: `brew install redis`
  - On Ubuntu: `sudo apt-get install redis-server`
  - On Windows: [Download from here](https://github.com/microsoftarchive/redis/releases)
- **Start Redis:**  
  ```sh
  redis-server
  ```

---

## 5. Run Crypto Agent

```sh
python main.py
```

- This will:
  - Start the FastAPI server (default: http://localhost:8000)
  - Start a background scheduler to keep the cache fresh

---

## 6. (Optional) Run with Docker

If you prefer Docker:

```sh
docker build -t crypto-agent .
docker run --env-file .env -p 8000:8000 crypto-agent
```

---

## 7. Test the API

- You can send requests to the FastAPI server (see below for sample input/output).
- Example:
  ```sh
  curl -X POST http://localhost:8000/your-endpoint -H "Content-Type: application/json" -d '{"query": "web3 tools"}'
  ```

---

## 8. Troubleshooting

- **Missing API keys:** Make sure all required keys are set in your `.env`.
- **Redis errors:** Ensure Redis is running and accessible.
- **Dependency errors:** Run `pip install -r requirements.txt` again.
- **Port conflicts:** Change the port in `main.py` or Docker if needed.

---


## Example: Query and Response

**Sample input:**
```json
{
  "query": "how is monalisa doing?",
  "min_articles": 3,
  "additional_context": {
    "token_data": {
      "token_name": "MONALISA",
      "current_price_usd": 0.052599,
      "market_cap": "$2.60K",
      "liquidity": "$4.88K",
      "total_supply": "1000M",
      "performance": {
        "1h": "0%",
        "6h": "0%",
        "24h": "+5%"
      },
      "trading_metrics": {
        "transactions": 4,
        "volume": "$48",
        "buys": 2,
        "sells": 2,
        "buy_volume": "$43",
        "sell_volume": "$6"
      },
      "recent_trades": [
        {
          "type": "BUY",
          "age": "5h",
          "amount": "993K",
          "total_sol": "0.0200",
          "total_usd": "$2.66",
          "maker": "RRD1oj"
        }
      ]
    }
  }
}
```

**Sample output:**
```json
{
  "query": "how is monalisa doing?",
  "answer": "Crypto Agent analysis: MONALISA is currently priced at $0.052599, with a $2.60K market cap and $4.88K liquidity. The last 24h shows a 5% gain, but trading volume and liquidity are very low, indicating a micro-cap token. Social media activity highlights the #MONALISAChallenge and some meme coin buzz, but overall, this is a highly speculative asset with limited market depth.",
  "sentiment": "Neutral",
  "context": "Community engagement and marketing efforts are visible, but the token remains in the micro-cap, meme coin space.",
  "trending_topics": [
    "MONALISAChallenge",
    "Micro-cap token",
    "Low Liquidity",
    "Social Media Engagement"
  ],
  "articles": [
    {
      "title": "Tweet by @Solcaller1",
      "summary": "Solana token $Giza just locked in a massive 355.91x gain! ... #jhope_MONALISA ...",
      "link": "https://twitter.com/Solcaller1/status/1903175351863590989",
      "category": "Social Media",
      "subCategory": "Twitter"
    }
  ],
  "article_analysis": [
    {
      "title": "Tweet by @taesoothe",
      "key_points": "Highlights the #MONALISAChallenge event across various social media platforms.",
      "significance": "Shows community engagement and marketing efforts around the token, potentially driving awareness."
    }
  ],
  "processed_at": "2025-04-13T14:31:58.453665"
}
```

---

**Crypto Agent**  
*Your AI-powered crypto research assistant. Real-time news, sentiment, and analytics—instantly.*
