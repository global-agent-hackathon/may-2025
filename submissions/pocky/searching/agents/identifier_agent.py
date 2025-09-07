from agno.core.base import Agent
from tools.identifier_tool import IdentifierTool
from agno.utils.prompt import load_prompt
from models.openai_agent import OpenAIAgent  

class IdentifierAgent(Agent):
	def __init__(self, model: OpenAIAgent, prompt_path="prompts/identifier_prompt.txt"):
		super().__init__(name="identifier-agent")
		self.tool = IdentifierTool()
		self.model = model
		self.system_prompt = load_prompt(prompt_path)

	def run(self, cve_json_path: str) -> str:
		context = self.tool.call(cve_json_path)
		messages = [
			{"role": "system", "content": self.system_prompt},
			{"role": "user", "content": context}
		]
		response = self.model.chat(messages)
		return response
