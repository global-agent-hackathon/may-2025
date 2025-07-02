from fastapi import APIRouter, Depends
from fastapi_utils.cbv import cbv
from backend.dependencies import get_finance_service
from backend.services.finance import FinanceService
from backend.models.requests.finance import (
    RevenueAnalysisRequest,
    ExpenseAnalysisRequest,
    ProfitMarginsRequest,
    ValuationEstimationRequest,
    FundingHistoryRequest,
)
from backend.models.response.finance import (
    RevenueAnalysisResponse,
    ExpenseAnalysisResponse,
    ProfitMarginsResponse,
    ValuationEstimationResponse,
    FundingHistoryResponse,
)
from backend.utils.logger import get_logger

finance_router = APIRouter(prefix="/finance", tags=["finance"])

LOG = get_logger("Finance API")


@cbv(finance_router)
class FinanceCBV:
    finance_service: FinanceService = Depends(get_finance_service)

    @finance_router.post("/revenue-analysis", response_model=RevenueAnalysisResponse)
    async def get_revenue_analysis(self, req: RevenueAnalysisRequest):
        LOG.debug(f"Received Request for Revenue Analysis: {req.model_dump_json()}")
        return await self.finance_service.get_revenue_analysis(
            company_name=req.company_name,
            domain=req.domain,
            start_date=req.start_date,
            end_date=req.end_date,
            granularity=req.granularity,
        )

    @finance_router.post("/expense-analysis", response_model=ExpenseAnalysisResponse)
    async def get_expense_analysis(self, req: ExpenseAnalysisRequest):
        LOG.debug(f"Received Request for Revenue Analysis: {req.model_dump_json()}")
        return await self.finance_service.get_expense_analysis(
            company_name=req.company_name,
            domain=req.domain,
            year=req.year,
            category=req.category,
        )

    @finance_router.post("/profit-margins", response_model=ProfitMarginsResponse)
    async def get_profit_margins(self, req: ProfitMarginsRequest):
        LOG.debug(f"Received Request for Revenue Analysis: {req.model_dump_json()}")
        return await self.finance_service.get_profit_margins(
            company_name=req.company_name, domain=req.domain, year=req.year
        )

    @finance_router.post(
        "/valuation-estimation", response_model=ValuationEstimationResponse
    )
    async def get_valuation_estimation(self, req: ValuationEstimationRequest):
        LOG.debug(f"Received Request for Revenue Analysis: {req.model_dump_json()}")
        return await self.finance_service.get_valuation_estimation(
            company_name=req.company_name, domain=req.domain, as_of_date=req.as_of_date
        )

    @finance_router.post("/funding-history", response_model=FundingHistoryResponse)
    async def get_funding_history(self, req: FundingHistoryRequest):
        LOG.debug(f"Received Request for Revenue Analysis: {req.model_dump_json()}")
        return await self.finance_service.get_funding_history(
            company_name=req.company_name, domain=req.domain
        )
