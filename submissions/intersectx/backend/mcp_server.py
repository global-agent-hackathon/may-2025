from fastmcp import FastMCP

from backend.dependencies import (
    get_finance_service,
    get_linkedin_team_service,
    get_market_analysis_service,
    get_risk_analysis_service,
    get_customer_sentiment_service,
    get_regulatory_compliance_service,
    get_partnership_network_service,
    get_search_service,
)
from backend.services.cache import CacheService
from backend.services.knowledge import KnowledgeBaseService
from backend.settings import get_app_settings
from dotenv import load_dotenv
from backend.agents.netlify import NetlifyAgent
from backend.utils.logger import get_logger

# Apply OpenAI client patch to fix AttributeError during garbage collection
from backend.utils.openai_patch import patch_openai_client

LOG = get_logger("MCP Server")
patch_openai_client()

load_dotenv()
mcp = FastMCP("Venture Insights MCP Server")

# Get app settings
app_settings = get_app_settings()
knowledge_base_service = KnowledgeBaseService(
    db_config=app_settings.db_config,
    vector_store_config=app_settings.vector_store_config,
)
netlify_agent = NetlifyAgent(app_settings.netlify_config)
# Instantiate services
finance_service = get_finance_service(
    app_settings=app_settings,
    knowledge_base_service=knowledge_base_service,
    netlify_agent=netlify_agent,
    cache_service=CacheService(app_settings.db_config),
)
linkedin_team_service = get_linkedin_team_service(
    app_settings=app_settings,
    netlify_agent=netlify_agent,
    cache_service=CacheService(app_settings.db_config),
)
market_analysis_service = get_market_analysis_service(
    app_settings=app_settings,
    netlify_agent=netlify_agent,
    cache_service=CacheService(app_settings.db_config),
)
risk_analysis_service = get_risk_analysis_service(
    netlify_agent=netlify_agent, cache_service=CacheService(app_settings.db_config)
)
customer_sentiment_service = get_customer_sentiment_service(
    app_settings=app_settings, cache_service=CacheService(app_settings.db_config)
)
regulatory_compliance_service = get_regulatory_compliance_service(
    netlify_agent=netlify_agent, cache_service=CacheService(app_settings.db_config)
)
partnership_network_service = get_partnership_network_service(
    netlify_agent=netlify_agent, cache_service=CacheService(app_settings.db_config)
)
search_service = get_search_service(
    app_settings=app_settings,
    netlify_agent=netlify_agent,
    knowledge_base_service=knowledge_base_service,
    cache_service=CacheService(app_settings.db_config),
)


# --- Finance ---
@mcp.tool()
async def revenue_analysis(
    company_name: str,
    domain: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
    granularity: str | None = "year",
):
    LOG.info("MCP tool call for revenue analysis")
    return await finance_service.get_revenue_analysis(
        company_name=company_name,
        domain=domain,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
    )


@mcp.tool()
async def expense_analysis(
    company_name: str,
    domain: str | None = None,
    year: int | None = None,
    category: str | None = None,
):
    return await finance_service.get_expense_analysis(
        company_name=company_name,
        domain=domain,
        year=year,
        category=category,
    )


@mcp.tool()
async def profit_margins(company_name: str, domain: str = None, year: int = None):
    return await finance_service.get_profit_margins(
        company_name=company_name,
        domain=domain,
        year=year,
    )


@mcp.tool()
async def valuation_estimation(
    company_name: str, domain: str | None = None, as_of_date: str | None = None
):
    return await finance_service.get_valuation_estimation(
        company_name=company_name,
        domain=domain,
        as_of_date=as_of_date,
    )


@mcp.tool()
async def funding_history(company_name: str, domain: str = None):
    return await finance_service.get_funding_history(
        company_name=company_name,
        domain=domain,
    )


# --- LinkedIn Team ---
@mcp.tool()
async def team_overview(company_name: str, domain: str = None):
    return await linkedin_team_service.get_team_overview(
        company_name=company_name,
        domain=domain,
    )


@mcp.tool()
async def individual_performance(
    company_name: str, domain: str | None = None, individual_name: str | None = None
):
    return await linkedin_team_service.get_individual_performance(
        company_name=company_name,
        domain=domain,
        individual_name=individual_name,
    )


@mcp.tool()
async def org_structure(company_name: str, domain: str = None):
    return await linkedin_team_service.get_org_structure(
        company_name=company_name,
        domain=domain,
    )


@mcp.tool()
async def team_growth(
    company_name: str,
    domain: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await linkedin_team_service.get_team_growth(
        company_name=company_name,
        domain=domain,
        start_date=start_date,
        end_date=end_date,
    )


# --- Market Analysis ---
@mcp.tool()
async def market_trends(
    industry: str,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await market_analysis_service.get_market_trends(
        industry=industry,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
async def competitive_analysis(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await market_analysis_service.get_competitive_analysis(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def growth_projections(
    industry: str,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await market_analysis_service.get_growth_projections(
        industry=industry,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
async def regional_trends(
    industry: str, regions: list = None, start_date: str = None, end_date: str = None
):
    return await market_analysis_service.get_regional_trends(
        industry=industry,
        regions=regions,
        start_date=start_date,
        end_date=end_date,
    )


# --- Risk Analysis ---
@mcp.tool()
async def regulatory_risks(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await risk_analysis_service.get_regulatory_risks(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def market_risks(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await risk_analysis_service.get_market_risks(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def operational_risks(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await risk_analysis_service.get_operational_risks(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def legal_risks(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await risk_analysis_service.get_legal_risks(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


# --- Customer Sentiment ---
@mcp.tool()
async def sentiment_summary(
    company_name: str,
    domain: str | None = None,
    product: str | None = None,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await customer_sentiment_service.get_sentiment_summary(
        company_name=company_name,
        domain=domain,
        product=product,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
async def customer_feedback(
    company_name: str,
    domain: str | None = None,
    product: str | None = None,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await customer_sentiment_service.get_customer_feedback(
        company_name=company_name,
        domain=domain,
        product=product,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
async def brand_reputation(
    company_name: str,
    domain: str | None = None,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await customer_sentiment_service.get_brand_reputation(
        company_name=company_name,
        domain=domain,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


# --- Regulatory Compliance ---
@mcp.tool()
async def compliance_overview(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await regulatory_compliance_service.get_compliance_overview(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def violation_history(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await regulatory_compliance_service.get_violation_history(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
async def compliance_risk(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await regulatory_compliance_service.get_compliance_risk(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def regional_compliance(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    regions: list | None = None,
):
    return await regulatory_compliance_service.get_regional_compliance(
        company_name=company_name,
        domain=domain,
        industry=industry,
        regions=regions,
    )


# --- Partnership Network ---
@mcp.tool()
async def partner_list(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await partnership_network_service.get_partner_list(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def strategic_alliances(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await partnership_network_service.get_strategic_alliances(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def network_strength(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
):
    return await partnership_network_service.get_network_strength(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
    )


@mcp.tool()
async def partnership_trends(
    company_name: str,
    domain: str | None = None,
    industry: str | None = None,
    region: str | None = None,
    start_date: str | None = None,
    end_date: str | None = None,
):
    return await partnership_network_service.get_partnership_trends(
        company_name=company_name,
        domain=domain,
        industry=industry,
        region=region,
        start_date=start_date,
        end_date=end_date,
    )


@mcp.tool()
async def general_search_knowledge(
    query: str,
):
    return await search_service.get_general_search_knowledge(
        query=query,
    )


# Add a resource for documentation overview
@mcp.resource("docs://overview")
async def get_overview() -> str:
    """
    Get an overview of the Venture Insights MCP Server.

    This resource provides a high-level description of the available
    tools and capabilities of this server.
    """
    return """
    # Venture Insights MCP Server
    
    This MCP server provides tools for analyzing companies, markets, and industries.
    
    ## Available Tool Categories:
    
    - **Finance**: Revenue analysis, expense analysis, profit margins, valuation estimation
    - **Team**: Team overview, individual performance, org structure, team growth
    - **Market**: Market trends, competitive analysis, growth projections, regional trends
    - **Risk**: Regulatory risks, market risks, operational risks, legal risks
    - **Customer**: Sentiment summary, customer feedback, brand reputation
    - **Compliance**: Compliance overview, violation history, compliance risk, regional compliance
    - **Partnerships**: Partner list, strategic alliances, network strength, partnership trends
    
    For detailed documentation on each tool, explore the available tools in the MCP Inspector.
    """


@mcp.resource("docs://mcp/full")
async def get_all_resources() -> str:
    """
    Get all the MCP API documentation. Returns the contents of the MCP_API.md file,
    which contains the complete API documentation for all MCP tools.

    Args: None

    Returns:
        str: The contents of the MCP API documentation
    """
    try:
        with open("MCP_API.md", "r") as file:
            return file.read()
    except Exception as e:
        return f"Error reading MCP API documentation: {str(e)}"


if __name__ == "__main__":
    mcp.run(transport="streamable-http", host="0.0.0.0", port=9000)
