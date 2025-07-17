from pydantic import BaseModel
from typing import Literal

class TestResult(BaseModel):
    test_status: Literal["Pass", "Fail", "Flaky"]
    message: str 