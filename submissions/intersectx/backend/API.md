# API Documentation

This document describes the request and response models for all endpoints in the Venture Insights MCP system. For each POST endpoint, a sample request JSON is provided.

---

## Research API

### /research/{company_name} (GET)
**Request:**
- Path parameter: company_name (str)

**Request Model (for future extensibility):**
```python
class ResearchRequest(BaseModel):
    company_name: str
```

**Sample Request:**
```
GET /research/TechNova%20Inc.
```

**Response Model:**
```python
class ResearchResponse(BaseModel):
    company_name: str
    finance: Optional[FinanceResponse] = None
    linkedin_team: Optional[LinkedInTeamResponse] = None
    market_analysis: Optional[MarketAnalysisResponse] = None
    partnership_network: Optional[PartnershipNetworkResponse] = None
    regulatory_compliance: Optional[RegulatoryComplianceResponse] = None
    customer_sentiment: Optional[CustomerSentimentResponse] = None
    risk_analysis: Optional[RiskAnalysisResponse] = None

class FinanceResponse(BaseModel):
    revenue: Optional[RevenueAnalysisResponse] = None
    expenses: Optional[ExpenseAnalysisResponse] = None
    margins: Optional[ProfitMarginsResponse] = None
    valuation: Optional[ValuationEstimationResponse] = None
    funding: Optional[FundingHistoryResponse] = None

# ... (see below for all nested response models)
```

**Sample Response:**
```json
{
  "company_name": "TechNova Inc.",
  "finance": {
    "revenue": {
      "company_name": "TechNova Inc.",
      "revenue_timeseries": [
        {
          "currency": "USD",
          "period_start": "2023-01-01",
          "period_end": "2023-12-31",
          "value": 1000000.0,
          "sources": ["https://finance.example.com"],
          "confidence": 0.9
        }
      ],
      "total_revenue": 1000000.0,
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/revenue"
    },
    "expenses": {
      "company_name": "TechNova Inc.",
      "expenses": [
        {"category": "R&D", "value": 200000.0, "currency": "USD", "sources": ["https://finance.example.com/expenses"], "confidence": 0.8},
        {"category": "Marketing", "value": 150000.0, "currency": "USD", "sources": ["https://finance.example.com/expenses"], "confidence": 0.7}
      ],
      "total_expense": 350000.0,
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/expenses"
    },
    "margins": {
      "company_name": "TechNova Inc.",
      "margins": [
        {"margin_type": "Gross", "value": 0.6, "currency": "USD", "sources": ["https://finance.example.com/margins"], "confidence": 0.85},
        {"margin_type": "Net", "value": 0.2, "currency": "USD", "sources": ["https://finance.example.com/margins"], "confidence": 0.8}
      ],
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/margins"
    },
    "valuation": {
      "company_name": "TechNova Inc.",
      "last_valuation": 5000000.0,
      "valuation_timeseries": [
        {"date": "2023-01-01", "value": 4000000.0, "currency": "USD", "sources": ["https://finance.example.com/valuation"], "confidence": 0.9},
        {"date": "2023-12-31", "value": 5000000.0, "currency": "USD", "sources": ["https://finance.example.com/valuation"], "confidence": 0.95}
      ],
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/valuation"
    },
    "funding": {
      "company_name": "TechNova Inc.",
      "funding_rounds": [
        {"round_type": "Seed", "value": 500000.0, "currency": "USD", "date": "2021-06-01", "lead_investors": ["VC Firm A"], "sources": ["https://finance.example.com/funding"], "confidence": 0.9},
        {"round_type": "Series A", "value": 2000000.0, "currency": "USD", "date": "2022-08-15", "lead_investors": ["VC Firm B"], "sources": ["https://finance.example.com/funding"], "confidence": 0.95}
      ],
      "total_funding": 2500000.0,
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/funding"
    }
  },
  "linkedin_team": {
    "team_overview": {
      "company_name": "TechNova Inc.",
      "company_description": "A leading tech company.",
      "total_employees": 200,
      "roles_breakdown": [
        {"role": "Engineer", "count": 100, "percentage": 50.0, "sources": [1], "confidence": 0.9},
        {"role": "Product", "count": 50, "percentage": 25.0, "sources": [1], "confidence": 0.8},
        {"role": "Sales", "count": 50, "percentage": 25.0, "sources": [1], "confidence": 0.7}
      ],
      "locations": ["San Francisco", "New York"],
      "key_hiring_areas": ["AI", "Cloud"],
      "growth_rate": 0.15,
      "sources": ["https://linkedin.com/company/example"],
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/team_overview"
    },
    "individual_performance": {
      "company_name": "TechNova Inc.",
      "individual_name": "Jane Doe",
      "title": "CTO",
      "image_url": "https://linkedin.com/jane.jpg",
      "tenure_years": 3.5,
      "performance_metrics": [
        {"metric": "Leadership", "value": 9.5, "sources": [1], "confidence": 0.95},
        {"metric": "Technical Skill", "value": 9.0, "sources": [1], "confidence": 0.9}
      ],
      "previous_companies": [
        {"name": "BigTech", "title": "Engineer", "duration": "2 years", "dates": "2018-2020"}
      ],
      "key_strengths": ["Leadership", "AI Expertise"],
      "development_areas": ["Public Speaking"],
      "education": [
        {"institution": "MIT", "degree": "PhD", "field_of_study": "CS", "dates": "2010-2015"}
      ],
      "sources": ["https://linkedin.com/jane"],
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/individual_performance"
    },
    "org_structure": {
      "company_name": "TechNova Inc.",
      "org_chart": [
        {"name": "Alice Smith", "title": "CEO", "department": "Executive", "linkedin_url": "https://linkedin.com/alice", "direct_reports": ["Bob Jones", "Carol Lee"]},
        {"name": "Bob Jones", "title": "CTO", "department": "Engineering", "linkedin_url": "https://linkedin.com/bob", "reports_to": "Alice Smith"},
        {"name": "Carol Lee", "title": "CFO", "department": "Finance", "linkedin_url": "https://linkedin.com/carol", "reports_to": "Alice Smith"}
      ],
      "ceo": "Alice Smith",
      "departments": [
        {"name": "Engineering", "head": "Bob Jones", "employee_count": 100},
        {"name": "Finance", "head": "Carol Lee", "employee_count": 30}
      ],
      "leadership_team": [
        {"name": "Alice Smith", "title": "CEO", "linkedin_url": "https://linkedin.com/alice", "department": "Executive"},
        {"name": "Bob Jones", "title": "CTO", "linkedin_url": "https://linkedin.com/bob", "department": "Engineering"}
      ],
      "sources": ["https://linkedin.com/orgstructure"],
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/org_structure"
    },
    "team_growth": {
      "company_name": "TechNova Inc.",
      "team_growth_timeseries": [
        {"period_start": "2022-01-01", "period_end": "2022-12-31", "hires": 60, "attrition": 10, "net_growth": 50, "growth_rate": 0.25, "sources": [1], "confidence": 0.9}
      ],
      "total_hires": 60,
      "total_attrition": 10,
      "net_growth": 50,
      "growth_rate_annualized": 0.25,
      "key_hiring_areas": ["AI", "Cloud"],
      "attrition_by_department": [
        {"department": "Engineering", "attrition_count": 5, "attrition_rate": 0.05}
      ],
      "hiring_trends": [
        {"trend": "Upward", "description": "Hiring increased in 2022", "supporting_data": {"percentage": 20.0, "count": 12, "year_over_year_change": 0.2, "previous_value": 48, "current_value": 60, "description": "12 more hires than last year"}}
      ],
      "sources": ["https://linkedin.com/teamgrowth"],
      "last_updated": "2024-06-01T12:00:00Z",
      "citations": [
        {"url": "https://example.com/citation1", "title": "Sample Citation 1"},
        {"url": "https://example.com/citation2", "title": "Sample Citation 2"}
      ],
      "iframe_url": "https://charts.netlify.app/team_growth"
    }
  },
  "market_analysis": {"market_trends": {"summary": "Cloud market is growing rapidly.", ...}},
  "partnership_network": {"partner_list": {"company_name": "TechNova Inc.", ...}},
  "regulatory_compliance": {"compliance_overview": {"company_name": "TechNova Inc.", ...}},
  "customer_sentiment": {"sentiment_summary": {"company_name": "TechNova Inc.", ...}},
  "risk_analysis": {"regulatory_risks": {"company_name": "TechNova Inc.", ...}}
}
```

---

## Market Analysis API

### /market-analysis/market-trends (POST)
**Request Model:**
```python
class MarketTrendsRequest(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "industry": "Cloud Computing",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class MarketTrendsResponse(CitationResponse):
    market_size: list[MarketSize]
    summary: str
    last_updated: Optional[str] = None
    citations: list[Any]
```

### /market-analysis/competitive-analysis (POST)
**Request Model:**
```python
class CompetitiveAnalysisRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    companies_to_compare: Optional[list[str]] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global",
  "companies_to_compare": ["CompetitorX", "CompetitorY"]
}
```
**Response Model:**
```python
class CompetitiveAnalysisResponse(CitationResponse):
    top_competitors: list[CompetitorProfile]
    summary: Optional[str] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

### /market-analysis/growth-projections (POST)
**Request Model:**
```python
class GrowthProjectionsRequest(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "industry": "Cloud Computing",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class GrowthProjectionsResponse(CitationResponse):
    projections_timeseries: list[GrowthProjectionTimeSeriesPoint]
    summary: Optional[str] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

### /market-analysis/regional-trends (POST)
**Request Model:**
```python
class RegionalTrendsRequest(BaseModel):
    company_name: str
    industry: Optional[str] = None
    regions_of_interest: Optional[list[str]] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "industry": "Cloud Computing",
  "regions_of_interest": ["US", "EU"],
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class RegionalTrendsResponse(CitationResponse):
    regional_trends: list[RegionalTrendPoint]
    summary: Optional[str] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

---

## Finance Agent

### /finance/revenue-analysis
**Request Model:**
```python
class RevenueAnalysisRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    granularity: Optional[str] = "year"  # year, quarter, or month
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31",
  "granularity": "quarter"
}
```
**Response Model:**
```python
class RevenueAnalysisResponse(CitationResponse):
    company_name: str
    revenue_timeseries: list[RevenueTimeSeriesPoint]
    total_revenue: Optional[float] = None
    last_updated: Optional[str] = None
    citations: list[Any]  # e.g. UrlCitation
```

---

### /finance/expense-analysis
**Request Model:**
```python
class ExpenseAnalysisRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    year: Optional[int] = None
    category: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "year": 2023,
  "category": "R&D"
}
```
**Response Model:**
```python
class ExpenseAnalysisResponse(CitationResponse):
    company_name: str
    expenses: list[ExpenseCategoryBreakdown]
    total_expense: Optional[float] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

---

### /finance/profit-margins
**Request Model:**
```python
class ProfitMarginsRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    year: Optional[int] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "year": 2023
}
```
**Response Model:**
```python
class ProfitMarginsResponse(CitationResponse):
    company_name: str
    margins: list[ProfitMarginBreakdown]
    last_updated: Optional[str] = None
    citations: list[Any]
```

---

### /finance/valuation-estimation
**Request Model:**
```python
class ValuationEstimationRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    as_of_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "as_of_date": "2024-05-01"
}
```
**Response Model:**
```python
class ValuationEstimationResponse(CitationResponse):
    company_name: str
    last_valuation: float
    valuation_timeseries: list[ValuationTimeSeriesPoint]
    last_updated: Optional[str] = None
    citations: list[Any]
```

---

### /finance/funding-history
**Request Model:**
```python
class FundingHistoryRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com"
}
```
**Response Model:**
```python
class FundingHistoryResponse(CitationResponse):
    company_name: str
    funding_rounds: list[FundingRound]
    total_funding: float
    last_updated: Optional[str] = None
    citations: list[Any]
```

---

## LinkedIn Team API

### /linkedin-team/team-overview (POST)
**Request Model:**
```python
class TeamOverviewRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com"
}
```
**Response Model:**
```python
class TeamOverviewResponse(BaseModel):
    company_name: str
    company_description: Optional[str] = None
    total_employees: int
    roles_breakdown: List[TeamRoleBreakdown]
    locations: Optional[List[str]] = None
    key_hiring_areas: Optional[List[str]] = None
    growth_rate: Optional[float] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
```

### /linkedin-team/individual-performance (POST)
**Request Model:**
```python
class IndividualPerformanceRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    individual_name: str
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "individual_name": "Alice Smith"
}
```
**Response Model:**
```python
class IndividualPerformanceResponse(BaseModel):
    company_name: str
    individual_name: str
    title: Optional[str] = None
    image_url: Optional[str] = None
    tenure_years: Optional[float] = None
    performance_metrics: List[IndividualPerformanceMetric]
    previous_companies: Optional[List[PreviousCompany]] = None
    key_strengths: Optional[List[str]] = None
    development_areas: Optional[List[str]] = None
    education: Optional[List[Education]] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
```

### /linkedin-team/org-structure (POST)
**Request Model:**
```python
class OrgStructureRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com"
}
```
**Response Model:**
```python
class OrgStructureResponse(BaseModel):
    company_name: str
    org_chart: List[OrgNode]
    ceo: Optional[str] = None
    departments: Optional[List[Department]] = None
    leadership_team: Optional[List[LeadershipTeamMember]] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
```

### /linkedin-team/team-growth (POST)
**Request Model:**
```python
class TeamGrowthRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class TeamGrowthResponse(BaseModel):
    company_name: str
    team_growth_timeseries: List[TeamGrowthTimeSeriesPoint]
    total_hires: int
    total_attrition: int
    net_growth: int
    growth_rate_annualized: Optional[float] = None
    key_hiring_areas: Optional[List[str]] = None
    attrition_by_department: Optional[List[DepartmentAttrition]] = None
    hiring_trends: Optional[List[HiringTrend]] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
```

---

## Files API

### /files/upload (POST)
**Request:**
- Multipart/form-data with fields:
  - file: The file to upload (PDF, PPTX, etc.)
  - company_name: str (form field)

**Sample Request (form-data):**
- file: (binary file)
- company_name: "Acme Corp"

**Response:**
```python
{
  "cloud_url": "https://res.cloudinary.com/yourcloud/abc123.pdf",
  "company": {
    "name": "Acme Corp"
  }
}
```

---

### /files/get-files/{company_name} (GET)
**Request:**
- Path parameter: company_name (str)

**Sample Request:**
```
GET /files/get-files/Acme%20Corp
```

**Response Model:**
```python
class CompanyDocumentsResponse(BaseModel):
    company_name: str
    document_urls: List[str]
```
**Sample Response:**
```json
{
  "company_name": "Acme Corp",
  "document_urls": [
    "https://res.cloudinary.com/yourcloud/abc123.pdf",
    "https://res.cloudinary.com/yourcloud/xyz456.pdf"
  ]
}
```

---

### /files/download (GET)
**Request:**
- Query parameter: cloud_url (str)

**Sample Request:**
```
GET /files/download?cloud_url=https://res.cloudinary.com/yourcloud/abc123.pdf
```

**Response:**
- Returns the file as an attachment (binary response)

---

# (The rest of the agents and endpoints will follow the same format. This file will be continued to include all request/response models and sample POST request JSONs for each endpoint.) 

---

## Customer Sentiment API

### /customer-sentiment/sentiment-summary (POST)
**Request Model:**
```python
class SentimentSummaryRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    product: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "product": "Main Product",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class SentimentSummaryResponse(CitationResponse):
    company_name: str
    product: Optional[str] = None
    region: Optional[str] = None
    sentiment_score: float
    sentiment_breakdown: SentimentBreakdown
    sentiment_timeseries: List[SentimentTimeSeriesPoint]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

### /customer-sentiment/customer-feedback (POST)
**Request Model:**
```python
class CustomerFeedbackRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    product: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "product": "Main Product",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class CustomerFeedbackResponse(CitationResponse):
    company_name: str
    product: Optional[str] = None
    region: Optional[str] = None
    feedback_items: List[CustomerFeedbackItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

### /customer-sentiment/brand-reputation (POST)
**Request Model:**
```python
class BrandReputationRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class BrandReputationResponse(CitationResponse):
    company_name: str
    region: Optional[str] = None
    reputation_score: float
    reputation_timeseries: List[BrandReputationTimeSeriesPoint]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[str] = None
    citations: list[Any]
```

### /customer-sentiment/sentiment-comparison (POST)
**Request Model:**
```python
class SentimentComparisonRequest(BaseModel):
    company_name: str
    competitors: List[str]
    domain: Optional[str] = None
    product: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "competitors": ["CompetitorX", "CompetitorY"],
  "domain": "tecnova.com",
  "product": "Main Product",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class SentimentComparisonResponse(CitationResponse):
    company_name: str
    product: Optional[str] = None
    region: Optional[str] = None
    competitors: List[str]
    target_sentiment: CompanySentimentData
    competitor_sentiments: List[CompanySentimentData]
    summary: Optional[str] = None
    confidence: float
    last_updated: str
    citations: list[Any]
```

---

## Partnership Network API

### /partnership-network/partner-list (POST)
**Request Model:**
```python
class PartnerListRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class PartnerListResponse(BaseModel):
    company_name: str
    partners: List[PartnerItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /partnership-network/strategic-alliances (POST)
**Request Model:**
```python
class StrategicAlliancesRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class StrategicAlliancesResponse(BaseModel):
    company_name: str
    alliances: List[AllianceImpactItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /partnership-network/network-strength (POST)
**Request Model:**
```python
class NetworkStrengthRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class NetworkStrengthResponse(BaseModel):
    company_name: str
    network_metrics: List[NetworkMetricItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /partnership-network/partnership-trends (POST)
**Request Model:**
```python
class PartnershipTrendsRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class PartnershipTrendsResponse(BaseModel):
    company_name: str
    partnership_trends_timeseries: List[PartnershipTrendTimeSeriesPoint]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

---

## Regulatory Compliance API

### /regulatory-compliance/compliance-overview (POST)
**Request Model:**
```python
class ComplianceOverviewRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class ComplianceOverviewResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    regulations: List[RegulationItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /regulatory-compliance/violation-history (POST)
**Request Model:**
```python
class ViolationHistoryRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global",
  "start_date": "2023-01-01",
  "end_date": "2023-12-31"
}
```
**Response Model:**
```python
class ViolationHistoryResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    violations: List[ViolationItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /regulatory-compliance/compliance-risk (POST)
**Request Model:**
```python
class ComplianceRiskRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class ComplianceRiskResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[ComplianceRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /regulatory-compliance/regional-compliance (POST)
**Request Model:**
```python
class RegionalComplianceRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    regions: Optional[List[str]] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "regions": ["US", "EU"]
}
```
**Response Model:**
```python
class RegionalComplianceResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    regional_compliance: List[RegionalComplianceItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

---

## Risk Analysis API

### /risk-analysis/regulatory-risks (POST)
**Request Model:**
```python
class RegulatoryRisksRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class RegulatoryRisksResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[RegulatoryRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /risk-analysis/market-risks (POST)
**Request Model:**
```python
class MarketRisksRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class MarketRisksResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[MarketRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /risk-analysis/operational-risks (POST)
**Request Model:**
```python
class OperationalRisksRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class OperationalRisksResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[OperationalRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

### /risk-analysis/legal-risks (POST)
**Request Model:**
```python
class LegalRisksRequest(BaseModel):
    company_name: str
    domain: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
```
**Sample Request JSON:**
```json
{
  "company_name": "TechNova Inc.",
  "domain": "tecnova.com",
  "industry": "Cloud Computing",
  "region": "Global"
}
```
**Response Model:**
```python
class LegalRisksResponse(BaseModel):
    company_name: str
    industry: Optional[str] = None
    region: Optional[str] = None
    risks: List[LegalRiskItem]
    summary: Optional[str] = None
    sources: Optional[List[str]] = None
    last_updated: Optional[datetime] = None
```

---

## Chat API

### /chat/threads (GET, POST)
**GET Request:**
- Query parameters:
  - limit (int, default 10, min 1, max 100)
  - offset (int, default 0, min 0)
  - user_id (str, optional) - User ID
  - sort_by (str, default "updated_at") - Field to sort by (updated_at or created_at)
  - sort_order (str, default "desc") - Sort order (asc or desc)

**Response Model:**
```python
List[ThreadSummary]
```

**POST Request:**
- No body required

**Response:**
```json
{
  "thread_id": "uuid-string"
}
```

### /chat/threads/{thread_id} (GET, DELETE)
**GET Request:**
- Path parameters: thread_id (str)
- Query parameters: user_id (str, optional)

**GET Response Model:**
```python
class ChatThreadWithMessages(ChatThreadBase):
    messages: list[MessageResponse]
```

**DELETE Request:**
- Path parameters: thread_id (str)
- Query parameters: user_id (str, optional)

**DELETE Response:**
```json
{
  "success": true
}
```

### /chat/threads/{thread_id}/messages (POST)
**Request:**
- Path parameters: thread_id (str)
- Query parameters: stream (bool, default False)
- Body:
```python
class SendMessageRequest(BaseModel):
    content: str
    user_id: Optional[str] = None
    user_name: Optional[str] = None
```

**Response Model:**
```python
class MessageResponse(ChatMessageBase):
    metadata: Optional[MessageMetadata] = None
```

---

## Companies API

### /companies/search (GET)
**Request:**
- Query parameter: limit (int, optional)

**Response Model:**
```python
class CompanyBaseInfo(BaseModel):
    name: str
    logo: str
    founder: str
    headquarters: str
    founding_date: datetime
    members_count: int
```

### /companies/{companyName}/analysis (GET)
**Request:**
- Path parameter: companyName (str)

**Response Model:**
```python
class CompanyAnalysisFullResponse(BaseModel):
    company: CompanyAnalysisCompanyInfo
    analysis: CompanyAnalysis
```

---

## News API

### /news/trending (GET)
**Request:**
- Query parameters: company_name (str, optional), limit (int, optional), domain (str, optional)

**Response Model:**
```python
class NewsItem(BaseModel):
    title: str
    url: str
    published_at: str
    summary: Optional[str] = None
    company_name: Optional[str] = None
    domain: Optional[str] = None
```

---

## Auth API

### /auth/signup (POST)
**Request Model:**
```python
class SignUpRequest(BaseModel):
    email: str
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
```
**Response:**
- Returns user info or token (implementation-specific)

### /auth/login (POST)
**Request Model:**
```python
class LoginRequest(BaseModel):
    email: str
    password: str
```
**Response:**
- Returns user info or token (implementation-specific)

--- 