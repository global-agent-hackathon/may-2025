from pydantic import BaseModel, Field
from typing import Optional

from backend.models.response.base import CitationResponse
from backend.plot.types import ChartData


# --- Revenue Analysis ---
class RevenueTimeSeriesPoint(BaseModel):
    currency: str = Field(
        ...,
        description="ISO 4217 currency code for the revenue amount (e.g., 'USD', 'EUR')",
    )
    period_start: str = Field(
        ...,
        description="ISO 8601 formatted start date of the reporting period (e.g., '2023-01-01')",
    )
    period_end: str = Field(
        ...,
        description="ISO 8601 formatted end date of the reporting period (e.g., '2023-03-31')",
    )
    value: float = Field(
        ...,
        description="The revenue amount for the specified period in the given currency",
    )
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this revenue data point"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class RevenueAnalysisResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    revenue_timeseries: list[RevenueTimeSeriesPoint] = Field(
        ...,
        description="Time series data points showing revenue over different periods",
    )
    total_revenue: Optional[float] = Field(
        None,
        description="Aggregated total revenue across all time periods (in the primary currency)",
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {
                "period_start": t.period_start,
                "period_end": t.period_end,
                "value": t.value,
                "currency": t.currency,
            }
            for t in self.revenue_timeseries
        ]
        return ChartData(
            data=data,
            title=f"Revenue Over Time for {self.company_name}",
            x="period_start",
            y="value",
            kind="line",
        )


# --- Expense Analysis ---


class ExpenseTimeSeriesPoint(BaseModel):
    # TODO: Add if timeseries is required
    currency: str
    period_start: str
    period_end: str
    category: str
    value: float
    sources: Optional[list[str]] = None
    confidence: Optional[float] = None


class ExpenseCategoryBreakdown(BaseModel):
    category: str = Field(
        ...,
        description="The expense category (e.g., 'Salaries', 'Marketing', 'Rent', 'R&D')",
    )
    value: float = Field(
        ..., description="The monetary amount of expenses in this category"
    )
    currency: str = Field(
        ...,
        description="ISO 4217 currency code for the expense amount (e.g., 'USD', 'EUR')",
    )
    sources: Optional[list[str]] = Field(
        None, description="List of sources or references for this expense category data"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class ExpenseAnalysisResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    expenses: list[ExpenseCategoryBreakdown] = Field(
        ..., description="Detailed breakdown of expenses by category"
    )
    total_expense: Optional[float] = Field(
        None,
        description="Total sum of all expenses across all categories (in the primary currency)",
    )
    last_updated: Optional[str] = Field(
        None,
        description="ISO 8601 timestamp indicating when this expense analysis was last updated",
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {
                "category": e.category,
                "value": e.value,
                "currency": e.currency,
            }
            for e in self.expenses
        ]
        return ChartData(
            data=data,
            title=f"Expenses by Category for {self.company_name}",
            x="category",
            y="value",
            kind="pie",
        )


# --- Profit Margins ---
class ProfitMarginTimeSeriesPoint(BaseModel):
    # TODO: Add if timeseries is required
    period_start: str
    period_end: str
    gross_margin: Optional[float] = None
    operating_margin: Optional[float] = None
    net_margin: Optional[float] = None
    sources: Optional[list[str]] = None
    confidence: Optional[float] = None


class ProfitMarginBreakdown(BaseModel):
    margin_type: str = Field(
        ..., description="Type of profit margin (e.g., 'gross', 'operating', 'net')"
    )
    value: float = Field(
        ..., description="The actual profit margin value (typically a percentage)"
    )
    currency: str = Field(
        ..., description="Currency code for the financial data (e.g., 'USD', 'EUR')"
    )
    sources: Optional[list[str]] = Field(
        None, description="list of sources or references for this profit margin data"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class ProfitMarginsResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    margins: list[ProfitMarginBreakdown] = Field(
        ..., description="list of different profit margin metrics for the company"
    )
    last_updated: Optional[str] = Field(
        None, description="ISO date string when this margin data was last updated"
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {
                "margin_type": m.margin_type,
                "value": m.value,
                "currency": m.currency,
            }
            for m in self.margins
        ]
        return ChartData(
            data=data,
            title=f"Profit Margins for {self.company_name}",
            x="margin_type",
            y="value",
            kind="pie",
        )


# --- Valuation Estimation ---
class ValuationTimeSeriesPoint(BaseModel):
    date: str = Field(
        ..., description="Date of the valuation point in ISO format (YYYY-MM-DD)"
    )
    value: float = Field(
        ..., description="The estimated valuation amount at this point in time"
    )
    currency: str = Field(
        ..., description="Currency code for the valuation (e.g., 'USD', 'EUR')"
    )
    sources: Optional[list[str]] = Field(
        None, description="list of sources or references for this valuation data point"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class ValuationEstimationResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being valued"
    )
    last_valuation: float = Field(
        ..., description="The most recent valuation amount for the company"
    )
    valuation_timeseries: list[ValuationTimeSeriesPoint] = Field(
        ..., description="Historical time series of company valuations"
    )
    last_updated: Optional[str] = Field(
        None, description="ISO date string when this valuation data was last updated"
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {
                "date": v.date,
                "value": v.value,
                "currency": v.currency,
            }
            for v in self.valuation_timeseries
        ]
        return ChartData(
            data=data,
            title=f"Valuation Over Time for {self.company_name}",
            x="date",
            y="value",
            kind="line",
        )


# --- Funding History ---
class FundingCumulativeTimeSeriesPoint(BaseModel):
    date: str
    cumulative_amount: float
    sources: Optional[list[str]] = None
    confidence: Optional[float] = None


class FundingRound(BaseModel):
    round_type: str = Field(
        ..., description="Type of funding round (e.g., 'Seed', 'Series A', 'Series B')"
    )
    value: float = Field(
        ..., description="Amount raised in this specific funding round"
    )
    currency: str = Field(..., description="Currency code for the funding round amount")
    date: Optional[str] = Field(
        None, description="Date of the funding round in ISO format (YYYY-MM-DD)"
    )
    lead_investors: Optional[list[str]] = Field(
        None,
        description="list of lead investors who participated in this funding round",
    )
    sources: Optional[list[str]] = Field(
        None, description="list of sources or references for this funding round data"
    )
    confidence: Optional[float] = Field(
        None,
        description="Confidence score between 0 and 1 for the accuracy of this data point",
    )


class FundingHistoryResponse(CitationResponse):
    company_name: str = Field(
        ..., description="Official name of the company being analyzed"
    )
    funding_rounds: list[FundingRound] = Field(
        ..., description="list of individual funding rounds the company has completed"
    )
    total_funding: float = Field(
        ..., description="Total amount of funding raised across all rounds"
    )
    last_updated: Optional[str] = Field(
        None, description="ISO date string when this funding data was last updated"
    )

    def get_plot_data(self) -> ChartData:
        data = [
            {
                "round_type": f.round_type,
                "value": f.value,
                "currency": f.currency,
                "date": f.date,
            }
            for f in self.funding_rounds
        ]
        return ChartData(
            data=data,
            title=f"Funding Rounds for {self.company_name}",
            x="round_type",
            y="value",
            kind="bar",
        )
