from typing import Optional
from pydantic import BaseModel, model_validator
import uuid
from agno.models.message import UrlCitation


class NewsItem(BaseModel):
    id: Optional[str] = None
    title: str
    content: str
    source: list[str]
    published_at: str
    category: str
    image_url: str
    citations: list[UrlCitation]


class NewsItemList(BaseModel):
    news_items: list[NewsItem]

    @model_validator(mode="after")
    def set_id(self):
        for news_item in self.news_items:
            news_item.id = str(uuid.uuid4())
        return self
