import json
import os
import re
from openai import OpenAI
from searching.agno.utils.prompt import load_prompt

class ValidationAgent:
    """
    Agent that validates whether a PoC sample correctly implements the intended attack behavior.
    """
    
    def __init__(self, validation_input: str, model_name: str = "gpt-4o"):
        """
        Initialize the Validation Agent.
        
        Args:
            validation_input (str): JSON string containing the attack intent and PoC sample.
            model_name (str): Model name to use (default: gpt-4o).
        """
        self.validation_input = validation_input
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # Load the prompt
        self.system_prompt = load_prompt("prompts/validation_prompt.txt")

    def run(self) -> bool:
        """
        Run the validation to determine if the PoC correctly implements the intended attack.
        
        Returns:
            bool: True if the PoC is valid, False otherwise.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.validation_input}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            result = response.choices[0].message.content.strip()
            
            # Extract the JSON result
            return self._extract_validation_result(result)
        except Exception as e:
            print(f"[ERROR] Validation failed: {e}")
            return False
    
    def _extract_validation_result(self, text: str) -> bool:
        """
        Extract the validation result from the model's response.
        
        Args:
            text (str): The model's response text.
            
        Returns:
            bool: True if the PoC is valid, False otherwise.
        """
        # Try to extract JSON from the response
        json_match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
        if json_match:
            json_str = json_match.group(1).strip()
        else:
            # If no code block, try to parse the entire text as JSON
            json_str = text.strip()
        
        try:
            data = json.loads(json_str)
            return data.get("valid", False)
        except json.JSONDecodeError:
            print(f"[ERROR] Failed to parse validation result: {text}")
            return False 