from backend.settings import MongoConnectionDetails
from backend.models.response.companies import (
    FeaturedCompany,
    CompanySearchResult,
    TopInvestorResponse,
    TopInvestorsListResponse,
)
from backend.utils.cache_decorator import cacheable
from backend.database.mongo import MongoDBConnector
from backend.models.response.research import (
    ResearchResponse,
)
from typing import Optional
import aiohttp
from urllib.parse import quote
import asyncio


class CompaniesService:
    def __init__(self, mongo_config: MongoConnectionDetails):
        self.mongo_config = mongo_config
        self.mongo_db = MongoDBConnector(mongo_config)
        # cache_service will be injected by the dependency injection system

    async def get_company_analysis(self, company_name: str) -> ResearchResponse:
        """
        Retrieve company analysis data from MongoDB.

        Args:
            company_name (str): Name of the company to retrieve research for

        Returns:
            ResearchResponse: The research data for the company
        """
        try:
            # Query MongoDB for the research data
            collection_name = "company_info"
            print(f">>> Querying collection: {collection_name}")

            # Get the document from MongoDB
            document = self.mongo_db.query(
                collection_name, {"company_name": company_name}
            )

            if not document:
                print(f">>> No research data found for {company_name}")
                return ResearchResponse(company_name=company_name)
            document = document[0]
            # Convert MongoDB document to ResearchResponse
            print(f">>> Found research data for {company_name}")
            print(document)

            # Create the research response from the document
            # discard the _id field
            document = {k: v for k, v in document.items() if k != "_id"}
            research_response = ResearchResponse(**document)

            return research_response

        except Exception as e:
            print(f">>> ERROR retrieving research data: {str(e)}")
            # Return empty ResearchResponse with just the company name
            return ResearchResponse(company_name=company_name)

    @staticmethod
    async def get_company_logo(company_name: str) -> str:
        fallback_logo = "https://pngimg.com/uploads/google/google_PNG19635.png"

        domain_base = (
            company_name.lower().replace(" ", "").replace(",", "").replace(".", "")
        )

        extensions = [".com", ".io", ".co", ".ai", ".org", ".net", ".app"]

        if len(domain_base) <= 3:
            return fallback_logo

        async with aiohttp.ClientSession() as session:
            for ext in extensions:
                try:
                    domain = f"{domain_base}{ext}"
                    logo_url = f"https://s2.googleusercontent.com/s2/favicons?domain={domain}&sz=128"

                    async with session.head(
                        f"https://{domain}", timeout=1.0
                    ) as response:
                        if response.status < 400:  # Any successful or redirect response
                            return logo_url
                except Exception:
                    continue

            return f"https://s2.googleusercontent.com/s2/favicons?domain={quote(company_name)}&sz=128"

    @cacheable()
    async def get_companies(self, limit: int = 100) -> list[CompanySearchResult]:
        """
        Get all companies from the database

        Args:
            limit: Maximum number of companies to return

        Returns:
            List of CompanySearchResult with company name and logo URL

        ! TODO Fix: the logo fetching is temporary and will be fixed in the future with a better solution
        """
        pipeline = [
            {
                "$project": {
                    "company_name": 1,
                }
            },
            {"$sort": {"company_name": 1}},
            {"$limit": limit},
        ]
        res = await self.mongo_db.aaggregate("company_info", pipeline)

        # Use asyncio.gather to fetch all logos concurrently
        company_names = [company["company_name"] for company in res]
        logo_urls = await asyncio.gather(
            *[self.get_company_logo(name) for name in company_names]
        )

        # Create company results with fetched logos
        companies = [
            CompanySearchResult(name=name, logoUrl=logo_url)
            for name, logo_url in zip(company_names, logo_urls)
        ]

        return companies

    @cacheable()
    async def get_featured_companies(
        self, limit: Optional[int] = 10, page: int = 1
    ) -> dict:
        """
        Get featured companies for display on the homepage or featured section

        Args:
            limit: Optional number of companies to return
            page: Page number for pagination

        Returns:
            Dictionary with companies, total count, page number and limit
        """

        pipeline = [
            {"$sort": {"company_name": 1}},
            {"$skip": ((page - 1) * limit)},
            {"$limit": limit},
            {
                "$project": {
                    "_id": 0,
                    "id": {"$ifNull": ["$card_info.id", {"$toString": "$_id"}]},
                    "name": {"$ifNull": ["$card_info.name", "$company_name"]},
                    "description": {
                        "$ifNull": [
                            "$card_info.description",
                            "AI-powered business solutions",
                        ]
                    },
                    "logoUrl": {
                        "$ifNull": [
                            "$card_info.logoUrl",
                            "https://pngimg.com/uploads/google/google_PNG19635.png",
                        ]
                    },
                    "logoText": {"$ifNull": ["$card_info.logoText", "COMPANY"]},
                    "logoSubText": {"$ifNull": ["$card_info.logoSubText", "SOLUTIONS"]},
                    "fundingStage": {
                        "$ifNull": ["$card_info.fundingStage", "Seed Stage"]
                    },
                    "tags": {"$ifNull": ["$card_info.tags", ["AI", "Tech", "SaaS"]]},
                    "fundingAsk": {"$ifNull": ["$card_info.fundingAsk", "500000"]},
                    "industry": {"$ifNull": ["$card_info.industry", "Tech"]},
                    "valuation": {"$ifNull": ["$card_info.valuation", "5000000"]},
                    "location": {"$ifNull": ["$card_info.location", "San Francisco"]},
                }
            },
        ]
        res = await self.mongo_db.aaggregate("company_info", pipeline)

        return {
            "companies": [FeaturedCompany.parse_obj(company) for company in res],
            "total": 10,
            "page": page,
            "limit": limit,
        }

    async def get_top_investors(self, limit: int = 10) -> TopInvestorsListResponse:
        users_collection = await self.mongo_db.aget_collection("users")
        cursor = (
            users_collection.find({"user_type": {"$in": ["vc", "investor"]}})
            .sort("portfolio", -1)
            .limit(limit)
        )
        investors = []
        async for user in cursor:
            investors.append(
                TopInvestorResponse(
                    first_name=user.get("first_name"),
                    last_name=user.get("last_name"),
                    linkedin_url=user.get("linkedin_url"),
                    portfolio=user.get("portfolio"),
                    companies_invested=user.get("companies_invested"),
                    email=user.get("email"),
                )
            )
        return TopInvestorsListResponse(investors=investors)
