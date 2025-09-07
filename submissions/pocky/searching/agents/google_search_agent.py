import json
import re
from typing import Optional
from agno.core.base import Agent
from agno.utils.prompt import load_prompt
from models.openai_agent import OpenAIAgent
from tools.exa_search_tool import ExaSearchTool

class GoogleSearchAgent(Agent):
	def __init__(self, model: OpenAIAgent, exa_api_key: str):
		super().__init__(name="google_search")
		self.model = model
		self.search_tool = ExaSearchTool(api_key=exa_api_key)

	def run(self, cve_path: str) -> dict:
		with open(cve_path, "r") as f:
			cve_data = json.load(f)

		# === Step 1: Generate Google Search Query ===
		query_prompt = load_prompt("prompts/google_query_prompt.txt")
		query_input = cve_data.get("description", "")

		messages = [
			{"role": "system", "content": query_prompt},
			{"role": "user", "content": query_input}
		]

		response = self.model.chat(messages=messages)
		print("[DEBUG] Raw model response for query:\n" + response)

		query = self._extract_query(response)
		if not query:
			print("[ERROR] Failed to parse query from model response")
			return {"success": False, "PoC": ""}

		print(f"[INFO] Generated search query: {query}")

		# === Step 2: Run Exa Search and Analyze ===
		final_result = self.search_tool.search_and_analyze(query, self.model)

		if not isinstance(final_result, dict):
			print("[ERROR] Final result is not a valid dict")
			return {"success": False, "PoC": ""}

		status = final_result.get("status", "")
		poc = final_result.get("candidate_poc", "")

		if status == "ready_to_decide" and poc.strip():
			return {"success": True, "PoC": poc.strip()}
		else:
			return {"success": False, "PoC": ""}

	def _extract_query(self, text: str) -> Optional[str]:
		"""
		Extracts the query_content field from the model's JSON-formatted response.
		"""
		match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
		raw_json = match.group(1).strip() if match else text.strip()

		try:
			data = json.loads(raw_json)
			return data.get("query_content")
		except json.JSONDecodeError:
			return None
