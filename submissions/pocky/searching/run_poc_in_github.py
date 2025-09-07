import sys
import os
import json
import requests


def extract_cve_id(cve_path):
	with open(cve_path, 'r', encoding='utf-8') as f:
		data = json.load(f)
	return data.get("id", "").strip()


def fetch_from_api(cve_id):
	url = f"https://poc-in-github.motikan2010.net/api/v1/?cve_id={cve_id}"
	try:
		resp = requests.get(url, timeout=10)
		if resp.status_code == 200:
			return resp.json()
		else:
			print(f"[WARN] API request failed with status code {resp.status_code}")
	except Exception as e:
		print(f"[ERROR] Exception during API request: {e}")
	return None


def fetch_from_github_fallback(cve_id):
	year = cve_id.split("-")[1]
	raw_url = f"https://raw.githubusercontent.com/nomi-sec/PoC-in-GitHub/master/{year}/{cve_id}.json"
	try:
		resp = requests.get(raw_url, timeout=10)
		if resp.status_code == 200:
			return resp.json()
		else:
			print(f"[WARN] Fallback GitHub request failed with status code {resp.status_code}")
	except Exception as e:
		print(f"[ERROR] Exception during fallback GitHub request: {e}")
	return None


def extract_html_urls(json_data):
	urls = []
	if isinstance(json_data, dict) and "data" in json_data:
		# Format from motikan API
		for item in json_data["data"]:
			if "html_url" in item:
				urls.append(item["html_url"])
	elif isinstance(json_data, list):
		# Fallback GitHub format
		for item in json_data:
			if "html_url" in item:
				urls.append(item["html_url"])
	return urls


def save_result(cve_id, urls):
	output = {
		"success": bool(urls),
		"PoC": "\n".join(urls) if urls else ""
	}
	out_path = f"./search_output/{cve_id}_pocgithub.json"
	with open(out_path, "w", encoding="utf-8") as f:
		json.dump(output, f, indent=2)
	print(f"[✓] Result saved to: {out_path}")


def main():
	if len(sys.argv) != 2:
		print("Usage: python run_poc_in_github.py <cve_json_file>")
		sys.exit(1)

	cve_path = sys.argv[1]
	if not os.path.isfile(cve_path):
		print(f"[ERROR] File not found: {cve_path}")
		sys.exit(1)

	cve_id = extract_cve_id(cve_path)
	print(f"[INFO] Processing CVE ID: {cve_id}")

	# Try primary API
	json_data = fetch_from_api(cve_id)
	urls = extract_html_urls(json_data) if json_data else []

	# Fallback to GitHub if needed
	if not urls:
		json_data = fetch_from_github_fallback(cve_id)
		urls = extract_html_urls(json_data) if json_data else []

	save_result(cve_id, urls)


if __name__ == "__main__":
	main()
