from typing import Optional

from agno.models.message import UrlCitation
from pydantic import BaseModel, Field, model_validator
from urllib.parse import urlparse


class CitationResponse(BaseModel):
    citations: list[UrlCitation] = Field(
        ..., description="List of citations for the response"
    )
    iframe_url: Optional[str] = Field(
        None, description="URL of the iframe for the response"
    )
    summary: str = Field(..., description="Summary of the response")

    @model_validator(mode="after")
    def validate_citations(self):
        processed_citations = []
        for citation in self.citations:
            url = citation.url
            title = citation.title

            if title is None:
                parsed_url = urlparse(url)
                domain = parsed_url.netloc

                if isinstance(domain, bytes):
                    domain = domain.decode("utf-8")

                # Remove 'www.' prefix if present
                if domain.startswith("www."):
                    domain = domain[4:]

                title = domain

            processed_citations.append(UrlCitation(url=url, title=title))

        self.citations = processed_citations
        return self
