from agno.agent import Agent
from agno.storage.mongodb import MongoDbStorage
from dotenv import load_dotenv

from backend.settings import get_app_settings
from backend.utils.llm import get_model

if __name__ == "__main__":
    load_dotenv()
    app_settings = get_app_settings()
    model = get_model(app_settings.llm_config)
    db_config = app_settings.db_config

    # Create a storage backend using the Mongo database
    storage = MongoDbStorage(
        # store sessions in the agent_sessions collection
        collection_name="agent_sessions",
        db_url=db_config.get_connection_string(),
    )

    # Add storage to the Agent
    agent = Agent(
        session_id="fixed_id_for_demo",
        storage=storage,
        model=model,
        add_history_to_messages=True,
        num_history_runs=3,
    )

    response = agent.run("What's my name")
    print(response)
