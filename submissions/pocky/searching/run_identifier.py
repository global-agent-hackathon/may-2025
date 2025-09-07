import sys
import os
import json
from dotenv import load_dotenv
from agents.identifier_agent import IdentifierAgent
from models.openai_agent import OpenAIAgent

def save_result(cve_path: str, llm_response: str):
	"""
	Save LLM response to a standardized result file alongside the original CVE JSON.

	Args:
		cve_path (str): Path to original CVE JSON file.
		llm_response (str): Raw output from the model.
	"""
	output_path = cve_path.replace(".json", "_result.json")
	
	try:
		parsed = json.loads(llm_response)
		result = {
			"success": parsed.get("success", False),
			"PoC": parsed.get("PoC", "")
		}
	except Exception:
		result = {
			"success": False,
			"PoC": "",
			"raw_output": llm_response.strip()
		}

	with open(output_path, "w", encoding="utf-8") as f:
		json.dump(result, f, indent=2, ensure_ascii=False)

	print(f"[✓] Result saved to: {output_path}")

def main():
	load_dotenv()
	
	if len(sys.argv) != 2:
		print("Usage: python run_identifier.py <path_to_CVE_json>")
		return

	cve_path = sys.argv[1]
	if not os.path.exists(cve_path):
		print(f"[✗] File not found: {cve_path}")
		return
	
	openai_api_key = os.getenv("OPENAI_API_KEY")
	
	# Init GPT-4o agent
	model = OpenAIAgent(
		api_key=openai_api_key, 
		model_name="gpt-4o"
	)

	# Run identifier agent
	agent = IdentifierAgent(model)
	llm_response = agent.run(cve_path)

	print("\n[LLM Response]:\n", llm_response)
	save_result(cve_path, llm_response)

if __name__ == "__main__":
	main()
