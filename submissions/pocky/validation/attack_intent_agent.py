import json
import os
from openai import OpenAI
from searching.agno.utils.prompt import load_prompt

class AttackIntentAgent:
    """
    Agent that analyzes a CVE description to determine the attack intent.
    """
    
    def __init__(self, description: str, model_name: str = "gpt-4o"):
        """
        Initialize the Attack Intent Agent.
        
        Args:
            description (str): The CVE description to analyze.
            model_name (str): Model name to use (default: gpt-4o).
        """
        self.description = description
        self.model_name = model_name
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = os.getenv("OPENAI_BASE_URL")
        self.client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        
        # Load the prompt
        self.system_prompt = load_prompt("prompts/intent_prompt.txt")
    
    def run(self) -> str:
        """
        Run the analysis to determine attack intent.
        
        Returns:
            str: The analyzed attack intent.
        """
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.description}
        ]
        
        try:
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            return f"[ERROR] Attack intent analysis failed: {e}" 