import json
import os
import re
from typing import List, Dict, Any, Optional
import asyncio

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from firecrawl import FirecrawlApp
from pydantic import BaseModel, Field

from constants.enums import FieldType, ModelConfig, ErrorMessages
from models.form_models import FormSchema, FormField
from utils.logger import get_logger

logger = get_logger()


class AgnoFormField(BaseModel):
    id: str = Field(..., description="Unique string identifier for the field")
    type: str = Field(..., description="Field type")
    label: str = Field(..., description="Descriptive label for the field")
    placeholder: Optional[str] = Field(None, description="Optional placeholder text")
    required: bool = Field(..., description="Whether the field is required")
    options: Optional[List[str]] = Field(None, description="Array of options for choice fields")
    fileSize: Optional[int] = Field(None, description="Max file size in MB for file fields")
    fileTypes: Optional[List[str]] = Field(None, description="Array of allowed file types")
    is_ai_field: bool = Field(False, description="Whether this is an AI-computed field")
    ai_metadata_prompt: Optional[str] = Field(None, description="AI computation prompt")
    ai_computed_value: Optional[str] = Field(None, description="Computed value from AI processing")


class AgnoFormModel(BaseModel):
    title: str = Field(..., description="The title of the form")
    description: str = Field(..., description="The description of the form")
    fields: List[AgnoFormField] = Field(..., description="Array of form fields")


class FormService:
    def __init__(self):
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_api_key:
            raise ValueError(ErrorMessages.MISSING_API_KEY)
        
        # Initialize Firecrawl
        self.firecrawl_api_key = os.getenv("FIRECRAWL_API_KEY")
        if self.firecrawl_api_key:
            self.firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
            logger.info("Firecrawl initialized successfully")
        else:
            logger.warning("Firecrawl API key missing")
            self.firecrawl = None
        
        logger.info("Setting up form agent with OpenAI")
        self.form_agent = Agent(
            model=OpenAIChat(id=ModelConfig.GPT_4_NANO, api_key=self.openai_api_key),
            description="Expert form schema generator",
            instructions=self._get_form_instructions(),
            response_model=AgnoFormModel,
            use_json_mode=True,
            markdown=True,
            debug_mode=True,
        )
        
        # Initialize AI computation agent
        self.ai_agent = Agent(
            model=OpenAIChat(id=ModelConfig.GPT_4_NANO, api_key=self.openai_api_key),
            description="AI that computes field values based on other form fields and web content.",
            instructions=[
                "Process the given prompt and return a comprehensive, well-structured response.",
                "When web content is provided, analyze it thoroughly and incorporate relevant insights.",
                "Provide detailed analysis with specific examples and actionable recommendations.",
                "Structure your response clearly with headings, bullet points, and logical flow.",
            ],
            markdown=False,
        )
    
    def _get_form_instructions(self) -> List[str]:
        return [
            "Create practical forms that collect necessary information efficiently.",
            "Return only valid JSON that matches the expected format.",
            "When editing forms, preserve existing field IDs and structure when appropriate.",
            "Support AI fields with type 'ai' that have comprehensive metadata prompts.",
            "AI fields should not be visible to users for input - they are computed automatically.",
            "Create detailed, context-aware AI prompts that provide clear analysis instructions.",
            "AI prompts should include specific criteria, evaluation frameworks, and expected output format.",
            "CRITICAL: Every field MUST have these required properties: id, type, label, required",
            "AI fields (type='ai') should ALWAYS have required=false since they are computed",
            "Regular input fields can have required=true or required=false based on necessity",
            "Ensure all field objects are complete and valid before returning",
        ]
    
    async def scrape_url_content(self, url: str) -> str:
        if not self.firecrawl:
            return ""
        
        try:
            logger.info(f"Scraping URL: {url}")
            result = self.firecrawl.scrape_url(url, formats=['markdown'])
            
            if result and result.get('data', {}).get('markdown'):
                content = result['data']['markdown']
                logger.info(f"Successfully scraped {len(content)} characters from {url}")
                return content
            
            logger.warning(f"No markdown content found for URL: {url}")
            return ""
                
        except Exception as e:
            logger.error(f"Error scraping URL {url}: {str(e)}")
            return ""
    
    def normalize_field(self, field: Dict[str, Any]) -> Dict[str, Any]:
        if 'id' not in field:
            field['id'] = f"field_{id(field)}"
        
        if 'type' not in field:
            field['type'] = FieldType.TEXT
            
        if 'label' not in field:
            field['label'] = "Untitled Field"
            
        if 'is_ai_field' not in field:
            field['is_ai_field'] = False
            
        if isinstance(field.get('is_ai_field'), str):
            field['is_ai_field'] = field['is_ai_field'].lower() == 'true'
            
        if field.get('is_ai_field'):
            field['type'] = FieldType.AI
            field['required'] = False
        else:
            if 'required' not in field:
                field['required'] = False
                
        if isinstance(field.get('required'), str):
            field['required'] = field['required'].lower() == 'true'
            
        if 'options' in field and field['options'] is not None:
            if not isinstance(field['options'], list):
                if isinstance(field['options'], str):
                    try:
                        field['options'] = json.loads(field['options'])
                    except:
                        field['options'] = [opt.strip() for opt in field['options'].split(',')]
                else:
                    field['options'] = []
        
        allowed_types = [t.value for t in FieldType]
        if field.get('type') not in allowed_types:
            field['type'] = FieldType.TEXT
            
        return field
    
    async def compute_ai_field(self, ai_metadata_prompt: str, form_data: Dict[str, Any], 
                              field_mapping: Dict[str, str]) -> str:
        try:
            scraped_content = {}
            url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+')
            
            for field_id, field_value in form_data.items():
                if isinstance(field_value, str):
                    urls = url_pattern.findall(field_value)
                    for url in urls:
                        if url not in scraped_content:
                            content = await self.scrape_url_content(url)
                            if content:
                                scraped_content[url] = content
                                logger.info(f"Scraped content from {url}: {len(content)} characters")
            
            processed_prompt = ai_metadata_prompt
            field_references = re.findall(r'\{([^}]+)\}', ai_metadata_prompt)
            
            for field_ref in field_references:
                field_value = None
                
                for field_id, field_label in field_mapping.items():
                    if field_label.lower() == field_ref.lower():
                        field_value = form_data.get(field_id, '')
                        break
                
                if field_value is None:
                    field_value = form_data.get(field_ref, '')
                
                enhanced_value = str(field_value or '')
                if isinstance(field_value, str):
                    urls_in_field = url_pattern.findall(field_value)
                    for url in urls_in_field:
                        if url in scraped_content:
                            enhanced_value += f"\n\n--- Content from {url} ---\n{scraped_content[url]}"
                
                processed_prompt = processed_prompt.replace(f'{{{field_ref}}}', enhanced_value)

            logger.info(f"Processed AI prompt with scraped content: {processed_prompt[:200]}...")
            
            response = self.ai_agent.run(processed_prompt)
            computed_value = response.content.strip()
            
            logger.info(f"AI field computed successfully: {len(computed_value)} characters")
            return computed_value
            
        except Exception as e:
            logger.error(f"Error computing AI field: {str(e)}")
            return f"Error computing value: {str(e)}"
    
    def generate_form(self, prompt: str, context: Optional[str] = None, 
                     existing_form: Optional[Dict[str, Any]] = None) -> FormSchema:
        
        user_message = self._build_generation_prompt(prompt, context, existing_form)
        
        try:
            logger.info("Calling form generation agent")
            response = self.form_agent.run(user_message)
            logger.info("Successfully received response from form agent")
            
            form_data = response.content
            
            # Handle case where response.content is a string instead of AgnoFormModel
            if isinstance(form_data, str):
                logger.warning("Received string response instead of structured model, attempting to parse")
                try:
                    form_dict = json.loads(form_data)
                    form_data = AgnoFormModel(**form_dict)
                except Exception as parse_error:
                    logger.error(f"Failed to parse string response: {parse_error}")
                    raise ValueError(f"Invalid response format: {parse_error}")
            
            # Convert fields to dictionaries
            field_dicts = []
            for field_data in form_data.fields:
                if hasattr(field_data, 'model_dump'):
                    field_dict = field_data.model_dump()
                else:
                    field_dict = field_data if isinstance(field_data, dict) else {}
                
                cleaned_dict = {k: v for k, v in field_dict.items() if v is not None}
                normalized_dict = self.normalize_field(cleaned_dict)
                
                # Validate required fields
                required_fields = ['id', 'type', 'label', 'required']
                for req_field in required_fields:
                    if req_field not in normalized_dict:
                        logger.warning(f"Missing required field '{req_field}' in field {normalized_dict.get('id', 'unknown')}")
                        if req_field == 'id':
                            normalized_dict['id'] = f"field_{len(field_dicts)}"
                        elif req_field == 'type':
                            normalized_dict['type'] = FieldType.TEXT
                        elif req_field == 'label':
                            normalized_dict['label'] = 'Untitled Field'
                        elif req_field == 'required':
                            normalized_dict['required'] = False
                
                field_dicts.append(normalized_dict)
            
            logger.info(f"Generated form with {len(field_dicts)} fields")
            
            form_schema = FormSchema(
                title=form_data.title,
                description=form_data.description,
                fields=field_dicts
            )
            
            return form_schema
            
        except Exception as e:
            logger.error(f"Error calling form generation API: {str(e)}")
            raise
    
    def _build_generation_prompt(self, prompt: str, context: Optional[str], 
                                existing_form: Optional[Dict[str, Any]]) -> str:
        # Get available field types
        available_types = [t.value for t in FieldType]
        field_types_str = ", ".join(available_types)
        
        if existing_form:
            field_descriptions = []
            for field in existing_form.get('fields', []):
                field_descriptions.append(self._format_field_for_prompt(field))
            
            fields_str = "\n".join(field_descriptions)
            context_str = (context or "")[:300] + "..." if context and len(context) > 300 else context or ""
            
            return f"""Modify this form based on the request: "{prompt}"

CURRENT FORM STRUCTURE:
Title: {existing_form.get('title', 'Untitled')}
Description: {existing_form.get('description', 'No description')}

CURRENT FIELDS:
{fields_str}

Additional context: {context_str}

AVAILABLE FIELD TYPES: {field_types_str}

Guidelines for modifications:
1. IMPORTANT: Preserve existing field IDs when keeping or modifying fields
2. You can add, modify, or remove fields as needed to fulfill the request
3. If adding new fields, assign them unique IDs that don't conflict with existing ones
4. Use only the available field types listed above
5. Support AI fields with type 'ai' for computed values based on other fields
6. AI fields should have is_ai_field=true and comprehensive ai_metadata_prompt with field references like {{fieldName}}
7. Return the complete modified form with all fields (not just changes)"""
        else:
            context_str = (context or "")[:500] + "..." if context and len(context) > 500 else context or ""
            
            return f"""Create a new form based on this request: "{prompt}"
Context: {context_str}

AVAILABLE FIELD TYPES: {field_types_str}

Please return a complete form with:
- A descriptive title
- A detailed description
- Appropriate fields with unique IDs, clear labels, and proper settings
- Use only the available field types listed above (choose the most appropriate type for each field)
- Support for AI fields (type='ai') that compute values based on other fields using comprehensive metadata prompts
- AI fields should reference other fields using {{fieldName}} syntax in the ai_metadata_prompt

Field type guidelines:
- text: Basic single-line text input
- long_answer: Multi-line text areas
- email: Email validation
- phone: Phone number input
- date/time: Date and time selection
- number: Numeric input with validation
- checkbox: List of options
- multiple_choice: Radio buttons (single selection)
- dropdown: Select dropdown (single selection)
- multi_select: Multiple selection from options
- file: File upload with optional size/type restrictions
- link: URL input
- h1/h2/h3: Section headers (not input fields)
- ai: Computed fields based on other form data

Make AI prompts detailed, professional, and value-adding rather than simple one-liners."""
    
    def _format_field_for_prompt(self, field: Dict[str, Any]) -> str:
        field_str = f"- id: {field.get('id')}, type: {field.get('type')}, label: {field.get('label')}, required: {field.get('required')}"
        
        if field.get('placeholder'):
            field_str += f", placeholder: {field.get('placeholder')}"
        if field.get('options'):
            field_str += f", options: {field.get('options')}"
        if field.get('is_ai_field'):
            field_str += f", is_ai_field: {field.get('is_ai_field')}"
        if field.get('ai_metadata_prompt'):
            field_str += f", ai_metadata_prompt: {field.get('ai_metadata_prompt')}"
            
        return field_str 

    def enhance_prompt(self, prompt: str, context: Optional[str] = None, 
                      examples: Optional[str] = None) -> Dict[str, Any]:
        """Enhance a form generation prompt using AI and memory insights"""
        
        enhancement_prompt = self._build_enhancement_prompt(prompt, context, examples)
        improvements = []
        reasoning = ""
        
        try:
            response = self.ai_agent.run(enhancement_prompt)
            enhanced = response.content.strip()
            
            # Ensure the enhanced prompt is significantly better
            if len(enhanced) <= len(prompt) + 10:
                # If enhancement is minimal, add some structured improvements
                enhanced = self._apply_structured_enhancements(prompt, context)
                improvements = ["Applied structured enhancements due to minimal AI improvement"]
                reasoning = "AI enhancement was minimal, applied rule-based improvements"
            else:
                # Analyze what was improved
                improvements = self._analyze_improvements(prompt, enhanced)
                reasoning = "Enhanced using AI with memory insights and successful patterns"
            
            logger.info(f"Enhanced prompt from {len(prompt)} to {len(enhanced)} characters")
            
            return {
                "enhanced_prompt": enhanced,
                "improvements": improvements,
                "confidence": 0.9 if len(enhanced) > len(prompt) + 50 else 0.7,
                "reasoning": reasoning
            }
            
        except Exception as e:
            logger.error(f"Error enhancing prompt: {str(e)}")
            # Fallback to structured enhancement
            enhanced = self._apply_structured_enhancements(prompt, context)
            return {
                "enhanced_prompt": enhanced,
                "improvements": ["Applied fallback structured enhancements"],
                "confidence": 0.6,
                "reasoning": f"AI enhancement failed ({str(e)}), used rule-based fallback"
            }

    def _analyze_improvements(self, original: str, enhanced: str) -> List[str]:
        """Analyze what improvements were made to the prompt"""
        improvements = []
        
        # Simple heuristic analysis
        if len(enhanced) > len(original) * 1.5:
            improvements.append("Significantly expanded prompt detail")
        
        if "field" in enhanced.lower() and "field" not in original.lower():
            improvements.append("Added specific field type requirements")
            
        if any(word in enhanced.lower() for word in ["validation", "required", "optional"]):
            improvements.append("Included validation and requirement specifications")
            
        if any(word in enhanced.lower() for word in ["user", "experience", "ux", "accessibility"]):
            improvements.append("Added user experience considerations")
            
        if not improvements:
            improvements.append("Enhanced prompt clarity and specificity")
            
        return improvements

    def _build_enhancement_prompt(self, prompt: str, context: Optional[str], 
                                 examples: Optional[str]) -> str:
        """Build a prompt for enhancing the user's form generation request"""
        
        base_prompt = f"""You are an expert form designer helping to enhance a user's form creation prompt. 
Your goal is to make their prompt more specific, detailed, and likely to generate a high-quality form.

ORIGINAL PROMPT: "{prompt}"

ENHANCEMENT GUIDELINES:
1. Add specific field types and validation requirements
2. Include user experience considerations (field order, grouping, etc.)
3. Specify data collection goals and use cases
4. Add accessibility and usability requirements
5. Include any missing essential fields for the form type
6. Make the prompt more actionable and specific

"""

        if context:
            base_prompt += f"\nMEMORY INSIGHTS: {context}\n"
        
        if examples:
            base_prompt += f"\nSUCCESSFUL EXAMPLES: {examples}\n"

        base_prompt += """
REQUIREMENTS:
- Keep the core intent of the original prompt
- Add 2-4 specific improvements that will lead to a better form
- Make it 2-3x more detailed while staying focused
- Include specific field types, validation rules, or UX considerations
- Don't change the fundamental purpose or tone

Return ONLY the enhanced prompt, nothing else."""

        return base_prompt

    def _apply_structured_enhancements(self, prompt: str, context: Optional[str]) -> str:
        """Apply rule-based enhancements when AI enhancement fails"""
        
        enhanced = prompt.strip()
        improvements = []
        
        # Detect form type and add relevant enhancements
        prompt_lower = enhanced.lower()
        
        if 'feedback' in prompt_lower or 'survey' in prompt_lower:
            improvements.extend([
                "Include rating scales (1-5 stars or 1-10 numeric)",
                "Add multiple choice questions for categorization",
                "Include open-ended text areas for detailed feedback"
            ])
        
        elif 'application' in prompt_lower or 'job' in prompt_lower:
            improvements.extend([
                "Include personal information section (name, email, phone)",
                "Add experience and education fields with date ranges",
                "Include file upload for resume and cover letter",
                "Add skills assessment or portfolio links"
            ])
        
        elif 'registration' in prompt_lower or 'event' in prompt_lower:
            improvements.extend([
                "Include date/time selection with timezone support",
                "Add contact information and emergency contacts",
                "Include dietary restrictions and accessibility needs",
                "Add payment information if applicable"
            ])
        
        elif 'contact' in prompt_lower or 'inquiry' in prompt_lower:
            improvements.extend([
                "Include subject/category dropdown for routing",
                "Add priority level selection",
                "Include preferred contact method selection"
            ])
        
        # Add general improvements if prompt is short
        if len(enhanced) < 100:
            improvements.extend([
                "Specify required vs optional fields clearly",
                "Include appropriate field validation rules",
                "Consider user experience and logical field ordering"
            ])
        
        # Apply improvements
        if improvements:
            enhanced += ". " + " ".join(improvements[:3])  # Limit to top 3 improvements
        
        # Add context insights
        if context and len(context) > 10:
            enhanced += f" {context}"
        
        return enhanced 

    def enhance_prompt_with_memory(self, prompt: str, user_id: str, 
                                  memory_context: Optional[str] = None,
                                  successful_examples: Optional[str] = None) -> Dict[str, Any]:
        """Enhance a form generation prompt specifically using memory insights and patterns"""
        
        try:
            from .memory_service import MemoryService
            memory_service = MemoryService()
            
            if not memory_service.is_enabled():
                # Fallback to regular enhancement if memory service is not available
                return self.enhance_prompt(prompt, memory_context, successful_examples)
            
            # Search for relevant memories
            form_memories = memory_service.search_memories(
                user_id=user_id,
                query=prompt,
                limit=5,
                memory_type="form_interaction"
            )
            
            # Extract successful patterns from memory
            successful_patterns = []
            memory_insights = []
            
            if form_memories:
                for memory in form_memories:
                    metadata = memory.get('metadata', {})
                    ai_analytics = metadata.get('ai_form_analytics', {})
                    
                    # Focus on successful AI-generated forms
                    if (ai_analytics.get('creation_method') == 'ai' and 
                        ai_analytics.get('success_score', 0) >= 7):
                        
                        field_count = ai_analytics.get('generated_field_count', 0)
                        field_types = ai_analytics.get('generated_field_types', [])
                        original_prompt = metadata.get('original_prompt', '')
                        
                        if field_count >= 3 and original_prompt:
                            successful_patterns.append({
                                'prompt': original_prompt[:200],  # Truncate for prompt
                                'field_count': field_count,
                                'field_types': field_types[:5],  # Top 5 field types
                                'score': ai_analytics.get('success_score', 0)
                            })
                            
                            memory_insights.append(f"Previous successful form: {field_count} fields, types: {', '.join(field_types[:3])}")
            
            # Sort by success score
            successful_patterns.sort(key=lambda x: x['score'], reverse=True)
            successful_patterns = successful_patterns[:3]  # Top 3 patterns
            
            # Build memory-enhanced prompt
            enhancement_prompt = self._build_memory_enhancement_prompt(
                prompt, successful_patterns, memory_insights, memory_context
            )
            
            # Generate enhanced prompt using AI
            response = self.ai_agent.run(enhancement_prompt)
            enhanced = response.content.strip()
            
            # Analyze improvements
            improvements = self._analyze_memory_improvements(prompt, enhanced, successful_patterns)
            
            # Generate insights summary
            insights_summary = self._generate_memory_insights_summary(successful_patterns, memory_insights)
            
            logger.info(f"Memory-enhanced prompt from {len(prompt)} to {len(enhanced)} characters using {len(successful_patterns)} patterns")
            
            return {
                "enhanced_prompt": enhanced,
                "improvements": improvements,
                "confidence": 0.9 if len(successful_patterns) > 0 else 0.7,
                "memory_insights": insights_summary,
                "successful_patterns": [p['prompt'][:100] + "..." for p in successful_patterns]
            }
            
        except Exception as e:
            logger.error(f"Error in memory enhancement: {str(e)}")
            # Fallback to regular enhancement
            fallback_result = self.enhance_prompt(prompt, memory_context, successful_examples)
            fallback_result['memory_insights'] = "Memory enhancement failed, used standard enhancement"
            fallback_result['successful_patterns'] = []
            return fallback_result

    def _build_memory_enhancement_prompt(self, prompt: str, successful_patterns: List[Dict], 
                                       memory_insights: List[str], context: Optional[str]) -> str:
        """Build a prompt for memory-based enhancement"""
        
        base_prompt = f"""You are an expert form designer with access to memory of successful form patterns. 
Enhance the user's form creation prompt by applying insights from their previous successful forms.

ORIGINAL PROMPT: "{prompt}"

MEMORY INSIGHTS FROM SUCCESSFUL FORMS:
"""
        
        if successful_patterns:
            for i, pattern in enumerate(successful_patterns, 1):
                base_prompt += f"\n{i}. Successful Pattern (Score: {pattern['score']}/10):"
                base_prompt += f"\n   - Original: \"{pattern['prompt']}\""
                base_prompt += f"\n   - Generated: {pattern['field_count']} fields"
                base_prompt += f"\n   - Field Types: {', '.join(pattern['field_types'])}\n"
        
        if memory_insights:
            base_prompt += f"\nPATTERN INSIGHTS:\n" + "\n".join(f"- {insight}" for insight in memory_insights[:5])
        
        if context:
            base_prompt += f"\nADDITIONAL CONTEXT: {context}"
        
        base_prompt += """

MEMORY-BASED ENHANCEMENT GUIDELINES:
1. Apply successful field type patterns from the user's history
2. Use similar complexity levels that worked well before
3. Incorporate field structures that proved effective
4. Match the user's preferred form organization style
5. Add specific field types that were successful in similar contexts
6. Maintain the optimal field count range from successful patterns

REQUIREMENTS:
- Keep the core intent of the original prompt
- Apply 2-4 memory-based improvements from successful patterns
- Make it more specific using insights from previous successful forms
- Include field types and structures that worked well before
- Don't exceed the typical successful complexity level

Return ONLY the enhanced prompt, nothing else."""

        return base_prompt

    def _analyze_memory_improvements(self, original: str, enhanced: str, patterns: List[Dict]) -> List[str]:
        """Analyze what memory-based improvements were made"""
        improvements = []
        
        if len(patterns) > 0:
            avg_field_count = sum(p['field_count'] for p in patterns) / len(patterns)
            improvements.append(f"Applied patterns from {len(patterns)} successful forms (avg {avg_field_count:.1f} fields)")
        
        # Analyze field type mentions
        common_types = set()
        for pattern in patterns:
            common_types.update(pattern['field_types'][:3])
        
        if common_types:
            mentioned_types = [t for t in common_types if t.lower() in enhanced.lower()]
            if mentioned_types:
                improvements.append(f"Incorporated successful field types: {', '.join(mentioned_types[:3])}")
        
        # Check for complexity improvements
        if len(enhanced) > len(original) * 1.3:
            improvements.append("Enhanced with detailed specifications from memory patterns")
        
        if any(word in enhanced.lower() for word in ["required", "optional", "validation"]):
            improvements.append("Added validation patterns from successful forms")
        
        if not improvements:
            improvements.append("Applied memory-based enhancements to improve success likelihood")
        
        return improvements

    def _generate_memory_insights_summary(self, patterns: List[Dict], insights: List[str]) -> str:
        """Generate a summary of memory insights used"""
        if not patterns and not insights:
            return "No specific memory patterns available"
        
        summary_parts = []
        
        if patterns:
            total_forms = len(patterns)
            avg_fields = sum(p['field_count'] for p in patterns) / total_forms if patterns else 0
            avg_score = sum(p['score'] for p in patterns) / total_forms if patterns else 0
            
            summary_parts.append(f"Applied insights from {total_forms} successful forms")
            summary_parts.append(f"Average success: {avg_fields:.1f} fields, {avg_score:.1f}/10 score")
        
        if insights:
            summary_parts.append(f"Used {len(insights)} memory insights")
        
        return ". ".join(summary_parts) if summary_parts else "Basic memory analysis applied" 