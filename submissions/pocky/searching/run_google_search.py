import os
import sys
import json
from dotenv import load_dotenv
from agents.google_search_agent import GoogleSearchAgent
from models.openai_agent import OpenAIAgent

def main():
	
	load_dotenv()
	
	if len(sys.argv) != 2:
		print(f"Usage: python {sys.argv[0]} <CVE_JSON_FILE>")
		sys.exit(1)

	cve_path = sys.argv[1]
	if not os.path.exists(cve_path):
		print(f"[!] File not found: {cve_path}")
		sys.exit(1)

	openai_api_key = os.getenv("OPENAI_API_KEY")
	exa_api_key = os.getenv("EXA_API_KEY")
			
	# Load OpenAI model
	model = OpenAIAgent(
		api_key=openai_api_key,
		model_name="gpt-4o"
	)

	# Run the agent
	agent = GoogleSearchAgent(model=model, exa_api_key=exa_api_key)
	result = agent.run(cve_path)

	# Save result
	cve_id = os.path.splitext(os.path.basename(cve_path))[0]
	output_file = f"./search_output/{cve_id}_google_result.json"
	with open(output_file, "w", encoding="utf-8") as f:
		json.dump(result, f, indent=2, ensure_ascii=False)
	print(f"[✓] Result saved to: {output_file}")

if __name__ == "__main__":
	main()
