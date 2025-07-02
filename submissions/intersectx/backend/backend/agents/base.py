from backend.settings import LLMConfig


class BaseAgent:
    def __init__(self, llm_config: LLMConfig):
        self.llm_config = llm_config

    @staticmethod
    def get_agent_instructions():
        pass

    def run(self, user_input: str):
        pass
