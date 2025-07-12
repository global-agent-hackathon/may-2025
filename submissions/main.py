import json
from typing import Union
from news_agent import AgnoAgent, translate_text
from fastapi import FastAPI
import uvicorn, os
from puzzle_agent import agent

app = FastAPI()

@app.get("")
def read_root():
    return {"Hello": "World"}

@app.get("/news")
def get_news():
    agno_agent = AgnoAgent()
    original_news = agno_agent.get_news()
    print(json.dumps(original_news, indent=4))

    translated_text = translate_text(original_news, ["hi-IN"])

    news_with_translations = {
        "title": original_news["title"],
        "description": original_news["description"],
        "source_links": original_news["source_links"],
        "translations": translated_text
    }
    print("news: ", news_with_translations)
    
    return news_with_translations

@app.get("/puzzle")
def get_puzzle():
    response = agent.run("""Generate a new chess puzzle using the tool and provide a complete analysis.
                        Finally, strictly output your analysis as a single JSON object with the structure {
                            title,
                            theme,
                            difficulty,
                            hint,
                            solution,
                            mate_in_n,
                            fen,
                        } 
                        Do not include any other text or markdown—just valid JSON.""")
    
    # Check if the response is a RunResponse object and extract content
    if hasattr(response, 'content'):
        puzzle_analysis = response.content
    else:
        puzzle_analysis = str(response)

    print("\n=== CHESS PUZZLE ANALYSIS ===\n")
    print(puzzle_analysis)
    return json.loads(puzzle_analysis[7:-3])

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  
    uvicorn.run(app, host="0.0.0.0", port=port, reload=False)