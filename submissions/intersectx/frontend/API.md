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
    "revenue": {"company_name": "TechNova Inc.", ...},
    "expenses": null,
    "margins": null,
    "valuation": null,
    "funding": null
  },
  "linkedin_team": {"team_overview": {"company_name": "TechNova Inc.", ...}},
  "market_analysis": {"market_trends": {"summary": "Cloud market is growing rapidly.", ...}},
  "partnership_network": {"partner_list": {"company_name": "TechNova Inc.", ...}},
  "regulatory_compliance": {"compliance_overview": {"company_name": "TechNova Inc.", ...}},
  "customer_sentiment": {"sentiment_summary": {"company_name": "TechNova Inc.", ...}},
  "risk_analysis": {"regulatory_risks": {"company_name": "TechNova Inc.", ...}}
}
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

# (Continue with similar updates for Market Analysis, LinkedIn Team, Partnership Network, Regulatory Compliance, Customer Sentiment, Risk Analysis, and other endpoints, using the latest request/response models from the codebase. For each, include the request model, sample request JSON, and response model as above.)

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

# Chat Service API Contract

This document describes the endpoints, request/response models, and sample payloads for the VentureInsights Chat Service API. The structure and detail match the Research API documentation style.

---

## Endpoints

### 1. Get Threads

**Endpoint:**
```
GET /chat/threads
```

**Query Parameters:**
- `limit` (int, default=10): Limit number of threads returned (1-100)
- `offset` (int, default=0): Offset for pagination
- `user_id` (str, optional): User ID
- `sort_by` (str, default="updated_at"): Field to sort by (`updated_at` or `created_at`)
- `sort_order` (str, default="desc"): Sort order (`asc` or `desc`)

**Response Model:**
```python
class ThreadSummary(ChatThreadBase):
    last_message: Optional[LastMessage] = None
    message_count: Optional[int] = 0

class LastMessage(BaseModel):
    content: str
    sender: Literal["user", "assistant"]
    timestamp: datetime
    user_id: Optional[str] = None
    user_name: Optional[str] = None
```

**Sample Response:**
```json
[
  {
    "id": "thread-123",
    "title": "Market Analysis",
    "created_by": "user1@example.com",
    "created_at": "2025-05-24T12:00:00Z",
    "updated_at": "2025-05-24T13:00:00Z",
    "last_message": {
      "content": "What are the latest trends?",
      "sender": "user",
      "timestamp": "2025-05-24T13:00:00Z",
      "user_id": "user1@example.com",
      "user_name": "User One"
    },
    "message_count": 5
  }
]
```

---

### 2. Create Thread

**Endpoint:**
```
POST /chat/threads
```

**Query Parameters:**
- `user_id` (str, optional): User ID

**Request Model:**
```python
class CreateThreadRequest(BaseModel):
    title: Optional[str] = None
    created_by: Optional[str] = None
```

**Sample Request:**
```json
{
  "title": "Q2 Financials",
  "created_by": "user2@example.com"
}
```

**Response:**
```json
{
  "thread_id": "thread-456"
}
```

---

### 3. Get Thread Details

**Endpoint:**
```
GET /chat/threads/{thread_id}
```

**Path Parameter:**
- `thread_id` (str): Unique thread identifier

**Query Parameters:**
- `user_id` (str, optional): User ID

**Response Model:**
```python
class ChatThreadWithMessages(ChatThreadBase):
    messages: list[MessageResponse]

class MessageResponse(ChatMessageBase):
    metadata: Optional[MessageMetadata] = None
    # ... see code for full details
```

**Sample Response:**
```json
{
  "id": "thread-123",
  "title": "Market Analysis",
  "created_by": "user1@example.com",
  "created_at": "2025-05-24T12:00:00Z",
  "updated_at": "2025-05-24T13:00:00Z",
  "messages": [
    {
      "id": "msg-1",
      "content": "What are the latest trends?",
      "sender": "user",
      "timestamp": "2025-05-24T13:00:00Z",
      "metadata": null
    }
  ]
}
```

**Example: GET /chat/threads/testing-message-9**

**Request:**
```
GET http://0.0.0.0:8080/chat/threads/testing-message-9
```

**Sample Response:**
```json
{
    "id": "testing-message-9",
    "title": null,
    "created_at": null,
    "updated_at": "2025-05-24T13:20:34Z",
    "created_by": null,
    "messages": [
        {
            "id": null,
            "content": "Hi",
            "sender": "user",
            "iframe_url": null,
            "timestamp": "2025-05-24T13:19:40Z",
            "user_id": null,
            "user_name": null,
            "metadata": null
        },
        {
            "id": null,
            "content": "Hello! How can I assist you today?",
            "sender": "assistant",
            "iframe_url": null,
            "timestamp": "2025-05-24T13:19:40Z",
            "user_id": null,
            "user_name": null,
            "metadata": null
        },
        {
            "id": null,
            "content": "Tell Me revenue about facebook and apple",
            "sender": "user",
            "iframe_url": null,
            "timestamp": "2025-05-24T13:20:25Z",
            "user_id": null,
            "user_name": null,
            "metadata": null
        },
        {
            "id": null,
            "content": "Here is the revenue information for Facebook and Apple:\n\n### Facebook (Meta Platforms, Inc.)\n- **2022 Revenue**: $116.6 billion USD\n- **2023 Revenue**: $113.6 billion USD\n- **2024 Revenue**: $164.5 billion USD\n- **2025 Revenue Estimate**: $123.73 billion USD (as of May 2025)\n- **Total Revenue (2022-2025)**: $518.43 billion USD  \n- Key sources: [Business of Apps](https://www.businessofapps.com/data/facebook-statistics/), [Meta Investor News](https://investor.atmeta.com/investor-news/press-release-details/2025/Meta-Reports-Fourth-Quarter-and-Full-Year-2024-Results/default.aspx).\n\n### Apple\n- **Q4 2024 Revenue**: $124.3 billion USD\n- **Q1 2025 Revenue**: $95.4 billion USD\n- **2023 Annual Revenue**: $383.3 billion USD  \n- **Total Recent Revenue**: $219.7 billion USD (covering 2023 & Q1-Q2 2025)\n- Key sources: [Apple Newsroom](https://www.apple.com/newsroom/2025/05/apple-reports-second-quarter-results/), [Statista](https://www.statista.com/statistics/263426/apples-global-revenue-since-1st-quarter-2005/).\n\nLet me know if you'd like further breakdowns or projections!",
            "sender": "assistant",
            "iframe_url": [
                "https://6831ba304cb23ac640f8caf0--golden-dolphin-728ed5.netlify.app/charts/8218eb81-28e2-47a5-93ed-9e40c099ea26.html",
                "https://68319cd58988c68893fc5e33--golden-dolphin-728ed5.netlify.app/charts/b3887da3-b6b9-43c2-bde3-7015bc9d5ff1.html"
            ],
            "timestamp": "2025-05-24T13:20:30Z",
            "user_id": null,
            "user_name": null,
            "metadata": null
        }
    ]
}
```

---

### 4. Delete Thread

**Endpoint:**
```
DELETE /chat/threads/{thread_id}
```

**Path Parameter:**
- `thread_id` (str): Unique thread identifier

**Query Parameters:**
- `user_id` (str, optional): User ID

**Response:**
```json
{
  "success": true
}
```

---

### 5. Send Message to Thread

**Endpoint:**
```
POST /chat/threads/{thread_id}/messages
```

**Path Parameter:**
- `thread_id` (str): Unique thread identifier

**Request Model:**
```python
class SendMessageRequest(BaseModel):
    content: str
    attachments: Optional[List[AttachmentRequest]] = None
    user_id: Optional[str] = None
    user_name: Optional[str] = None

class AttachmentRequest(BaseModel):
    id: str
```

**Sample Request:**
```json
{
  "content": "Please summarize the last quarter's revenue.",
  "user_id": "user2@example.com",
  "user_name": "User Two"
}
```

**Response Model:**
```python
class MessageResponse(ChatMessageBase):
    metadata: Optional[MessageMetadata] = None
    # ... see code for full details
```

**Sample Response:**
```json
{
  "id": "ebb579c5-2caa-4aad-8c7c-356a6eddc7b5",
  "content": "Facebook's revenue over recent years is summarized below:\n\n- **2022**: $116.6 billion USD  \n- **2023**: $113.6 billion USD  \n- **2024**: $164.5 billion USD  \n- **2025 (Projection)**: $123.73 billion USD (as of the latest update)\n\n### Total Revenue (2022-2025): $518.43 billion USD\n\nYou can explore detailed visualizations from this data [HERE](https://6831ba304cb23ac640f8caf0--golden-dolphin-728ed5.netlify.app/charts/8218eb81-28e2-47a5-93ed-9e40c099ea26.html).\n\nFor further updates or deeper insights, feel free to ask!",
  "sender": "assistant",
  "iframe_url": [
    "https://6831ba304cb23ac640f8caf0--golden-dolphin-728ed5.netlify.app/charts/8218eb81-28e2-47a5-93ed-9e40c099ea26.html"
  ],
  "timestamp": "2025-05-24T17:53:19.425687",
  "user_id": null,
  "user_name": null,
  "metadata": {
    "tools": [
      {
        "tool_call_id": "call_GdoWwgZxpToCV9lRB0cQHTuY",
        "tool_name": "revenue_analysis",
        "tool_args": {
          "company_name": "Facebook"
        },
        "tool_call_error": false,
        "result": "{...}",
        "metrics": {
          "time": 23.797636041010264
        },
        "stop_after_tool_call": false,
        "created_at": 1748089364,
        "requires_confirmation": null,
        "confirmed": null,
        "confirmation_note": null,
        "requires_user_input": null,
        "user_input_schema": null,
        "external_execution_required": null
      }
    ],
    "formatted_tool_calls": [
      "revenue_analysis(company_name=Facebook)"
    ],
    "citations": null,
    "messages": [
      {
        "role": "user",
        "content": "Tell Me revenue about facebook"
      },
      {
        "role": "assistant",
        "content": null
      },
      {
        "role": "tool",
        "content": "{...}"
      },
      {
        "role": "assistant",
        "content": "Facebook's revenue over recent years is summarized below: ..."
      }
    ],
    "model": "gpt-4o"
  }
}
```
