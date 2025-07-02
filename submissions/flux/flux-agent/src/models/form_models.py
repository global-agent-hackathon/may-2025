from typing import List, Optional, Any, Dict
from pydantic import BaseModel, Field, model_validator
from constants.enums import FieldType


class FormField(BaseModel):
    id: str = Field(..., description="Unique identifier for the field")
    type: FieldType = Field(..., description="Type of the form field")
    label: str = Field(..., description="Display label for the field")
    placeholder: Optional[str] = Field(None, description="Placeholder text")
    required: bool = Field(False, description="Whether the field is required")
    options: Optional[List[str]] = Field(None, description="Options for choice fields")
    fileSize: Optional[int] = Field(None, description="Max file size in MB")
    fileTypes: Optional[List[str]] = Field(None, description="Allowed file types")
    is_ai_field: bool = Field(False, description="Whether this is an AI-computed field")
    ai_metadata_prompt: Optional[str] = Field(None, description="AI computation prompt")
    ai_computed_value: Optional[str] = Field(None, description="Computed AI value")

    @model_validator(mode='before')
    @classmethod
    def clean_null_values(cls, values):
        if isinstance(values, dict):
            return {k: v for k, v in values.items() if v is not None}
        return values

    class Config:
        use_enum_values = True


class FormSchema(BaseModel):
    title: str = Field(..., description="Form title")
    description: str = Field(..., description="Form description")
    fields: List[Dict[str, Any]] = Field(..., description="Form fields")

    @model_validator(mode='before')
    @classmethod
    def clean_fields(cls, values):
        if isinstance(values, dict) and 'fields' in values:
            cleaned_fields = []
            for field in values['fields']:
                if isinstance(field, dict):
                    cleaned_field = {k: v for k, v in field.items() if v is not None}
                    cleaned_fields.append(cleaned_field)
                else:
                    cleaned_fields.append(field)
            values['fields'] = cleaned_fields
        return values


class FormRequest(BaseModel):
    prompt: str = Field(..., description="Natural language prompt for form generation")
    context: Optional[str] = Field(None, description="Additional context")
    existingFormSchema: Optional[Dict[str, Any]] = Field(None, description="Existing form schema for editing")
    user_id: Optional[str] = Field(None, description="User ID for the request")


class PromptEnhancementRequest(BaseModel):
    prompt: str = Field(..., description="Original prompt to enhance")
    context: Optional[str] = Field(None, description="Memory context from similar forms")
    examples: Optional[str] = Field(None, description="Examples of successful prompts")
    enhancement_type: str = Field(default="form_generation", description="Type of enhancement needed")


class PromptEnhancementResponse(BaseModel):
    enhanced_prompt: str = Field(..., description="Enhanced version of the prompt")
    improvements: List[str] = Field(default_factory=list, description="List of improvements made")
    confidence: float = Field(default=0.8, description="Confidence score for the enhancement")
    reasoning: Optional[str] = Field(None, description="Explanation of the enhancements made")


class MemoryEnhancementRequest(BaseModel):
    prompt: str = Field(..., description="Original prompt to enhance with memory insights")
    user_id: str = Field(..., description="User ID to search memories for")
    memory_context: Optional[str] = Field(None, description="Pre-gathered memory context")
    successful_examples: Optional[str] = Field(None, description="Examples of successful forms")


class MemoryEnhancementResponse(BaseModel):
    enhanced_prompt: str = Field(..., description="Memory-enhanced version of the prompt")
    improvements: List[str] = Field(default_factory=list, description="List of memory-based improvements made")
    confidence: float = Field(default=0.8, description="Confidence score for the enhancement")
    memory_insights: Optional[str] = Field(None, description="Summary of memory insights used")
    successful_patterns: List[str] = Field(default_factory=list, description="Successful patterns found in memory")


class FormResponse(BaseModel):
    title: str
    description: str
    fields: List[Dict[str, Any]] 