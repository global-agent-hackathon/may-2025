from agno.agent import Agent
from agno.models.azure import AzureOpenAI

class EmissionsQnAAgent:
    def __init__(self, deployment_id, api_key, endpoint):
        self.agent = Agent(
            model=AzureOpenAI(
                id=deployment_id,
                api_key=api_key,
                azure_endpoint=endpoint
            ),
            memory=True  # Enables chat memory
        )

    def answer_question(self, context: str, question: str):
        prompt = f"""
You are an emissions data analyst assistant. Answer user questions based on the following context:

{context}

Q: {question}
A:
"""
        response = self.agent.run(prompt)
        return response.content
