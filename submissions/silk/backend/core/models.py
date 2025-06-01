from typing import List
from pydantic import BaseModel, Field


class SectionOutline(BaseModel):
    section_title: str = Field(..., description="Concise, descriptive title for the course section.")
    section_description: str = Field(
        ...,
        description="Comprehensive description acting as a detailed prompt for content generation. Must include learning objectives, key topics/concepts, examples needed, and its connection to the overall course flow."
    )

class CourseOutline(BaseModel):
    course_title: str = Field(..., description="Engaging and accurate title for the entire course.")
    course_description: str = Field(..., description="A brief overview of the course, its target audience, and what learners will achieve.")
    sections: List[SectionOutline] = Field(..., min_length=1, description="A list of sequential sections that make up the course.")

class CourseAuthenticator(BaseModel):
    is_valid_course_request: bool = Field(..., description="Indicates if the given course request is valid or a random chat message")