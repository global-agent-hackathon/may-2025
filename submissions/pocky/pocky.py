# pocky.py

import os
import json
import subprocess
from openai import OpenAI
from exa_py import Exa
from dotenv import load_dotenv
from validation.validation_agent import ValidationAgent
from validation.attack_intent_agent import AttackIntentAgent

# === CONFIGURATION ===
load_dotenv()
EXA_API_KEY = os.getenv("EXA_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

openai = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
exa = Exa(EXA_API_KEY)

RESULTS_DIR = "results"
LOGS_DIR = "logs"
PROMPTS_DIR = "prompts"

os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(LOGS_DIR, exist_ok=True)

# === LOGGING ===
def log(cve_id, stage, content):
	with open(os.path.join(LOGS_DIR, f"{cve_id}.log"), "a") as f:
		f.write(f"\n[Stage: {stage}]\n{content}\n")
		print(f"\n[Stage: {stage}]\n{content}\n")

def save_result(cve_id, text):
	with open(os.path.join(RESULTS_DIR, f"{cve_id}_PoC.txt"), "w") as f:
		f.write(text)

def get_cve_description(cve_id):
	with open(f"./search_output/{cve_id}.json", "r") as f:
		return json.load(f)["description"]

# === POC PROCESSING ===
def process_poc_results(cve_id):
	init_result_path = "./search_output/init_result.txt"
	with open(init_result_path, "r") as f:
		init_result = f.read().strip()
	
	pocgithub_path = f"./search_output/{cve_id}_pocgithub.json"
	google_result_path = f"./search_output/{cve_id}_google_result.json"
	
	# Check for GitHub PoC repository
	if os.path.exists(pocgithub_path) and os.path.exists(init_result_path) and not os.path.exists(google_result_path):
		with open(pocgithub_path, "r") as f:
			github_data = json.load(f)
		if github_data.get("success") is True:
			log(cve_id, "special_case", "Detected GitHub PoC repository")
			poc = f"A readily usable exploit tool repository: {github_data.get('PoC')}"
			save_result(cve_id, poc)
			return poc
	
	return init_result

# === MAIN WORKFLOW ===
def run_agent_for_cve(cve_id):

	# Stage 1: PoC Retrieval
	subprocess.run(f"python searching/run_all_sources.py {cve_id}", shell=True)
	poc = process_poc_results(cve_id)
	if poc and poc.startswith("A readily usable exploit tool repository:"):
		return

	# Stage 2: Attack Intent
	description = get_cve_description(cve_id)
	intent = AttackIntentAgent(description).run()
	log(cve_id, "attack_intent", f"Attack intent: {intent}")
	
	# Stage 3: Validation
	validation_input = json.dumps({"attack_intent": intent, "poc_sample": poc}, indent=2)
	valid = ValidationAgent(validation_input).run()
	log(cve_id, "validation", f"Validation: {valid}")

	if valid is True:
		save_result(cve_id, poc)
		log(cve_id, "success", f"PoC for {cve_id} is written to {RESULTS_DIR}/{cve_id}_PoC.txt")
		return

	save_result(cve_id, f"[!] The PoC for {cve_id} failed validation.\nHowever, you can also refer to the PoC:\n {poc}")
	log(cve_id, "failed", f"PoC for {cve_id} failed validation.")

# === ENTRY POINT ===
if __name__ == "__main__":
	import sys
	if len(sys.argv) < 2:
		print("Usage: python pocky.py CVE-XXXX-XXXX")
		exit(1)                                    
	run_agent_for_cve(sys.argv[1].strip())