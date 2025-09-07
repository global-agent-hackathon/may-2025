class Agent:
	def __init__(self, name: str = "default-agent"):
		self.name = name

	def run(self, *args, **kwargs):
		raise NotImplementedError("Agent must implement a run() method.")
