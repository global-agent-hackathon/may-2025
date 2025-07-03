import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
import os
from agno.embedder.together import TogetherEmbedder
from sklearn.metrics.pairwise import cosine_similarity
import ast
from agno.tools import tool
from agno.agent import Agent
from agno.models.groq import Groq
load_dotenv()

@tool
def get_code_example(query: str) -> list[dict]:
    """
    Retrieve the most relevant Manim code examples based on semantic similarity to the query.
    
    This function:
    1. Loads a dataset of Manim code examples with pre-computed embeddings
    2. Generates an embedding for the input query
    3. Calculates cosine similarity between the query and all examples
    4. Returns the top 3 most relevant code examples
    
    Args:
        query (str): A natural language description of the desired animation or effect
        
    Returns:
        list: A list of dictionaries, each containing:
            - code (str): The Manim code example
            - prompt (str): The original prompt/description of the code
            - similarity (float): The cosine similarity score (0-1) to the query
            
    """
    manim_csv = Path("/home/deb/usr/manimator/backend/data/manim_dataset_with_embeddings.csv")
    df = pd.read_csv(manim_csv)

    df['embeddings'] = df['embeddings'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) else x)
    
    embedder = TogetherEmbedder(api_key=os.getenv("TOGETHER_API_KEY"))
    query_embd = np.array(embedder.get_embedding(query)).reshape(1, -1)
    
    df['similarity'] = df['embeddings'].apply(
        lambda x: cosine_similarity([x], query_embd)[0][0] if x is not None else -1
    )

    top_results = df.sort_values('similarity', ascending=False).head(3)
    
    results = []
    for _, row in top_results.iterrows():
        results.append({
            'code': row['Code'],
            'prompt': row['prompt'],
            'similarity': row['similarity']
        })
    
    return results

def main():

    agent = Agent(
    model=Groq(id="llama-3.3-70b-versatile"),
    description="You are an animator using manin to write code for animation",
    tools=[get_code_example],      
    show_tool_calls=True,           
    markdown=True                   
    )


    agent.print_response("create an animation of rotaing cube", stream=True)

if __name__ == "__main__":
    main()