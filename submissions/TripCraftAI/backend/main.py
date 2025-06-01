from agno.agent import Agent, RunResponse
from agno.models.groq import Groq
from dotenv import load_dotenv

load_dotenv()

def main():

    agent = Agent(
        model=Groq(
            id="llama-3.3-70b-versatile",
            temperature=0.1,
            ),
        markdown=True

    )

    # Print the response in the terminal
    agent.print_response("Share a 2 sentence horror story.")



if __name__ == "__main__":
    main()
