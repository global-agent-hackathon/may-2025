class Tool:
	def __init__(self, name: str, description: str = ""):
		self.name = name
		self.description = description

	def call(self, *args, **kwargs):
		raise NotImplementedError("Tool must implement a call() method.")
