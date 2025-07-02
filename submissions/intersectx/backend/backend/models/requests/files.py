from pydantic import BaseModel


class FileUploadRequest(BaseModel):
    company_name: str
