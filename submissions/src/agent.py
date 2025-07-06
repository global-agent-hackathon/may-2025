import logging
import os
import json
import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from langchain.schema import SystemMessage, HumanMessage
import google.generativeai as genai
from langchain_google_genai import ChatGoogleGenerativeAI
from .utils.cache import RedisCache
from .tools import BaseTool, CryptoNewsTool, CryptoSearchTool, TwitterTool, DexscreenerTool
from .prompts import SYSTEM_PROMPT, HUMAN_PROMPT_TEMPLATE, TOOL_SELECTION_PROMPT
from .utils.response_utils import parse_llm_response, fallback_response
from .constants import GEMINI_FLASH, LLM_TEMPERATURE
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
class CryptoAgent:
    def __init__(self, redis_host: str = "localhost", redis_port: int = 6379, redis_password: str = ""):
        logger.info("Initializing CryptoAgent")
        
        self.cache = RedisCache(host=redis_host, port=redis_port, password=redis_password)
        
        self.tools = {}
        self.register_tool(CryptoNewsTool(self.cache))
        self.register_tool(CryptoSearchTool(self.cache))
        self.register_tool(TwitterTool(self.cache))
        self.register_tool(DexscreenerTool(self.cache))
        
        logger.info(f"Registered {len(self.tools)} tools: {', '.join(self.tools.keys())}")
        
        google_api_key = os.getenv("GOOGLE_API_KEY")
        if not google_api_key:
            logger.warning("GOOGLE_API_KEY not set. Agent functionality will be limited.")
        
        genai.configure(api_key=google_api_key)
        
        self.llm = ChatGoogleGenerativeAI(
            model=GEMINI_FLASH,
            temperature=LLM_TEMPERATURE,
            google_api_key=google_api_key,
            convert_system_message_to_human=False,
        )
        
        logger.info("CryptoAgent initialized successfully")
    
    def register_tool(self, tool: BaseTool) -> None:
        self.tools[tool.name] = tool
        logger.info(f"Registered tool: {tool.name}")
    
    async def select_tools(self, query: str) -> List[Dict[str, Any]]:
        logger.info(f"Selecting appropriate tools for query: '{query}'")
        try:
            tool_descriptions = "\n".join([
                f"- {name}: {tool.description}"
                for name, tool in self.tools.items()
            ])
            
            prompt = TOOL_SELECTION_PROMPT.format(tools_needed=tool_descriptions)
            
            logger.debug(f"Sending tool selection prompt to LLM")
            response = self.llm.invoke([
                SystemMessage(content=prompt),
                HumanMessage(content=query)
            ])
            logger.debug(f"Received tool selection response: {response.content}")
            
            try:
                response_content = response.content.strip()
                if response_content.startswith("```json"):
                    response_content = response_content.replace("```json", "", 1)
                if response_content.endswith("```"):
                    response_content = response_content[:-3]
                    
                parsed_response = json.loads(response_content.strip())
                logger.debug(f"Successfully parsed tool selection as JSON: {parsed_response}")
                tools_needed = parsed_response.get("tools_needed", [])
                
                if not tools_needed:
                    logger.warning(f"No valid tools selected from JSON response, defaulting to crypto_search and twitter")
                    return [
                        {"name": "crypto_search", "custom_input": query},
                        {"name": "twitter", "custom_input": query}
                    ]
                
                valid_tools = []
                for tool in tools_needed:
                    if tool.get("name") in self.tools:
                        valid_tools.append(tool)
                        logger.debug(f"Added valid tool from selection: {tool.get('name')}")
                    else:
                        logger.warning(f"Tool {tool.get('name')} not found in registered tools")
                
                if not valid_tools:
                    logger.warning(f"No valid tools selected, defaulting to crypto_search and twitter")
                    return [
                        {"name": "crypto_search", "custom_input": query},
                        {"name": "twitter", "custom_input": query}
                    ]
                
                logger.info(f"Selected tools: {', '.join([t.get('name') for t in valid_tools])} for query: '{query}'")
                return valid_tools
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON response: {str(e)}, defaulting to crypto_search and twitter")
                return [
                    {"name": "crypto_search", "custom_input": query},
                    {"name": "twitter", "custom_input": query}
                ]
                
        except Exception as e:
            logger.error(f"Error selecting tools: {str(e)}", exc_info=True)
            logger.info(f"Defaulting to crypto_search and twitter due to error")
            return [
                {"name": "crypto_search", "custom_input": query},
                {"name": "twitter", "custom_input": query}
            ]
    
    async def process_query(self, query: str, min_articles: int = 3, additional_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        logger.info(f"Processing query: '{query}' (min_articles: {min_articles})")
        if additional_context and len(additional_context) > 0:
            logger.info(f"Additional context provided with keys: {', '.join(additional_context.keys())}")
        
        try:
            logger.debug("Starting tool selection")
            selected_tools = await self.select_tools(query)
            
            logger.debug(f"Preparing to execute {len(selected_tools)} tools")
            tool_tasks = []
            for tool_info in selected_tools:
                tool_name = tool_info.get("name")
                custom_input = tool_info.get("custom_input", query)
                
                if tool_name in self.tools:
                    logger.debug(f"Creating task for tool: {tool_name} with input: '{custom_input}'")
                    tool = self.tools[tool_name]
                    task = asyncio.create_task(tool.execute({"query": custom_input}))
                    tool_tasks.append((tool_name, task))
                else:
                    logger.warning(f"Tool {tool_name} not found in registered tools")
            
            logger.debug(f"Executing {len(tool_tasks)} tool tasks")
            tool_responses = {}
            successful_tools = []
            for tool_name, task in tool_tasks:
                try:
                    logger.debug(f"Awaiting response from {tool_name}")
                    result = await task
                    logger.debug(f"Received response from {tool_name}")
                    
                    if "error" in result and (not result.get("tweets", []) and not result.get("articles", [])):
                        logger.warning(f"Tool {tool_name} returned an error: {result.get('error')}")
                    else:
                        article_count = len(result.get("articles", []))
                        tweet_count = len(result.get("tweets", []))
                        logger.info(f"Tool {tool_name} returned {article_count} articles and {tweet_count} tweets")
                        tool_responses[tool_name] = result
                        successful_tools.append(tool_name)
                except Exception as e:
                    logger.error(f"Error executing {tool_name}: {str(e)}", exc_info=True)
            
            combined_data = {
                "articles": [],
                "tweets": [],
                "time_context": "Recent news"
            }
            
            logger.debug("Processing all successful tool responses")
            for tool_name, response in tool_responses.items():
                if "articles" in response:
                    article_count = len(response.get("articles", []))
                    logger.debug(f"Adding {article_count} articles from {tool_name}")
                    combined_data["articles"].extend(response.get("articles", []))
                
                if "tweets" in response:
                    tweets = response.get("tweets", [])
                    logger.debug(f"Adding {len(tweets)} tweets from {tool_name}")
                    combined_data["tweets"].extend(tweets)
                    
                    for tweet in tweets:
                        logger.debug(f"Converting tweet by @{tweet.get('author', 'unknown')} to article format")
                        combined_data["articles"].append({
                            "title": f"Tweet by @{tweet.get('author', 'unknown')}",
                            "summary": tweet.get("text", ""),
                            "link": f"https://twitter.com/{tweet.get('author', 'unknown')}/status/{tweet.get('id', '')}",
                            "published": tweet.get("created_at", ""),
                            "category": "Social Media",
                            "subCategory": "Twitter"
                        })
                
                if "time_context" in response:
                    logger.debug(f"Setting time context from {tool_name}: {response.get('time_context')}")
                    combined_data["time_context"] = response.get("time_context")
            
            if not combined_data["articles"]:
                logger.info("No articles found from primary tools, checking for token-specific content")
                token_name = None
                
                if "token" in query.lower():
                    possible_tokens = query.lower().split("token")
                    if len(possible_tokens) > 0:
                        token_name = possible_tokens[0].strip()
                        logger.info(f"Extracted possible token name from query: {token_name}")
                
                if additional_context and len(additional_context) > 0 and "token_data" in additional_context:
                    token_name = additional_context.get("token_data", {}).get("token_name", "")
                    logger.info(f"Found token name in additional context: {token_name}")
                
                if token_name and "twitter" not in tool_responses:
                    logger.info(f"Trying Twitter specifically for token: {token_name}")
                    twitter_tool = self.tools["twitter"]
                    twitter_result = await twitter_tool.execute({"query": f"{token_name} token cryptocurrency"})
                    
                    if twitter_result and "tweets" in twitter_result:
                        tweets = twitter_result.get("tweets", [])
                        if tweets:
                            logger.info(f"Found {len(tweets)} tweets about {token_name} token")
                            combined_data["tweets"].extend(tweets)
                            for tweet in tweets:
                                combined_data["articles"].append({
                                    "title": f"Tweet by @{tweet.get('author', 'unknown')}",
                                    "summary": tweet.get("text", ""),
                                    "link": f"https://twitter.com/{tweet.get('author', 'unknown')}/status/{tweet.get('id', '')}",
                                    "published": tweet.get("created_at", ""),
                                    "category": "Social Media",
                                    "subCategory": "Twitter"
                                })
                            successful_tools.append("twitter")
                            tool_responses["twitter"] = twitter_result
                        else:
                            logger.warning(f"No tweets found about {token_name} token")
            
            if not combined_data["articles"] and "twitter" not in tool_responses:
                logger.warning("No articles found, falling back to twitter")
                twitter_tool = self.tools["twitter"]
                twitter_result = await twitter_tool.execute({"query": query})
                
                if twitter_result and "tweets" in twitter_result:
                    tweets = twitter_result.get("tweets", [])
                    if tweets:
                        logger.info(f"Found {len(tweets)} tweets from twitter fallback")
                        combined_data["tweets"].extend(tweets)
                        for tweet in tweets:
                            combined_data["articles"].append({
                                "title": f"Tweet by @{tweet.get('author', 'unknown')}",
                                "summary": tweet.get("text", ""),
                                "link": f"https://twitter.com/{tweet.get('author', 'unknown')}/status/{tweet.get('id', '')}",
                                "published": tweet.get("created_at", ""),
                                "category": "Social Media",
                                "subCategory": "Twitter"
                            })
                        successful_tools.append("twitter")
                        tool_responses["twitter"] = twitter_result
                    else:
                        logger.warning("No tweets found from twitter fallback")
            
            if not combined_data["articles"] and "crypto_news" not in tool_responses:
                logger.warning("No articles or tweets found, falling back to crypto_news")
                crypto_news_tool = self.tools["crypto_news"]
                crypto_news_result = await crypto_news_tool.execute({"query": query})
                
                if crypto_news_result and "articles" in crypto_news_result and crypto_news_result["articles"]:
                    logger.info(f"Found {len(crypto_news_result['articles'])} articles from crypto_news fallback")
                    tool_responses["crypto_news"] = crypto_news_result
                    combined_data["articles"].extend(crypto_news_result.get("articles", []))
                    successful_tools.append("crypto_news")
                else:
                    logger.warning("No articles found from crypto_news fallback")
            
            if not combined_data["articles"]:
                logger.warning("No articles or tweets found from any tool or fallback mechanisms")
                return self._ensure_required_fields(fallback_response("No relevant articles or tweets found for your query"), query)
            
            logger.info(f"Preparing LLM input with {len(combined_data['articles'])} articles and {len(combined_data['tweets'])} tweets")
            articles_text = json.dumps(combined_data["articles"], indent=2)
            
            human_content = HUMAN_PROMPT_TEMPLATE.format(
                query=query,
                time_context=combined_data["time_context"],
                articles_text=articles_text,
                articles_count=len(combined_data["articles"]),
                time_range_start="unknown",
                time_range_end=datetime.now(),
            )
            
            if additional_context and len(additional_context) > 0:
                logger.info("Adding additional context to LLM prompt")
                human_content += f"\n\nAdditional Context:\n{json.dumps(additional_context, indent=2)}"
            
            if combined_data["tweets"]:
                logger.info(f"Adding {len(combined_data['tweets'])} tweets summary to LLM prompt")
                tweet_summary = f"\n\nAdditional Twitter Data:\nFound {len(combined_data['tweets'])} relevant tweets about the topic."
                human_content += tweet_summary
            
            messages = [
                SystemMessage(content=SYSTEM_PROMPT),
                HumanMessage(content=human_content)
            ]
            
            logger.info("Querying LLM for analysis")
            response = await self.llm.ainvoke(messages)
            llm_response = response.content.strip()
            logger.debug(f"LLM response length: {len(llm_response)} characters")
            
            try:
                logger.debug("Parsing LLM response")
                parsed_json = parse_llm_response(llm_response)
                logger.debug(f"Building final response with {len(combined_data['articles'])} articles")
                final_response = self._build_final_response(query, parsed_json, combined_data["articles"], min_articles)
                logger.info(f"Successfully processed query: '{query}' with sentiment: {final_response.get('sentiment')}")
                return final_response
                
            except Exception as e:
                logger.error(f"Error parsing LLM response: {str(e)}", exc_info=True)
                error_response = self._ensure_required_fields(fallback_response(f"Failed to process response: {str(e)}"), query)
                logger.info(f"Returning fallback response for query: '{query}'")
                return error_response
                
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}", exc_info=True)
            return self._ensure_required_fields(fallback_response(str(e)), query)
    
    def _build_final_response(self, query: str, parsed_json: Dict[str, Any], articles: List[Dict[str, Any]], min_articles: int) -> Dict[str, Any]:
        logger.info("Building final response from parsed LLM output and articles")
        
        context_parts = []
        article_analysis = parsed_json.get("article_analysis", [])
        
        for analysis in article_analysis[:3]:
            if analysis.get("significance"):
                logger.debug(f"Adding significance from article: {analysis.get('title', 'unknown')}")
                context_parts.append(analysis.get("significance"))
        
        context = " ".join(context_parts) if context_parts else f"Based on analysis of recent cryptocurrency news."
        logger.debug(f"Final context: {context}")
        
        return_articles = []
        if article_analysis:
            article_titles = [a.get("title", "") for a in article_analysis]
            logger.debug(f"Looking for articles matching {len(article_titles)} analyzed titles")
            for article in articles:
                if article.get("title", "") in article_titles and len(return_articles) < min_articles:
                    logger.debug(f"Adding analyzed article: {article.get('title', 'unknown')}")
                    return_articles.append(article)
        
        if len(return_articles) < min_articles:
            logger.debug(f"Adding more articles to reach minimum of {min_articles}")
            for article in articles:
                if article not in return_articles and len(return_articles) < min_articles:
                    logger.debug(f"Adding additional article: {article.get('title', 'unknown')}")
                    return_articles.append(article)
        
        logger.info(f"Final response contains {len(return_articles)} articles and {len(article_analysis)} analyses")
        
        response = {
            "query": query,
            "answer": parsed_json.get("answer", "No analysis available."),
            "sentiment": parsed_json.get("sentiment", "Neutral"),
            "context": context,
            "trending_topics": parsed_json.get("trending_topics", ["Bitcoin", "Ethereum", "Cryptocurrency"]),
            "articles": return_articles[:min_articles],
            "article_analysis": article_analysis,
            "processed_at": datetime.now().isoformat()
        }
        
        return self._ensure_required_fields(response, query)
    
    def _ensure_required_fields(self, response: Dict[str, Any], query: str) -> Dict[str, Any]:
        logger.debug("Ensuring all required fields are present in response")
        
        if "query" not in response:
            logger.debug("Adding missing 'query' field to response")
            response["query"] = query
        
        if "processed_at" not in response:
            logger.debug("Adding missing 'processed_at' field to response")
            response["processed_at"] = datetime.now().isoformat()
            
        if "articles" not in response:
            logger.debug("Adding missing 'articles' field to response")
            response["articles"] = []
            
        if "article_analysis" not in response:
            logger.debug("Adding missing 'article_analysis' field to response")
            response["article_analysis"] = []
            
        return response