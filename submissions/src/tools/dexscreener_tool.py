import os
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import httpx

from ..tools.base_tool import BaseTool
from ..models import CryptoNewsResponse
from ..utils.cache import RedisCache

logger = logging.getLogger(__name__)

class DexscreenerTool(BaseTool):
    name = "dexscreener"
    description = "Get real-time token price, liquidity, volume, trending pairs, and trading data from Dexscreener. Use this for on-chain token analytics, trending tokens, and DEX pair search."

    BASE_URL = "https://api.dexscreener.com"

    def __init__(self, redis_cache: Optional[RedisCache] = None):
        super().__init__()
        self.cache = redis_cache

    # --- API endpoint methods ---
    async def fetch_token_data(self, address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest/tokens/{address}"
        logger.info(f"Fetching Dexscreener token data: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_pair_data(self, chain: str, pair_address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest/pairs/{chain}/{pair_address}"
        logger.info(f"Fetching Dexscreener pair data: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def search_pairs(self, query: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest/dex/search?q={query}"
        logger.info(f"Searching Dexscreener pairs: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_trending(self, chain: Optional[str] = None) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest/trending"
        if chain:
            url += f"?chain={chain}"
        logger.info(f"Fetching Dexscreener trending pairs: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_latest_token_profiles(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/token-profiles/latest/v1"
        logger.info(f"Fetching Dexscreener latest token profiles: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_latest_boosted_tokens(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/token-boosts/latest/v1"
        logger.info(f"Fetching Dexscreener latest boosted tokens: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_top_boosted_tokens(self) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/token-boosts/top/v1"
        logger.info(f"Fetching Dexscreener top boosted tokens: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_orders(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/orders/v1/{chain_id}/{token_address}"
        logger.info(f"Fetching Dexscreener orders: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_pair_by_chain_and_pair(self, chain_id: str, pair_id: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/latest/dex/pairs/{chain_id}/{pair_id}"
        logger.info(f"Fetching Dexscreener pair by chain and pair: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_token_pools(self, chain_id: str, token_address: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/token-pairs/v1/{chain_id}/{token_address}"
        logger.info(f"Fetching Dexscreener token pools: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    async def fetch_pairs_by_token_addresses(self, chain_id: str, token_addresses: str) -> Dict[str, Any]:
        url = f"{self.BASE_URL}/tokens/v1/{chain_id}/{token_addresses}"
        logger.info(f"Fetching Dexscreener pairs by token addresses: {url}")
        async with httpx.AsyncClient() as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return resp.json()

    # --- Main execute method ---
    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        # params: { ... see below ... }
        action = params.get("action")
        chain_id = params.get("chain_id")
        token_address = params.get("token_address")
        pair_id = params.get("pair_id")
        token_addresses = params.get("token_addresses")
        query = params.get("query")
        trending = params.get("trending")

        if action == "latest_token_profiles":
            data = await self.fetch_latest_token_profiles()
            return {"query": "Dexscreener latest token profiles", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "latest_boosted_tokens":
            data = await self.fetch_latest_boosted_tokens()
            return {"query": "Dexscreener latest boosted tokens", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "top_boosted_tokens":
            data = await self.fetch_top_boosted_tokens()
            return {"query": "Dexscreener top boosted tokens", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "orders" and chain_id and token_address:
            data = await self.fetch_orders(chain_id, token_address)
            return {"query": f"Dexscreener orders for {token_address} on {chain_id}", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "pair_by_chain_and_pair" and chain_id and pair_id:
            data = await self.fetch_pair_by_chain_and_pair(chain_id, pair_id)
            return {"query": f"Dexscreener pair {pair_id} on {chain_id}", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "search_pairs" and query:
            data = await self.search_pairs(query)
            return {"query": f"Dexscreener search for '{query}'", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "token_pools" and chain_id and token_address:
            data = await self.fetch_token_pools(chain_id, token_address)
            return {"query": f"Dexscreener pools for {token_address} on {chain_id}", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif action == "pairs_by_token_addresses" and chain_id and token_addresses:
            data = await self.fetch_pairs_by_token_addresses(chain_id, token_addresses)
            return {"query": f"Dexscreener pairs for tokens {token_addresses} on {chain_id}", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        elif trending:
            data = await self.fetch_trending(chain_id if isinstance(trending, str) else None)
            return {"query": f"Dexscreener trending pairs{f' on {chain_id}' if chain_id else ''}", "dexscreener": data, "timestamp": datetime.now().isoformat()}
        else:
            return {"error": "No valid Dexscreener parameters provided. Please specify a valid 'action' and required parameters."}

    def format_response(self, query: str, tool_response: Dict[str, Any]) -> Dict[str, Any]:
        response = self.create_base_response(query)
        dexscreener = tool_response.get("dexscreener", {})
        # Format for each action
        if isinstance(dexscreener, dict) and "pairs" in dexscreener:
            pairs = dexscreener.get("pairs", [])
            if pairs:
                summary = f"Found {len(pairs)} pairs. Top: " + ", ".join([p.get("baseToken", {}).get("symbol", "?") for p in pairs[:3]])
                response.update({
                    "answer": summary,
                    "context": "Pairs data from Dexscreener.",
                    "articles": [],
                    "trending_topics": [p.get("baseToken", {}).get("symbol", "?") for p in pairs[:3]],
                })
            else:
                response["answer"] = "No pairs found."
        elif isinstance(dexscreener, list):
            # For endpoints returning a list (orders, pools, tokens)
            if dexscreener:
                response.update({
                    "answer": f"Found {len(dexscreener)} results.",
                    "context": "List data from Dexscreener.",
                    "articles": [],
                    "trending_topics": [],
                })
            else:
                response["answer"] = "No results found."
        elif isinstance(dexscreener, dict):
            # For token profiles, boosts, etc.
            if "tokenAddress" in dexscreener:
                response.update({
                    "answer": f"Token: {dexscreener.get('tokenAddress')}, Chain: {dexscreener.get('chainId')}",
                    "context": "Token profile from Dexscreener.",
                    "articles": [],
                    "trending_topics": [],
                })
            else:
                response["answer"] = str(dexscreener)
        else:
            response["answer"] = "No relevant data found from Dexscreener."
        return response
