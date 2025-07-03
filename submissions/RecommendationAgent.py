from agno.agent import Agent
from agno.models.azure.openai_chat import AzureOpenAI
from read_env import *

def recommendationTool(topic,proficiency_level):
    query = 'Give me the best study materials in terms of youtube tutorials and websites for the give topic to get profiency in the given proficiency level. Topic:' + topic +'Profiency Level:' + proficiency_level
    agent = Agent(model=AzureOpenAI(id="XXXXXXX",
                               api_key=AZURE_OPENAI_API_KEY), markdown=True)
    assistant_message = agent.run(query).messages[-1].content
    return(assistant_message)
