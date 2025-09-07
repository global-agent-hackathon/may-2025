import openai
import os

class OpenAIAgent:
	"""
	A simple wrapper around the OpenAI Chat Completion API for use in Agno-style agents.
	"""

	def __init__(self, api_key: str = os.getenv("OPENAI_API_KEY"), base_url: str = os.getenv("OPENAI_BASE_URL"), model_name: str = "gpt-4o"):
		"""
		Initialize the OpenAI agent.

		Args:
			api_key (str): Your OpenAI API key.
			base_url (str): The OpenAI API base URL.
			model_name (str): Model name to use (e.g., gpt-4, gpt-4o, gpt-3.5-turbo).
		"""
		self.client = openai.OpenAI(api_key=api_key, base_url=base_url)
		self.model = model_name

	def chat(self, messages: list[dict], temperature: float = 0.7) -> str:
		"""
		Perform a chat completion.

		Args:
			messages (list): List of message dicts, each with role/content.
			temperature (float): Sampling temperature.

		Returns:
			str: The model's response content.
		"""
		try:
			response = self.client.chat.completions.create(
				model=self.model,
				messages=messages,
				temperature=temperature
			)
			return response.choices[0].message.content.strip()
		except Exception as e:
			return f"[ERROR] OpenAI request failed: {e}"
