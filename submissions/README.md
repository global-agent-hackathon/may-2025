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
  {
    "query":"What are the best perfoming coins right now ?",
    "min_articles":5
}
```

**Sample output:**
```json
{
    "query": "What are the best perfoming coins right now ?",
    "answer": "Based on the provided articles, it appears that several cryptocurrencies are showing potential for strong performance. BNB is eyeing a massive rally following a legal victory for Binance. XRP is also gaining traction with analysts forecasting a potential surge in June. Additionally, Salamanca (DON), a Cardano competitor, is anticipated to experience a significant price increase upon a potential Binance listing. However, Bitcoin is showing signs of fatigue after reaching a new all-time high, with analysts predicting a potential price drop.",
    "sentiment": "Mixed",
    "context": "This article highlights a major catalyst for BNB, suggesting a strong bullish outlook due to positive regulatory developments. This article indicates growing optimism for XRP, driven by anticipation surrounding the SEC's crypto roundtable and positive technical analysis. This article suggests a high-potential investment opportunity in Salamanca (DON), driven by the anticipation of increased trading volume and exposure from a Binance listing.",
    "trending_topics": [
        "BNB rally",
        "XRP price surge",
        "Salamanca (DON) Binance listing",
        "Bitcoin price correction",
        "PCE inflation data impact on crypto"
    ],
    "articles": [
        {
            "title": "Crypto Rebounds as BNB Eyes Massive Triple-Digit Rally",
            "summary": "The post Crypto Rebounds as BNB Eyes Massive Triple-Digit Rally appeared on BitcoinEthereumNews.com.\nKey Takeaways: The SEC throws out a high-profile lawsuit against Binance with prejudice, which shows a big change in how the current administration handles regulation. Binance celebrates the legal victory, calling it a “huge win for crypto” and crediting Chairman Paul Atkins and Trump-era allies for policy reversal. BNB is predicted to rise quickly as analysts foresee a rally toward a new all-time high. There is also growing speculation that it could break $1,000 if the momentum stays strong. The U.S. Securities and Exchange Commission (SEC) has officially abandoned its case against Binance. This is a big win for the global crypto industry in both legal and symbolic terms. This choice has already led to talk of a market-wide comeback and a revived positive mood for Binance’s native coin, BNB. SEC’s Sudden Dismissal Signals Policy Reversal The SEC has dropped its civil complaint against Binance “with prejudice,” which means that the issue is over and done with. It had been a big deal in the crypto sector since mid-2023. This legal language is very important because it makes sure the case can’t be reopened later. The U.S. government is revising how it controls digital assets right now, so this news is timely. Paul Atkins, who is well-known for being pro-crypto, is now a high-ranking official at the SEC. This shows that the agency is shifting away from what detractors called “regulation by enforcement.” People think that Atkins’ support for the Trump administration’s crypto-friendly policy is quite important. The SEC is moving away from the harsh crackdowns that were common during the Gary Gensler period under this new direction. Instead, the present government seems more interested in helping U.S. blockchain innovation, which it now sees as strategically crucial for keeping the U.S. competitive in finance. Binance publicly acknowledged this reversal in… ",
            "media": [
                "https://i3.wp.com/www.cryptoninjas.net/wp-content/uploads/In-the-center-SEC-vs.-Binance-is-depicted-in-a-d….jpeg"
            ],
            "link": "https://bitcoinethereumnews.com/crypto/crypto-rebounds-as-bnb-eyes-massive-triple-digit-rally/?utm_source=rss&utm_medium=rss&utm_campaign=crypto-rebounds-as-bnb-eyes-massive-triple-digit-rally",
            "authors": [
                {
                    "name": "Bitcoin Ethereum News"
                }
            ],
            "published": "2025-05-30T15:24:10+00:00",
            "category": "financial",
            "subCategory": "cryptocurrency",
            "language": "en",
            "timeZone": "UTC"
        },
        {
            "title": "XRP Price Prediction: Analysts Forecast Explosive XRP Rally in June as SEC Roundtable Approaches",
            "summary": "The post XRP Price Prediction: Analysts Forecast Explosive XRP Rally in June as SEC Roundtable Approaches appeared on BitcoinEthereumNews.com.\nAs June approaches, fresh momentum appears to be building for XRP amid rising anticipation surrounding the U.S. Securities and Exchange Commission’s (SEC) upcoming crypto roundtable. The Ripple-linked token has recently seen a series of conflicting price moves, leaving investors curious about what’s next. However, some top analysts remain bullish, predicting a potential surge that could reshape the current Ripple market narrative. XRP Rally Gaining Traction, Says Trader DonAlt Veteran crypto trader DonAlt believes that XRP’s recent upward trend may only be the beginning. In a recent analysis, he referred to XRP’s chart as “one of the most interesting” among altcoins, noting that the 20% gain seen since late April could be a prelude to a much larger move. XRP remains one of the most compelling altcoin charts, poised for strong performance if the broader market upswing continues. Source: DonAlt via X “What we’re seeing with XRP’s gains is just peanuts compared to what might be around the corner,” DonAlt said, highlighting $2.75 as a crucial resistance level. A breakout above this threshold, he added, could ignite a rapid price acceleration. DonAlt previously made accurate calls about XRP’s performance in late 2024, lending credibility to his latest prediction. The token’s recent rebound from its long-standing price floor has rekindled optimism. Since the April low, XRP has posted steady gains, defying broader market uncertainty. At the time of writing, XRP is priced at $2.22, though it has slipped below key support levels in the past 48 hours, sparking short-term caution. XRP Price Faces Key Technical Challenges Despite bullish longer-term sentiment, XRP is currently navigating a short-term downtrend. The price recently dropped below the important support zone between $2.30 and $2.34, placing the spotlight on lower levels like $2.15 and even $1.79. These are now viewed as key zones to prevent deeper declines… ",
            "media": [
                "https://i0.wp.com/bravenewcoin.com/wp-content/uploads/2025/05/Bnc-May-30-1.jpg"
            ],
            "link": "https://bitcoinethereumnews.com/tech/xrp-price-prediction-analysts-forecast-explosive-xrp-rally-in-june-as-sec-roundtable-approaches/?utm_source=rss&utm_medium=rss&utm_campaign=xrp-price-prediction-analysts-forecast-explosive-xrp-rally-in-june-as-sec-roundtable-approaches",
            "authors": [
                {
                    "name": "Bitcoin Ethereum News"
                }
            ],
            "published": "2025-05-30T15:21:08+00:00",
            "category": "financial",
            "subCategory": "cryptocurrency",
            "language": "en",
            "timeZone": "UTC"
        },
        {
            "title": "Priced Cheap Below $0.01, This Cardano (ADA) Competitor Could Rip 48x Higher in the Next 2 Weeks",
            "summary": "The post Priced Cheap Below $0.01, This Cardano (ADA) Competitor Could Rip 48x Higher in the Next 2 Weeks appeared on BitcoinEthereumNews.com.\nAs a Binance Smart Chain (BSC) meme coin, Salamanca (DON) is competing strongly with Cardano (ADA) in 2025. Due to its strong momentum, high trading volume on major exchanges and the strong expectation of an upcoming Binance listing, Salamanca (DON) is now being discussed among crypto enthusiasts, even though it trades far under $0.01. A number of market analysts are forecasting gains of over 2,000% and a rapid 48x rise in prices shortly. Current Price and Trading Activity According to the latest available data, the price of Salamanca (DON) is between $0.0012 and $0.0014 and this price may vary somewhat during the day. Users can purchase the token on Gate, MEXC, and PancakeSwap, ensuring that investors of every kind can trade it easily. Today’s 24-hour volume surpassed $3.8 million, highlighting how lively and involved the broader community is in the coin’s ecosystem. Binance Listing: The Next Major Catalyst The most exciting news for Salamanca (DON) is that it will soon be added to Binance, the largest crypto exchange. Many believe that a listing on Binance can substantially boost a token’s recognition, ease of trading, and the levels of buyers and sellers for the coin. People in the community are saying that key work is being done and the industry is keeping a close eye out for official notice. Upon the expected completion of the listing, Salamanca (DON) may welcome a lot of new buyers and see increased market activity. Price Range and Growth Targets DON is still around $0.009, so it is available to people looking to invest little money. You can buy Salamanca now for roughly $0.0012, which is much less than it cost at its highest point of $0.008512. Market forecasters are estimating a near-term rise of 2,000% compared to the current price and a few charts predict… ",
            "media": [
                "https://i0.wp.com/thenewscrypto.com/wp-content/uploads/2025/05/image001-115.jpg"
            ],
            "link": "https://bitcoinethereumnews.com/tech/priced-cheap-below-0-01-this-cardano-ada-competitor-could-rip-48x-higher-in-the-next-2-weeks/?utm_source=rss&utm_medium=rss&utm_campaign=priced-cheap-below-0-01-this-cardano-ada-competitor-could-rip-48x-higher-in-the-next-2-weeks",
            "authors": [
                {
                    "name": "Bitcoin Ethereum News"
                }
            ],
            "published": "2025-05-30T15:19:11+00:00",
            "category": "financial",
            "subCategory": "cryptocurrency",
            "language": "en",
            "timeZone": "UTC"
        },
        {
            "title": "PEPE Coin Prediction: $0.0001 in Sight, but Ozak AI’s $1 Goal Looks More Explosive",
            "summary": "The post PEPE Coin Prediction: $0.0001 in Sight, but Ozak AI’s $1 Goal Looks More Explosive appeared on BitcoinEthereumNews.com.\nThe meme coin mania that started with Dogecoin and exploded with Shiba Inu has given birth to many projects, and PEPE Coin is one of the latest to make waves in the crypto world. Inspired by the infamous Pepe the Frog meme, PEPE quickly captured investor attention with its viral appeal, massive supply, and low price point.  Now, traders are eyeing the next psychological level: $0.00001. But while PEPE grinds toward its target, Ozak AI, a new artificial intelligence crypto project, is making headlines with a $0.005 entry price, a $1 target, and over $1 million raised in its presale. Which project holds more potential in 2025? Let’s break down the forecast. Can PEPE Reach $0.0001? PEPE’s price trajectory has been defined by aggressive short-term pumps, followed by equally fast pullbacks. With billions of tokens in circulation, moving the price significantly takes substantial trading volume and interest. Reaching $0.00001 would require renewed momentum from meme coin traders and possibly another viral cycle. Technically, PEPE shows support at $0.0000052 and $0.0000041, with resistance forming at $0.000078 and $0.000095. If it breaks above those levels on strong volume, a move toward $0.0001 is within reach. However, it largely depends on sentiment, social media hype, and broader altcoin market conditions—factors that can be volatile and unpredictable. Youtube embed: Next 500X AI Altcoin Why Ozak AI’s $1 Target Looks More Explosive While PEPE has entertainment value and meme momentum, Ozak AI offers a fundamentally different proposition. Positioned at the intersection of artificial intelligence and decentralized technology, Ozak AI is targeting a more utility-driven audience. Its use cases in AI automation, predictive data models, and blockchain-based intelligence tools are designed to appeal to both retail and institutional investors. The real attention-grabber? Ozak AI is currently in its presale phase at just $0.005 per token. With… ",
            "media": [
                "https://i1.wp.com/www.livebitcoinnews.com/wp-content/uploads/2025/05/may-30-pr-2.png"
            ],
            "link": "https://bitcoinethereumnews.com/crypto/pepe-coin-prediction-0-0001-in-sight-but-ozak-ais-1-goal-looks-more-explosive/?utm_source=rss&utm_medium=rss&utm_campaign=pepe-coin-prediction-0-0001-in-sight-but-ozak-ais-1-goal-looks-more-explosive",
            "authors": [
                {
                    "name": "Bitcoin Ethereum News"
                }
            ],
            "published": "2025-05-30T15:30:07+00:00",
            "category": "financial",
            "subCategory": "cryptocurrency",
            "language": "en",
            "timeZone": "UTC"
        },
        {
            "title": "Katana Revolutionizes DeFi from Its Cradle with GSR and Polygon Labs",
            "summary": "Katana Foundation is a non-profit organization whose aim is to make the most advanced DeFi experience accessible to all kinds of users. It has announced the launch of Katana on a private mainnet. Engineered with DeFi in mind, this blockchain attempts to derive maximum productivity from each asset, endlessly granting superior yield and strong liquidity.\nThe post Katana Revolutionizes DeFi from Its Cradle with GSR and Polygon Labs appeared first on CoinGape.",
            "media": [
                "https://coingape.com/wp-content/uploads/2025/05/Katana-Revolutionizes-DeFi-from-Its-Cradle-with-GSR-and-Polygon-Labs.webp"
            ],
            "link": "https://coingape.com/blog/katana-revolutionizes-defi-from-its-cradle-with-gsr-and-polygon-labs/",
            "authors": [
                {
                    "name": "Coingape Staff"
                }
            ],
            "published": "2025-05-30T15:30:04+00:00",
            "category": "financial",
            "subCategory": "cryptocurrency",
            "language": "en",
            "timeZone": "UTC"
        }
    ],
    "article_analysis": [
        {
            "title": "Crypto Rebounds as BNB Eyes Massive Triple-Digit Rally",
            "key_points": "The SEC dropped its case against Binance, leading to predictions of a significant rally for BNB, potentially reaching a new all-time high and possibly breaking $1,000.",
            "significance": "This article highlights a major catalyst for BNB, suggesting a strong bullish outlook due to positive regulatory developments."
        },
        {
            "title": "XRP Price Prediction: Analysts Forecast Explosive XRP Rally in June as SEC Roundtable Approaches",
            "key_points": "Analysts predict a potential surge for XRP in June, with $2.75 identified as a crucial resistance level. A breakout above this level could lead to rapid price acceleration.",
            "significance": "This article indicates growing optimism for XRP, driven by anticipation surrounding the SEC's crypto roundtable and positive technical analysis."
        },
        {
            "title": "Priced Cheap Below $0.01, This Cardano (ADA) Competitor Could Rip 48x Higher in the Next 2 Weeks",
            "key_points": "Salamanca (DON) is expected to experience a 48x price increase following a potential Binance listing, with analysts forecasting gains of over 2,000%.",
            "significance": "This article suggests a high-potential investment opportunity in Salamanca (DON), driven by the anticipation of increased trading volume and exposure from a Binance listing."
        }
    ],
    "processed_at": "2025-05-30T21:14:19.201288"
}
```

---

**Crypto Agent**  
*Your AI-powered crypto research assistant. Real-time news, sentiment, and analytics—instantly.*
