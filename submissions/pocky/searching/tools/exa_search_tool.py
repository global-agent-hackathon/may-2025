import os
import time
import json
from exa_py import Exa

class ExaSearchTool:
	def __init__(self, api_key: str):
		self.client = Exa(api_key)

	def extract_json_block(self, text: str) -> dict:
		"""
		Extract the first valid JSON block from the response.
		"""
		import json
		import re

		# Try extracting from markdown-wrapped block
		match = re.search(r"```json\s*({.*?})\s*```", text, re.DOTALL)
		if match:
			try:
				return json.loads(match.group(1).strip())
			except json.JSONDecodeError:
				pass

		# Try raw JSON if no markdown block found or failed to decode
		try:
			return json.loads(text.strip())
		except json.JSONDecodeError:
			print("[WARN] Unable to parse response as JSON")
			return {}

	def search_and_analyze(self, query: str, model) -> dict:
		print(f"[INFO] Searching with query: {query}")
		try:
			results = self.client.search_and_contents(query, text=True)
		except Exception as e:
			print(f"[ERROR] Exa search failed: {e}")
			return {
				"status": "fail",
				"query": query,
				"reason": str(e),
				"search_results": []
			}

		# Construct input for analysis
		search_snippets = []
		for item in results.results:
			snippet = item.text.replace("\n", " ").strip()
			url = item.url.strip()
			search_snippets.append(f"[{url}]\n{snippet}")

		combined_snippets = "\n\n".join(search_snippets)

		# Load prompt template
		prompt_path = os.path.join("prompts", "google_analysis_prompt.txt")
		with open(prompt_path, "r", encoding="utf-8") as f:
			system_prompt = f.read().strip()

		messages = [
			{"role": "system", "content": system_prompt},
			{"role": "user", "content": combined_snippets}
		]

		try:
			response = model.chat(messages=messages)
			print("[DEBUG] Raw model response for snippet analysis:")
			print(response)
			result = self.extract_json_block(response)
			result["query"] = query
			return result
		except Exception as e:
			print(f"[ERROR] Failed to parse final analysis result: {e}")
			return {
				"status": "fail",
				"query": query,
				"reason": str(e),
				"search_results": search_snippets
			}
