from pydantic import BaseModel
from typing import List, Optional, Literal
from datetime import datetime


class FileUploadInitiateResponse(BaseModel):
    file_id: str
    upload_url: str
    expires: datetime


class ProcessingDetails(BaseModel):
    progress: float
    estimated_time_remaining: int


class ExtractedEntity(BaseModel):
    type: str
    value: str
    confidence: float
    relevance: float
    context: str


class DocumentSection(BaseModel):
    title: str
    content: str
    page_numbers: List[int]


class DocumentTable(BaseModel):
    title: str
    data: List[List[str]]
    page_number: int


class DocumentFigure(BaseModel):
    title: str
    description: str
    page_number: int


class DocumentStructure(BaseModel):
    sections: List[DocumentSection]
    tables: List[DocumentTable]
    figures: List[DocumentFigure]


class FileAnalysis(BaseModel):
    summary: str
    key_points: List[str]
    sentiment: str
    extracted_entities: List[ExtractedEntity]
    document_structure: DocumentStructure


class FileResponse(BaseModel):
    id: str
    name: str
    type: str
    size: int
    status: Literal["uploading", "processing", "ready", "error"]
    url: str
    created_at: datetime
    thread_id: Optional[str] = None
    processing_progress: Optional[float] = None
    processing_details: Optional[ProcessingDetails] = None
    analysis: Optional[FileAnalysis] = None
    thumbnail: Optional[str] = None


class FileListResponse(BaseModel):
    files: List[FileResponse]
    total: int


class CompanyDocumentsResponse(BaseModel):
    company_name: str
    document_urls: List[str]


class DoucmentParseResponse(BaseModel):
    heading: str
    content: str
