from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field

class ChartGenerationRequest(BaseModel):
    form_id: str
    prompt: str
    context: Optional[Dict[str, Any]] = None

class ChartConfig(BaseModel):
    field_id: str
    field_label: str
    sql_query: str
    data_transform: str
    x_axis_label: Optional[str] = None
    y_axis_label: Optional[str] = None
    filters: Optional[Dict[str, Any]] = None

class ChartSuggestion(BaseModel):
    title: str
    type: str
    description: str
    config: ChartConfig
    confidence: float = 0.5

class ChartGenerationResponse(BaseModel):
    prompt: str
    form_id: str
    total_responses: int
    available_fields: List[Dict[str, Any]] = []
    suggestions: List[ChartSuggestion] = []

class ChartDataRequest(BaseModel):
    form_id: str
    chart_type: str
    title: str
    config: ChartConfig

class ChartDataPoint(BaseModel):
    name: str
    value: float
    label: Optional[str] = None
    date: Optional[str] = None

class ChartDataResponse(BaseModel):
    title: str
    type: str
    config: ChartConfig
    data_points: List[ChartDataPoint] = []
    total_points: int = 0
    last_updated: str = Field(default_factory=lambda: datetime.now().isoformat())

class AnalyticsInsightRequest(BaseModel):
    form_id: str
    insight_type: str = "general"
    time_range: Optional[Dict[str, str]] = None

class AnalyticsInsight(BaseModel):
    title: str
    description: str
    type: str
    confidence: float
    supporting_data: Optional[List[Dict[str, Any]]] = None
    suggested_actions: Optional[List[str]] = None

class AnalyticsInsightResponse(BaseModel):
    insights: List[AnalyticsInsight] = []
    form_id: str
    analysis_period: Optional[str] = None
    data_quality_score: Optional[float] = None 