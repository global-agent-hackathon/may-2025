from pydantic import BaseModel, EmailStr
from typing import Optional

class SendMailRequest(BaseModel):
    to_address: EmailStr
    subject: str
    content_plain: str
    content_html: Optional[str] = None