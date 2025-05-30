from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any

class AuthorModel(BaseModel):
    name: Optional[str] = Field(None, description="Author name")

class NewsItem(BaseModel):
    title: Optional[str] = Field(None, description="News article title")
    summary: Optional[str] = Field(None, description="Brief summary of the article")
    media: Optional[List[str]] = Field(None, description="Media URLs associated with the article")
    link: Optional[str] = Field(None, description="Link to the article")
    authors: Optional[List[AuthorModel]] = Field(None, description="List of article authors")
    published: Optional[str] = Field(None, description="Publication date of the article")
    category: Optional[str] = Field(None, description="Category of the article")
    subCategory: Optional[str] = Field(None, description="Sub-category of the article")
    language: Optional[str] = Field(None, description="Language of the article")
    timeZone: Optional[str] = Field(None, description="Timezone of publication")

class ArticleAnalysis(BaseModel):
    title: str = Field(..., description="Title of the article")
    key_points: str = Field(..., description="Key points from the article")
    significance: str = Field(..., description="Significance of the article in the market context")

class TweetItem(BaseModel):
    id: str = Field(..., description="Tweet ID")
    text: str = Field(..., description="Tweet text")
    author: str = Field(..., description="Tweet author")
    created_at: str = Field(..., description="Tweet creation date")
    likes: int = Field(0, description="Number of likes")
    retweets: int = Field(0, description="Number of retweets")

class QueryRequest(BaseModel):
    query: str = Field(..., description="User query")
    min_articles: Optional[int] = Field(3, description="Minimum number of articles to return")
    additional_context: Optional[Dict[str, Any]] = Field(None, description="Additional context for the query")

class CryptoNewsResponse(BaseModel):
    query: str = Field(..., description="Original query from the user")
    answer: str = Field(..., description="Answer to the query")
    sentiment: str = Field(..., description="Overall market sentiment (Bullish, Bearish, Neutral, or Mixed)")
    context: str = Field(..., description="Additional context about the market")
    trending_topics: List[str] = Field(default=[], description="List of trending topics in crypto")
    articles: List[NewsItem] = Field(..., description="List of relevant news articles")
    article_analysis: Optional[List[ArticleAnalysis]] = Field(None, description="Analysis of key articles")
    processed_at: str = Field(..., description="ISO timestamp when the query was processed")

class TwitterResponse(BaseModel):
    query: str = Field(..., description="Original query from the user")
    tweets: List[TweetItem] = Field(..., description="List of relevant tweets")
    processed_at: str = Field(..., description="ISO timestamp when the query was processed")

class ToolResponse(BaseModel):
    tool: str = Field(..., description="Tool used to generate the response")
    data: Dict[str, Any] = Field(..., description="Tool-specific response data")