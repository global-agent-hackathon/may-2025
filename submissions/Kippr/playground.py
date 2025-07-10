from agno.playground import Playground, serve_playground_app
from agent import kippr

app = Playground(
    agents=[
        kippr
    ]
).get_app()

if __name__ == "__main__":
    serve_playground_app("playground:app", reload=True)