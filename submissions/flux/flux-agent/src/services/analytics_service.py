import json
import os
from typing import List, Dict, Any, Optional
from datetime import datetime
import random

# Import agent and model classes
from agno.agent import Agent
from agno.models.openai import OpenAIChat
# from agno.models.groq import GroqChat  # Not available in the installed version

from models.analytics_models import (
    ChartGenerationRequest, ChartGenerationResponse, ChartSuggestion, ChartConfig,
    ChartDataRequest, ChartDataResponse, ChartDataPoint
)
from constants.enums import ModelConfig, ErrorMessages
from utils.logger import get_logger

logger = get_logger()

class AnalyticsService:
    """Service for generating charts and analytics insights based on form data"""
    
    def __init__(self, database_service=None):
        logger.info("Initializing AnalyticsService")
        self.database_service = database_service
        self._setup_chart_agent()
    
    def _setup_chart_agent(self):
        """Set up the AI agent for chart generation"""
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            raise ValueError(ErrorMessages.MISSING_API_KEY)
        
        logger.info("Setting up chart agent with OpenAI model")
        self.chart_agent = Agent(
            model=OpenAIChat(id=ModelConfig.GPT_4_NANO, api_key=openai_api_key),
            description="Expert data analyst that generates chart suggestions based on form data",
            instructions=self._get_chart_generation_instructions(),
            response_model=self._get_chart_suggestion_model(),
            use_json_mode=True,
            markdown=True,
            debug_mode=True,
        )
    
    def _get_chart_generation_instructions(self) -> List[str]:
        return [
            "You are an expert data analyst that generates chart suggestions based on form data.",
            "Analyze the user's request and form fields to recommend the most relevant visualizations.",
            "IMPORTANT: Only use these supported chart types: bar, pie, line, area, doughnut",
            "Choose appropriate chart types based on data types:",
            "- Use pie or doughnut charts for categorical data distribution (select/radio fields)",
            "- Use bar charts for comparing categories or discrete values",
            "- Use line charts for time series data or trends over createdAt",
            "- Use area charts for cumulative data or filled time series",
            "CRITICAL: Only use fields that are actually provided in the AVAILABLE FIELDS list.",
            "Generate SQL queries that work with PostgreSQL and properly filter by form ID.",
            "For JSONB data access, use: data->>'field_id' for text or CAST(data->>'field_id' AS numeric) for numbers.",
            "Always include proper WHERE clauses to filter by formId.",
            "Use the exact field IDs provided in the AVAILABLE FIELDS list.",
            "For aggregation, specify methods like 'COUNT', 'SUM', 'AVG', 'GROUP BY', etc.",
            "If no specific fields are available, create a basic response count chart using COUNT(*).",
            "Provide clear titles, axis labels, and data transformation instructions.",
            "Score suggestions based on relevance to the user's request (1-10 scale).",
            "IMPORTANT: Do not reference fields that don't exist in the AVAILABLE FIELDS list.",
        ]
    
    def _get_chart_suggestion_model(self):
        from pydantic import BaseModel, Field
        
        class AgnoChartConfig(BaseModel):
            type: str = Field(..., description="Chart type - MUST be one of: bar, pie, line, area, doughnut")
            title: str = Field(..., description="Chart title")
            data_source: str = Field(..., description="SQL query to fetch data")
            aggregation: str = Field(..., description="Data aggregation method (COUNT, SUM, AVG, etc.) - REQUIRED")
            x_axis: Optional[str] = Field(None, description="X-axis configuration")
            y_axis: Optional[str] = Field(None, description="Y-axis configuration")
            color_field: Optional[str] = Field(None, description="Field for color coding")
        
        class AgnoChartSuggestion(BaseModel):
            id: str = Field(..., description="Unique identifier for the suggestion")
            title: str = Field(..., description="Human-readable title")
            description: str = Field(..., description="Brief description of what this chart shows")
            chart_config: AgnoChartConfig = Field(..., description="Chart configuration")
            confidence_score: float = Field(..., description="Confidence score (0-10)")
            reasoning: str = Field(..., description="Why this chart is relevant")
        
        class AgnoChartResponse(BaseModel):
            suggestions: List[AgnoChartSuggestion] = Field(..., description="List of chart suggestions")
        
        return AgnoChartResponse
    
    def generate_chart_suggestions(
        self, 
        request: ChartGenerationRequest,
        form_title: str = None,
        form_description: str = None,
        fields: List[Dict[str, Any]] = None,
        total_responses: int = None
    ) -> ChartGenerationResponse:
        """Generate chart suggestions based on user prompt and form data"""
        
        try:
            # Fetch real form data from database
            actual_form_title, actual_form_description, actual_fields, actual_total_responses = self._fetch_form_data(request.form_id)
            
            # Use fetched data, fallback to passed parameters if needed
            final_form_title = actual_form_title or form_title or ""
            final_form_description = actual_form_description or form_description or ""
            final_fields = actual_fields if actual_fields else (fields or [])
            final_total_responses = actual_total_responses if actual_total_responses is not None else (total_responses or 0)
            
            # Generate AI-powered suggestions
            ai_suggestions = self._generate_ai_chart_suggestions(
                request.prompt, request.form_id, final_form_title, final_form_description, final_fields, final_total_responses
            )
            
            return ChartGenerationResponse(
                prompt=request.prompt,
                form_id=request.form_id,
                total_responses=final_total_responses,
                available_fields=final_fields,
                suggestions=ai_suggestions
            )
            
        except Exception as e:
            logger.error(f"Error generating chart suggestions: {e}")
            raise
    
    def _generate_ai_chart_suggestions(
        self, prompt: str, form_id: str, form_title: str, form_description: str, 
        fields: List[Dict[str, Any]], total_responses: int
    ) -> List[ChartSuggestion]:
        """Generate chart suggestions using AI agent"""
        
        try:
            # Build comprehensive prompt for the AI agent
            agent_prompt = self._build_chart_agent_prompt(
                prompt, form_id, form_title, form_description, fields, total_responses
            )
            
            # Get response from AI agent
            response = self.chart_agent.run(agent_prompt)
            
            # Parse the response - following cookbook pattern
            if not hasattr(response, 'content'):
                logger.warning(f"No content in AI response: {response}")
                return []
            
            # The response.content should be the AgnoChartResponse model directly
            ai_response = response.content
            
            # Extract suggestions - should be a list of AgnoChartSuggestion models
            if hasattr(ai_response, 'suggestions'):
                ai_suggestions = ai_response.suggestions
            else:
                logger.warning(f"No suggestions in AI response: {ai_response}")
                return []
            
            # Convert AI suggestions to our format - just take the first one
            chart_suggestions = []
            if ai_suggestions:
                ai_suggestion = ai_suggestions[0]  # Just take the first suggestion
                
                # The ai_suggestion should be an AgnoChartSuggestion model
                # Extract chart config from AI response
                ai_chart_config = ai_suggestion.chart_config
                
                # Map the internal AgnoChartConfig to the expected ChartConfig format
                # Fix: Ensure data_transform is always a string, never None
                aggregation = ai_chart_config.aggregation
                data_transform = aggregation if aggregation is not None else 'COUNT'
                
                # Validate and convert chart type to ensure UI compatibility
                validated_chart_type = self._validate_and_convert_chart_type(ai_chart_config.type)
                
                chart_config = ChartConfig(
                    field_id=self._extract_field_id_from_sql(ai_chart_config.data_source or ''),
                    field_label=ai_chart_config.title,
                    sql_query=ai_chart_config.data_source or '',
                    data_transform=data_transform,
                    x_axis_label=ai_chart_config.x_axis,
                    y_axis_label=ai_chart_config.y_axis,
                    filters={"color_field": ai_chart_config.color_field} if ai_chart_config.color_field else None
                )
                
                chart_suggestion = ChartSuggestion(
                    title=ai_suggestion.title,
                    type=validated_chart_type,
                    description=ai_suggestion.description,
                    config=chart_config,
                    confidence=ai_suggestion.confidence_score / 10.0  # Convert to 0-1 scale
                )
                
                chart_suggestions.append(chart_suggestion)
            
            logger.info(f"Generated {len(chart_suggestions)} AI chart suggestion")
            return chart_suggestions
            
        except Exception as e:
            logger.error(f"Error in AI chart generation: {e}")
            raise
    
    def _validate_and_convert_chart_type(self, chart_type: str) -> str:
        """Validate chart type and convert unsupported types to supported ones"""
        supported_types = ['bar', 'pie', 'line', 'area', 'doughnut']
        
        # If already supported, return as-is
        if chart_type in supported_types:
            return chart_type
        
        # Convert unsupported types to supported equivalents
        type_mapping = {
            'histogram': 'bar',  # Convert histogram to bar chart
            'scatter': 'line',   # Convert scatter to line chart
            'column': 'bar',     # Convert column to bar chart
            'donut': 'doughnut', # Convert donut to doughnut
            'spline': 'line',    # Convert spline to line chart
            'bubble': 'pie',     # Convert bubble to pie chart
        }
        
        converted_type = type_mapping.get(chart_type.lower(), 'bar')
        logger.warning(f"Converted unsupported chart type '{chart_type}' to '{converted_type}'")
        return converted_type
    
    def _extract_field_id_from_sql(self, sql_query: str) -> str:
        """Extract field ID from SQL query for field_id requirement"""
        import re
        # Look for patterns like data->>'field_id' in the SQL
        match = re.search(r"data->>\'([^']+)\'", sql_query)
        if match:
            return match.group(1)
        # Fallback to a default if no field found
        return "unknown_field"
    
    def _build_chart_agent_prompt(
        self, prompt: str, form_id: str, form_title: str, form_description: str, 
        fields: List[Dict[str, Any]], total_responses: int
    ) -> str:
        """Build a comprehensive prompt for the chart generation agent"""
        
        # Build field descriptions with types and sample data
        field_descriptions = []
        sample_data = {}
        
        for field in fields:
            field_type = field.get('type', 'text')
            field_id = field.get('id', '')
            field_label = field.get('label', '')
            
            desc = f"- {field_label} (ID: '{field_id}', Type: {field_type})"
            if field.get('options'):
                options = field.get('options', [])
                desc += f", Options: {options}"
                # Add sample value for the JSON
                if options:
                    sample_data[field_id] = options[0] if isinstance(options, list) else str(options)
            elif field_type == 'number':
                desc += " - Numeric field for mathematical operations"
                sample_data[field_id] = 25
            elif field_type == 'email':
                desc += " - Email address field"
                sample_data[field_id] = "user@example.com"
            elif field_type == 'date':
                desc += " - Date field (YYYY-MM-DD format)"
                sample_data[field_id] = "2024-01-15"
            else:
                desc += " - Text field"
                sample_data[field_id] = "Sample text response"
                
            field_descriptions.append(desc)
        
        fields_text = "\n".join(field_descriptions) if field_descriptions else "No fields available"
        sample_json = json.dumps(sample_data, indent=2) if sample_data else '{"response": "No fields defined yet"}'
        
        return f"""Generate chart suggestions for a form based on the following information:

USER REQUEST: "{prompt}"

FORM DETAILS:
- Form ID: {form_id}
- Title: {form_title or "Untitled Form"}
- Description: {form_description or "No description"}
- Total Responses: {total_responses}

AVAILABLE FIELDS:
{fields_text}

SAMPLE DATA STRUCTURE:
The 'data' JSONB column contains form responses in this format:
{sample_json}

DATABASE SCHEMA:
The form data is stored in a PostgreSQL database with the following structure:
- Table: "FormResponse"
  - "id": Primary key (UUID)
  - "formId": The ID of the form ({form_id})
  - "createdAt": Timestamp when the response was submitted
  - "data": JSONB column containing all form field values where keys are the field IDs

SQL QUERY EXAMPLES:
- For categorical data: SELECT data->>'field_id' AS category, COUNT(*) AS count FROM "FormResponse" WHERE "formId" = '{form_id}' GROUP BY category
- For numeric data: SELECT CAST(data->>'numeric_field' AS numeric) AS value FROM "FormResponse" WHERE "formId" = '{form_id}'
- For time trends: SELECT DATE(createdAt) AS date, COUNT(*) AS responses FROM "FormResponse" WHERE "formId" = '{form_id}' GROUP BY date ORDER BY date
- Basic count: SELECT COUNT(*) AS total_responses FROM "FormResponse" WHERE "formId" = '{form_id}'

REQUIREMENTS:
1. CRITICAL: Chart type MUST be one of: bar, pie, line, area, doughnut (no other types allowed)
2. Generate 1 chart suggestion that best addresses the user's request
3. ONLY use field IDs that exist in the AVAILABLE FIELDS list above
4. If no fields are available, create a basic response count or time-based chart
5. Choose appropriate chart types based on the data types shown
6. Ensure SQL queries filter for this form's responses using: WHERE "formId" = '{form_id}'
7. For accessing data in the JSONB column, use: data->>'field_id' for text or CAST(data->>'field_id' AS numeric) for numbers
8. Include relevant axis labels and data transformation instructions
9. Assign confidence scores based on how well the suggestion addresses the user's request
10. IMPORTANT: Always provide an aggregation method (COUNT, SUM, AVG, etc.) - never leave it null

EXPECTED OUTPUT:
Return a JSON object with a "suggestions" array containing exactly ONE chart suggestion that matches the AgnoChartSuggestion model structure."""
    
    def execute_chart_query(self, form_id: str, chart_config: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a chart's SQL query and return formatted data"""
        
        try:
            sql_query = chart_config.get('sql_query', '')
            if not sql_query:
                raise ValueError("No SQL query provided in chart config")
            
            if not self.database_service:
                logger.warning("No database service available")
                return {"data_points": [], "total_points": 0}
            
            logger.info(f"Executing chart query: {sql_query}")
            
            # Execute the SQL query
            results = self.database_service.execute_query(sql_query)
            
            # Format results for chart consumption
            data_points = []
            for row in results:
                if isinstance(row, tuple) and len(row) >= 2:
                    # Handle tuple results (name, value)
                    data_points.append({
                        "name": str(row[0]) if row[0] is not None else "Unknown",
                        "value": int(row[1]) if row[1] is not None else 0
                    })
                elif isinstance(row, dict):
                    # Handle dict results
                    name_key = None
                    value_key = None
                    
                    # Try to find name and value keys
                    for key in row.keys():
                        if key.lower() in ['name', 'position', 'category', 'label']:
                            name_key = key
                        elif key.lower() in ['value', 'count', 'total', 'total_applicants']:
                            value_key = key
                    
                    if name_key and value_key:
                        data_points.append({
                            "name": str(row[name_key]) if row[name_key] is not None else "Unknown",
                            "value": int(row[value_key]) if row[value_key] is not None else 0
                        })
            
            logger.info(f"Formatted {len(data_points)} data points for chart")
            
            return {
                "data_points": data_points,
                "total_points": len(data_points),
                "query_executed": sql_query
            }
            
        except Exception as e:
            logger.error(f"Error executing chart query: {e}")
            raise
    
    def generate_chart_data(self, request: ChartDataRequest) -> ChartDataResponse:
        """Generate actual chart data by executing the chart's SQL query"""
        # This would integrate with the database service to execute the query
        # For now, return a placeholder response
        
        return ChartDataResponse(
            title=request.title,
            type=request.chart_type,
            config=request.config,
            data_points=[
                ChartDataPoint(name="Sample", value=100),
                ChartDataPoint(name="Data", value=200),
            ],
            total_points=2
        )
    
    def _fetch_form_data(self, form_id: str) -> tuple[str, str, List[Dict[str, Any]], int]:
        """Fetch form metadata and field information"""
        try:
            if not self.database_service:
                logger.warning("No database service available, using default values")
                return "", "", [], 0
            
            # Get form details
            form_query = 'SELECT title, description, schema FROM "Form" WHERE id = %s AND "isDeleted" = false'
            form_results = self.database_service.execute_query(form_query, (form_id,))
            
            if not form_results:
                logger.warning(f"Form {form_id} not found")
                return "", "", [], 0
            
            form_data = form_results[0]
            form_title = form_data.get('title', '')
            form_description = form_data.get('description', '')
            schema = form_data.get('schema', {})
            
            # Extract fields from schema
            fields = []
            if isinstance(schema, dict):
                if 'fields' in schema and isinstance(schema['fields'], list):
                    fields = schema['fields']
                elif isinstance(schema, list):
                    fields = schema
            
            # Get response count
            count_query = 'SELECT COUNT(*) as total FROM "FormResponse" WHERE "formId" = %s'
            count_results = self.database_service.execute_query(count_query, (form_id,))
            total_responses = count_results[0].get('total', 0) if count_results else 0
            
            logger.info(f"Found form '{form_title}' with {len(fields)} fields and {total_responses} responses")
            return form_title, form_description, fields, total_responses
            
        except Exception as e:
            logger.error(f"Error fetching form data: {e}")
            return "", "", [], 0
    
    def execute_chart_analysis(self, request: dict, user_id: str) -> dict:
        """
        Execute a chart analysis based on the provided request.
        Expects request to contain at least 'form_id' and 'chart_config'.
        Returns data in a format consistent with other chart endpoints.
        """
        try:
            form_id = request.get("form_id")
            chart_config = request.get("chart_config")
            return_csv = request.get("return_csv", False)

            if not form_id or not chart_config:
                raise ValueError("Missing 'form_id' or 'chart_config' in request.")

            # Run the chart query
            result = self.execute_chart_query(form_id, chart_config)

            # Return in a format consistent with other chart endpoints
            response = {
                "data_points": result.get("data_points", []),
                "total_points": result.get("total_points", 0),
                "query_executed": result.get("query_executed", ""),
                "return_csv": return_csv,
                "success": True,
                "message": "Chart data retrieved successfully"
            }
            return response

        except Exception as e:
            logger.error(f"Error in execute_chart_analysis: {e}")
            raise 