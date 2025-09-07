#!/usr/bin/env python3

import os
import sys
import json
import requests

API_KEY = os.getenv("NVD_API_KEY")  # NVD API Key
DOC_DIR = "./search_output/"
os.makedirs(DOC_DIR, exist_ok=True)

headers = {
	"apiKey": API_KEY
}

def fetch_cve_data(cve_id):
	url = f"https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={cve_id}"
	try:
		response = requests.get(url, headers=headers, timeout=10)
		if response.status_code == 200:
			return response.json()
		else:
			print(f"[!] Failed to fetch {cve_id} - Status code: {response.status_code}")
			return None
	except Exception as e:
		print(f"[!] Error fetching {cve_id}: {e}")
		return None

def extract_id_and_english_description(raw_json):
	try:
		cve_info = raw_json["vulnerabilities"][0]["cve"]
		en_desc = next((desc["value"] for desc in cve_info.get("descriptions", []) if desc.get("lang") == "en"), "")
		return {
			"id": cve_info["id"],
			"description": en_desc
		}
	except Exception as e:
		print(f"[!] Error extracting English description: {e}")
		return None

def save_to_file(cve_id, data):
	filepath = os.path.join(DOC_DIR, f"{cve_id}.json")
	with open(filepath, "w", encoding="utf-8") as f:
		json.dump(data, f, indent=4, ensure_ascii=False)
	print(f"[+] Saved to: {filepath}")

def main():
	if len(sys.argv) != 2:
		print("Usage: python script.py <CVE-ID>")
		sys.exit(1)

	cve_id = sys.argv[1].strip().upper()
	print(f"[*] Fetching CVE data for: {cve_id}")
	raw_data = fetch_cve_data(cve_id)

	if raw_data:
		extracted = extract_id_and_english_description(raw_data)
		if extracted:
			save_to_file(cve_id, extracted)

if __name__ == "__main__":
	main()
