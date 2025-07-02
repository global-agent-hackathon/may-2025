from datetime import datetime, date
from typing import Optional, Type, Union
from backend.utils.cache_decorator import cacheable

from agno.agent import Agent
from pydantic import BaseModel

from backend.agents.output_parser import LLMOutputParserAgent
from backend.settings import SonarConfig, LLMConfig
from backend.utils.llm import get_model, get_sonar_model
from backend.models.response.team import (
    TeamOverviewResponse,
    IndividualPerformanceResponse,
    OrgStructureResponse,
    TeamGrowthResponse,
)
from backend.plot.factory import get_builder


class TeamService:
    def __init__(self, llm_config: LLMConfig, sonar_config: SonarConfig, netlify_agent):
        self.llm_config = llm_config
        # cache_service will be injected by the dependency injection system
        self.sonar_config = sonar_config
        self.llm_model = get_model(self.llm_config)
        self.sonar_model = get_sonar_model(self.sonar_config)
        self.llm_output_parser = LLMOutputParserAgent(self.llm_model)
        self.netlify_agent = netlify_agent

    async def _execute_llm_analysis(
        self,
        company_name: str,
        prompt: str,
        response_model: Type[BaseModel],
        agent_name: str = "AnalysisAgent",
        use_knowledge_base: bool = False,
    ) -> Union[
        TeamOverviewResponse,
        IndividualPerformanceResponse,
        OrgStructureResponse,
        TeamGrowthResponse,
    ]:
        """
        Common method to execute LLM analysis and parse the response.

        Args:
            prompt: The prompt to send to the LLM
            response_model: The Pydantic model to parse the response into
            agent_name: Name of the agent for logging/identification

        Returns:
            Parsed response model instance with citations if available
        """
        analysis_agent = Agent(
            name=agent_name,
            model=self.sonar_model,
            instructions=prompt,
        )

        if use_knowledge_base:
            analysis_agent.knowledge = self.knowledge_base
            analysis_agent.knowledge_filters = {"company_name": company_name}

        # Use the LLM to generate the content
        content = analysis_agent.run(prompt)

        # Parse the LLM output into the response model
        response = self.llm_output_parser.parse(content.content, response_model)

        # Ensure datetime fields are properly formatted as strings
        if hasattr(response, "last_updated") and response.last_updated is not None:
            if isinstance(response.last_updated, datetime):
                response.last_updated = response.last_updated.isoformat()

        # For TeamGrowthResponse, also convert period dates in timeseries
        if hasattr(response, "team_growth_timeseries"):
            for point in response.team_growth_timeseries:
                if hasattr(point, "period_start") and isinstance(
                    point.period_start, date
                ):
                    point.period_start = point.period_start.isoformat()
                if hasattr(point, "period_end") and isinstance(point.period_end, date):
                    point.period_end = point.period_end.isoformat()

        # Attach citations if response is a Pydantic model and has citations
        if hasattr(response, "citations") and hasattr(content, "citations"):
            response.citations = (
                content.citations.urls if hasattr(content.citations, "urls") else []
            )

        try:
            chart_data = response.get_plot_data()
            builder = get_builder(chart_data.kind, self.netlify_agent)
            response.iframe_url = await builder.plot(chart_data, company_name)
        except Exception:
            response.iframe_url = None

        return response

    @cacheable()
    async def get_team_overview(self, company_name: str, domain: Optional[str] = None):
        """
        Retrieve team overview data for a company from LinkedIn.
        Args:
            company_name (str): Name of the company
            domain (str, optional): Domain of the company
        Returns:
            Dict: Contains company name, total employees, roles breakdown, locations,
            and data sources.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a LinkedIn data specialist with access to comprehensive team data. Generate a detailed team overview for:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - company_description: Brief description of what the company does, their mission, and their industry focus
        - total_employees: The total number of employees at the company
        - roles_breakdown: A list of roles with counts, percentage of total workforce, sources (as indices into the main sources list), and confidence levels (Engineering, Product, Sales, etc.)
        - locations: List of primary office locations
        - key_hiring_areas: Top areas where the company is currently hiring (e.g., "Data Science", "Frontend Engineering")
        - growth_rate: Overall team expansion rate (e.g., 0.15 for 15% growth)
        - sources: List of source URLs where this data was found
        - last_updated: The datetime of the latest data (ISO format)

        For the roles_breakdown, make sure to include a percentage field that shows what portion of the company each role represents.
        
        Be as realistic, accurate, and detailed as possible. Use plausible numbers and sources. Ensure that percentages add up to 100%.
        Reference sources by their index in the main sources list when used inside nested fields.
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=TeamOverviewResponse,
            agent_name="LinkedInTeamOverviewAgent",
        )

    @cacheable()
    async def get_individual_performance(
        self,
        company_name: str,
        domain: Optional[str] = None,
        individual_name: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve performance data for an individual based on LinkedIn.
        Args:
            company_name (str): Name of the company
            domain (str, optional): Domain of the company
            individual_name (str, optional): Name of the individual
        Returns:
            Dict: Contains individual name, title, tenure, performance metrics,
            and data sources.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a LinkedIn data specialist with access to executive profiles and performance data. Generate a comprehensive profile for:
        - Individual Name: {individual_name or "N/A"}
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - individual_name: The name of the individual
        - title: Current job title
        - image_url: URL to the individual's profile image (if available)
        - tenure_years: Number of years at the company
        - performance_metrics: A list of metrics with values, sources (as indices into the main sources list), and confidence levels (endorsements, connections, articles published, etc.)
        - previous_companies: List of previous employment with name, title, duration, and dates
        - key_strengths: List of core capabilities and professional strengths
        - development_areas: List of growth opportunities or areas for professional development
        - education: List of educational background with institution, degree, field of study, and dates
        - sources: List of source URLs where this data was found
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic, accurate, and detailed as possible. Create a coherent professional profile that includes accomplishments and career trajectory.
        Reference sources by their index in the main sources list when used inside nested fields.
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=IndividualPerformanceResponse,
            agent_name="LinkedInIndividualPerformanceAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_org_structure(
        self,
        company_name: str,
        domain: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve organizational structure data for a company from LinkedIn.
        Args:
            company_name (str): Name of the company
            domain (str, optional): Domain of the company
        Returns:
            Dict: Contains company name, org chart nodes, and data sources.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a LinkedIn data specialist with access to organizational hierarchies and leadership data. Generate a detailed organizational structure for:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - org_chart: A list of organization nodes, each with:
          * name: Individual's full name
          * title: Job title
          * department: Organizational department or function
          * linkedin_url: Direct link to LinkedIn profile
          * reports_to: Name of manager/supervisor
          * direct_reports: List of names of subordinates
          * sources: List of indices referring to the main sources list
        - ceo: Name of the Chief Executive Officer
        - departments: List of departments with name, head, employee count, and any sub-departments
        - leadership_team: List of executive team members with name, title, linkedin_url, and department
        - sources: List of source URLs where this data was found
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic, accurate, and detailed as possible. Create a coherent organizational structure that makes sense for this company size and industry.
        Reference sources by their index in the main sources list when used inside nested fields.
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=OrgStructureResponse,
            agent_name="LinkedInOrgStructureAgent",
            use_knowledge_base=use_knowledge_base,
        )

    @cacheable()
    async def get_team_growth(
        self,
        company_name: str,
        domain: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        use_knowledge_base: bool = False,
    ):
        """
        Retrieve team growth data for a company from LinkedIn.
        Args:
            company_name (str): Name of the company
            domain (str, optional): Domain of the company
            start_date (str, optional): Start date for analysis
            end_date (str, optional): End date for analysis
        Returns:
            Dict: Contains company name, team growth timeseries, and summary metrics.
        """
        prompt = f"""
        The current date is {datetime.now().isoformat()}.
        You are a LinkedIn data specialist with access to hiring trends and workforce analytics. Generate a detailed team growth analysis for:
        - Company Name: {company_name}
        - Domain: {domain or "N/A"}
        - Start Date: {start_date or "N/A"}
        - End Date: {end_date or "N/A"}

        Please provide the following fields in your response:
        - company_name: The name of the company
        - team_growth_timeseries: A list of time periods with:
          * period_start: Start date of period (ISO format)
          * period_end: End date of period (ISO format)
          * hires: Number of new hires in period
          * attrition: Number of departures in period
          * net_growth: Net change in headcount for period
          * growth_rate: Growth rate as a decimal for this period (e.g., 0.05 for 5% growth)
          * sources: List of indices referring to the main sources list
          * confidence: Confidence level in this data point
        - total_hires: The total number of new hires over the entire period
        - total_attrition: The total number of departures over the entire period
        - net_growth: The net change in team size over the entire period
        - growth_rate_annualized: Year-over-year comparison as a decimal (e.g., 0.12 for 12% annual growth)
        - key_hiring_areas: Top areas where the company focused recent hiring efforts
        - attrition_by_department: List of departments with corresponding attrition count and rate
        - hiring_trends: List of identified hiring patterns with trend name, description, and supporting data
        - sources: List of source URLs where this data was found
        - last_updated: The datetime of the latest data (ISO format)

        Be as realistic, accurate, and detailed as possible. Use plausible numbers and ensure mathematical consistency across statistics.
        Reference sources by their index in the main sources list when used inside nested fields.
        Output should be a detailed textual description of all these fields and their values.
        """

        return await self._execute_llm_analysis(
            company_name=company_name,
            prompt=prompt,
            response_model=TeamGrowthResponse,
            agent_name="LinkedInTeamGrowthAgent",
            use_knowledge_base=use_knowledge_base,
        )
