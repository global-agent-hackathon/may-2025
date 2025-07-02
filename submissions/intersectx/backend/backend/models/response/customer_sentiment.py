from pydantic import BaseModel
from typing import Optional, List
from .base import CitationResponse
from backend.plot.types import ChartData


# --- Sentiment Summary ---
class SentimentTimeSeriesPoint(BaseModel):
    period_start: str  # ISO format date string (YYYY-MM-DD)
    period_end: str  # ISO format date string (YYYY-MM-DD)
    positive: int
    negative: int
    neutral: int
    sentiment_score: float
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class SentimentBreakdown(BaseModel):
    positive: int
    negative: int
    neutral: int


class SentimentSummaryResponse(CitationResponse):
    company_name: str
    product: Optional[str] = None
    region: Optional[str] = None
    sentiment_score: float
    sentiment_breakdown: SentimentBreakdown
    sentiment_timeseries: List[SentimentTimeSeriesPoint]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None  # ISO format datetime string

    def get_plot_data(self) -> ChartData:
        # Example: Line chart of sentiment score over time
        data = [
            {"period_start": t.period_start, "sentiment_score": t.sentiment_score}
            for t in self.sentiment_timeseries
        ]
        return ChartData(
            data=data,
            title=f"Sentiment Score Over Time for {self.company_name}",
            x="period_start",
            y="sentiment_score",
            kind="line",
        )

    class Config:
        arbitrary_types_allowed = True


# --- Customer Feedback ---
class CustomerFeedbackItem(BaseModel):
    date: str  # ISO format date string (YYYY-MM-DD)
    customer: Optional[str] = None
    feedback: str
    sentiment: str
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class CustomerFeedbackResponse(CitationResponse):
    company_name: str
    product: Optional[str] = None
    region: Optional[str] = None
    feedback_items: List[CustomerFeedbackItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None  # ISO format datetime string

    def get_plot_data(self) -> ChartData:
        # Example: Pie chart of feedback sentiment distribution
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for item in self.feedback_items:
            if item.sentiment in sentiment_counts:
                sentiment_counts[item.sentiment] += 1
        data = [{"sentiment": k, "count": v} for k, v in sentiment_counts.items()]
        return ChartData(
            data=data,
            title=f"Customer Feedback Sentiment Distribution for {self.company_name}",
            x="sentiment",
            y="count",
            kind="pie",
        )

    class Config:
        arbitrary_types_allowed = True


# --- Brand Reputation ---
class BrandReputationTimeSeriesPoint(BaseModel):
    period_start: str  # ISO format date string (YYYY-MM-DD)
    period_end: str  # ISO format date string (YYYY-MM-DD)
    reputation_score: float
    sources: Optional[List[str]] = None
    confidence: Optional[float] = None


class BrandReputationResponse(CitationResponse):
    company_name: str
    region: Optional[str] = None
    reputation_score: float
    reputation_timeseries: List[BrandReputationTimeSeriesPoint]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None  # ISO format datetime string

    def get_plot_data(self) -> ChartData:
        # Example: Line chart of reputation score over time
        data = [
            {"period_start": t.period_start, "reputation_score": t.reputation_score}
            for t in self.reputation_timeseries
        ]
        return ChartData(
            data=data,
            title=f"Brand Reputation Over Time for {self.company_name}",
            x="period_start",
            y="reputation_score",
            kind="line",
        )

    class Config:
        arbitrary_types_allowed = True


# --- Sentiment Comparison ---
class CompanySentimentData(BaseModel):
    company: str
    sentiment_score: float
    strengths: List[str]
    weaknesses: List[str]


class SentimentComparisonResponse(CitationResponse):
    company_name: str
    product: Optional[str] = None
    region: Optional[str] = None
    competitors: List[str]
    target_sentiment: CompanySentimentData
    competitor_sentiments: List[CompanySentimentData]
    summary: Optional[str] = None
    confidence: float
    last_updated: str  # ISO format datetime string

    def get_plot_data(self) -> ChartData:
        # Example: Bar chart comparing sentiment scores
        data = [
            {
                "company": self.company_name,
                "sentiment_score": self.target_sentiment.sentiment_score,
            }
        ] + [
            {"company": c.company, "sentiment_score": c.sentiment_score}
            for c in self.competitor_sentiments
        ]
        return ChartData(
            data=data,
            title=f"Sentiment Comparison for {self.company_name} vs Competitors",
            x="company",
            y="sentiment_score",
            kind="bar",
        )

    class Config:
        arbitrary_types_allowed = True
