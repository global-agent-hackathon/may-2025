import json
import re
from agno.tools.base import Tool


class IdentifierTool(Tool):
	def __init__(self):
		super().__init__(
			name="identifier",
			description="Extracts description from simplified CVE JSON format"
		)

	def call(self, cve_file_path: str) -> str:
		"""
		Load and extract description field from simplified CVE JSON.

		Args:
			cve_file_path (str): Path to simplified CVE JSON file.

		Returns:
			str: JSON-formatted string containing the CVE description.
		"""
		try:
			with open(cve_file_path, "r", encoding="utf-8") as f:
				data = json.load(f)

			description = data.get("description", "")

			result = {
				"Description": description
			}

			formatted = json.dumps(result, indent=2)

#			print("\n================= IdentifierTool Input Preview =================")
#			print(formatted)
#			print("===============================================================\n")

			return self._clean_json_block(formatted)

		except Exception as e:
			return f"[ERROR] Failed to parse CVE file: {e}"

	def _clean_json_block(self, text: str) -> str:
		match = re.search(r"```json\s*(\{.*?\})\s*```", text, re.DOTALL)
		return match.group(1).strip() if match else text.strip()
