import os

base_files = {
	"agno/tools/base.py": '''\
class Tool:
	def __init__(self, name: str, description: str = ""):
		self.name = name
		self.description = description

	def call(self, *args, **kwargs):
		raise NotImplementedError("Tool must implement a call() method.")
''',

	"agno/core/base.py": '''\
class Agent:
	def __init__(self, name: str = "default-agent"):
		self.name = name

	def run(self, *args, **kwargs):
		raise NotImplementedError("Agent must implement a run() method.")
''',

	"agno/utils/prompt.py": '''\
def load_prompt(path: str) -> str:
	with open(path, "r", encoding="utf-8") as f:
		return f.read()
'''
}

def init_agno():
	for path, content in base_files.items():
		os.makedirs(os.path.dirname(path), exist_ok=True)
		with open(path, "w", encoding="utf-8") as f:
			f.write(content)
		print(f"[✓] Created {path}")

if __name__ == "__main__":
	init_agno()
