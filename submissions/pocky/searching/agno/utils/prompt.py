def load_prompt(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()
