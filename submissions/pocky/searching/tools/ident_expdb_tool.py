import os
import json
import re


class IdentExpDBTool:
	def __init__(self, model, prompt_path: str):
		self.model = model
		self.prompt = self._load_prompt(prompt_path)

	def _load_prompt(self, prompt_path: str) -> str:
		if not os.path.exists(prompt_path):
			raise FileNotFoundError(f"Prompt file not found: {prompt_path}")
		with open(prompt_path, "r", encoding="utf-8") as f:
			return f.read().strip()

	def run(self, input_text: str) -> dict:
		messages = [
			{"role": "system", "content": self.prompt},
			{"role": "user", "content": input_text}
		]

		response = self.model.chat(messages)

#		print("\n===== Raw Model Response =====")
#		print(response)
#		print("================================")

		cleaned = self._clean_json_block(response)

		try:
			result = json.loads(cleaned)
			if "success" in result and "PoC" in result:
				return result
		except Exception as e:
			print("[ERROR] Failed to parse model output as JSON:")
			print(f"Exception: {e}")
			print("Raw output:", response)

		return {"success": "fail", "PoC": ""}

	def _clean_json_block(self, text: str) -> str:
		"""
		Remove ```json ... ``` block if present, else return original
		"""
		match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
		return match.group(1).strip() if match else text.strip()
