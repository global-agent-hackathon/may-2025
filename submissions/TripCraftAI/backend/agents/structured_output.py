from typing import TypeVar, Type, Any
from pydantic import BaseModel
from agno.agent import Agent
from loguru import logger
from config.llm import model
import json
import re

T = TypeVar("T", bound=BaseModel)


def clean_json_string(json_str: str) -> str:
    """
    Clean a JSON string by removing markdown code blocks and any extra whitespace.

    Args:
        json_str (str): The JSON string to clean

    Returns:
        str: The cleaned JSON string
    """
    # Remove markdown code blocks
    json_str = re.sub(r"```(?:json)?\n?(.*?)```", r"\1", json_str, flags=re.DOTALL)

    # If no code blocks found, use the original string
    if not json_str.strip():
        json_str = json_str

    # Remove any leading/trailing whitespace
    json_str = json_str.strip()

    return json_str


async def convert_to_model(input_text: str, target_model: Type[T]) -> T:
    """
    Convert input text into a specified Pydantic model using an Agno agent.

    Args:
        input_text (str): The input text to convert
        target_model (Type[T]): The target Pydantic model class

    Returns:
        T: An instance of the target model
    """

    structured_output_agent = Agent(
        model=model,
        description="Convert natural language input into structured data models",
        instructions=[
            "Convert the following text into a valid JSON that matches this Pydantic model schema:",
            "Return ONLY the JSON object that matches the schema exactly.",
        ],
        markdown=True,
        expected_output="\n".join(
            [
                "A valid JSON object that matches the provided schema.",
                "Do not include any explanations or additional text - return only the JSON object.",
                "Without ````json` or ````",
            ]
        ),
    )

    schema = target_model.model_json_schema()
    schema_str = json.dumps(schema, indent=2)

    # Create the prompt with model schema and clear instructions
    prompt = f"""
    Your task is to convert the input text into a valid JSON object that exactly matches the provided schema.
    Do not include any explanations or additional text - return only the JSON object.

    Model schema:
    {schema_str}

    Rules:
    - Output must be valid JSON
    - All required fields must be included
    - Field types must match schema exactly
    - No extra fields allowed
    - Validate all constraints (min/max values, regex patterns, etc)

    Input text to convert:
    {input_text}
    """

    # Get structured response from the agent
    try:
        response = await structured_output_agent.arun(prompt)
        content = clean_json_string(response.content)
        logger.info(f"Structured output agent response: {content}")
        return target_model.model_validate_json(content)
    except Exception as e:
        logger.error(f"Failed to parse response into {target_model.__name__}: {str(e)}")
        raise ValueError(
            f"Failed to parse response into {target_model.__name__}: {str(e)}"
        )
