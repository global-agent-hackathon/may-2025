import json
from tools.ident_expdb_tool import IdentExpDBTool

class IdentExpDBAgent:
	"""
	Agent to load and analyze Exploit-DB search results for PoC identification.
	"""

	def __init__(self, model, prompt_path: str = "prompts/ident_expdb_prompt.txt"):
		self.tool = IdentExpDBTool(model=model, prompt_path=prompt_path)

	def run(self, txt_path: str) -> dict:
		"""
		Args:
			txt_path (str): Path to the Exploit-DB result text file (e.g., CVE-XXXX-YYYY_exploitdb.txt)

		Returns:
			dict: {"success": ..., "PoC": ...}
		"""
		with open(txt_path, "r", encoding="utf-8") as f:
			content = f.read()

		return self.tool.run(content)
