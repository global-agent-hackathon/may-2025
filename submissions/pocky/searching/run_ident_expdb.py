import sys
import os
import json
from dotenv import load_dotenv
from agents.ident_expdb_agent import IdentExpDBAgent
from models.openai_agent import OpenAIAgent

def normalize_success_field(value) -> bool:
	"""
	Normalize different representations of success into a boolean.
	"""
	if isinstance(value, bool):
		return value
	if isinstance(value, str):
		return value.strip().lower() == "true"
	return False

def save_result(txt_path: str, llm_response):
	"""
	Standardize and save LLM response to JSON with only "success" and "PoC" fields.

	Args:
		txt_path (str): Path to input txt file (e.g., CVE-xxxx_exploitdb.txt)
		llm_response (str or dict): Raw output from the model, or parsed dict
	"""
	output_path = txt_path.replace(".txt", "_poc.json")

	try:
		# If response is a string, try to parse it
		if isinstance(llm_response, str):
			parsed = json.loads(llm_response)
		elif isinstance(llm_response, dict):
			parsed = llm_response
		else:
			raise ValueError("Unsupported llm_response type")

		poc = parsed.get("PoC", "")
		if isinstance(poc, list):
			poc = next((x for x in poc if isinstance(x, str) and x.strip()), "")

		success_raw = parsed.get("success", False)
		success = normalize_success_field(success_raw) and bool(poc.strip())

		result = {
			"success": success,
			"PoC": poc.strip() if success else ""
		}

	except Exception:
		result = {
			"success": False,
			"PoC": ""
		}

	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(result, f, indent=2)

	print(f"[✓] Result saved to: {output_path}")

def main():
	load_dotenv()

	if len(sys.argv) != 2:
		print("Usage: python run_ident_expdb.py <exploitdb_txt_file>")
		return

	txt_path = sys.argv[1]
	if not os.path.exists(txt_path):
		print(f"[✗] File not found: {txt_path}")
		return

	openai_api_key = os.getenv("OPENAI_API_KEY")
	model = OpenAIAgent(
		api_key=openai_api_key,
		model_name="gpt-4o"
	)

	agent = IdentExpDBAgent(model)
	llm_response = agent.run(txt_path)

	print("\n[LLM Response]:\n", llm_response)
	save_result(txt_path, llm_response)

if __name__ == "__main__":
	main()
