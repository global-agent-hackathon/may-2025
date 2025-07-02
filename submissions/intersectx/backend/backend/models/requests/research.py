from pydantic import BaseModel


class ResearchRequest(BaseModel):
    company_name: str
