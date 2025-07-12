from agno.agent import Agent
from agno.models.google import Gemini
from tool import generate_mate_in_n_puzzle
from dotenv import load_dotenv
import os

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
# Adjust path to your local stockfish
ENGINE_PATH = "stockfish/stockfish.exe"


agent = Agent(
    model=Gemini(id="gemini-2.0-flash",api_key=api_key),
    tools=[generate_mate_in_n_puzzle],
    show_tool_calls=True,
    markdown=True,
    instructions=[
        """You are a chess puzzle expert. When asked to generate a chess puzzle:
        1. Call the "generate_mate_in_n_puzzle" tool. MAKE SURE YOU CALL THE TOOL.
        2. Once you receive the puzzle data, create the following:
           - A descriptive title for the puzzle , dont reveal any hint here
           - Classification of the main tactical theme (fork, pin, discovered attack, mate pattern, etc.)
           - Difficulty rating (Easy, Medium, Hard, Expert)
           - A subtle hint that doesn't give away the solution
           - A detailed explanation of the solution. Example 1. Qh8+ Kxh8 2. Nf7+ Kg8 3. Nh6# + some text explaination that is optional. Validate the solution against the FEN.
           - The solution should solve the FEN, simulate the moves in the solution staring from the FEN and check if it is checkmate.
           - How many moves it is checkmate
        3. Format your response clearly with sections for each component
        4. Include the FEN from the tool's response
        
        Always verify the FEN is valid before proceeding. If the tool returns an error, explain the error to the user.
        If the tool return a ''NoneType' object is not subscriptable' that means it failed run it again"""
    ]
)