import os
import sys
import json
import subprocess

def run_and_check_output(command, output_file, success_key="success", value=True, poc_key="PoC"):
	subprocess.run(command, shell=True)
	if not os.path.exists(output_file):
		return False, None
	with open(output_file, "r") as f:
		try:
			result = json.load(f)
		except json.JSONDecodeError:
			return False, None
	if result.get(success_key) == value:
		return True, result.get(poc_key, "")
	return False, None

def main():
	if len(sys.argv) != 2:
		print("Usage: python run_all_sources.py <CVE-ID>")
		return

	cve_id = sys.argv[1]
	cve_json_path = f"./search_output/{cve_id}.json"
	result_path = "./search_output/init_result.txt"

	# Step 1: Get CVE JSON
	subprocess.run(f"python ./searching/cveinfo.py {cve_id}", shell=True)

	# Step 2: Run Identifier
	id_json_path = f"./search_output/{cve_id}_result.json"
	success, poc = run_and_check_output(f"python ./searching/run_identifier.py {cve_json_path}", id_json_path)
	if success:
		with open(result_path, "w") as f:
			f.write(poc)
		return

	# Step 3: Exploit-DB retrieval
	exploit_txt_path = f"./search_output/{cve_id}_exploitdb.txt"
	subprocess.run(f"python ./searching/run_exploit_db.py {cve_json_path}", shell=True)

	# Step 4: Analyze Exploit-DB
	exploit_json_path = f"./search_output/{cve_id}_exploitdb_poc.json"
	success, poc = run_and_check_output(f"python ./searching/run_ident_expdb.py {exploit_txt_path}", exploit_json_path)
	if success:
		with open(result_path, "w") as f:
			f.write(poc)
		return

	# Step 5: PoC-in-GitHub
	github_json_path = f"./search_output/{cve_id}_pocgithub.json"
	success, poc = run_and_check_output(f"python ./searching/run_poc_in_github.py {cve_json_path}", github_json_path)
	if success:
		with open(result_path, "w") as f:
			f.write(poc)
		return

	# Step 6: Google Search
	google_json_path = f"./search_output/{cve_id}_google_result.json"
	success, poc = run_and_check_output(f"python ./searching/run_google_search.py {cve_json_path}", google_json_path)
	with open(result_path, "w") as f:
		f.write(poc if success else "Failed to gather a PoC.")

if __name__ == "__main__":
	main()
