from pydantic import BaseModel, Field
from typing import Optional, List, Any, Dict


class ActionRequest(BaseModel):
    videoId: str
    categories: List[str]
    customPrompts: Any = {}


class StatusResponse(BaseModel):
    status: str
    detail: Optional[str] = None


class VideoScoreResult:
    def __init__(
        self,
        video_id: str,
        score: float,
        categories: Dict[str, float],
        evaluation_summary: str,
        content_summary: str,
    ):
        self.type = "videoScore"
        self.video_id = video_id
        self.score = score
        self.categories = categories
        self.evaluation_summary = evaluation_summary
        self.content_summary = content_summary

    def to_dict(self):
        return {
            "type": self.type,
            "videoId": self.video_id,
            "score": round(self.score, 2),
            "categories": {k: round(v, 2) for k, v in self.categories.items()},
            "evaluation_summary": self.evaluation_summary,
            "content_summary": self.content_summary,
        }


class CategoryResult(BaseModel):
    name: str = Field(
        ...,
        description="Name of the category.",
    )
    score: float = Field(
        ...,
        description=(
            "Score obtained after the evaluation. If category has positive connotation "
            "(e.g., intelligence or accuracy), number 10 will be the highest score you "
            "can assign to that category and 0 will be the lowest score. If feature "
            "has negative connotation (e.g., manipulation or bias), you will rank 0 "
            "as the highest score of that feature and 10 as the lowest score."
        ),
    )
    connotation: str = Field(
        ...,
        description="Connotation of the category (positive or negative).",
    )
    reason: str = Field(
        ...,
        description="Reasoning behind the score.",
    )


class OverallResult(BaseModel):
    score: Optional[float] = Field(
        ...,
        description="Average of all categories score.",
    )
    reason: Optional[str] = Field(
        ...,
        description="Summary of reasons of all categories.",
    )


class EvaluationResult(BaseModel):
    categories: List[Optional[CategoryResult]] = Field(
        ...,
        description="List of categories with the result of the evaluation.",
    )
    overall: OverallResult = Field(
        ...,
        description="Overall score and reasoning.",
    )
    error: str = Field(
        ...,
        description="Error message returned by the gathering process.",
    )
    content_summary: str = Field(
        ...,
        description="Summary of the video content.",
    )
