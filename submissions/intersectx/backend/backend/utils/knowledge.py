from agno.agent import Agent
from agno.knowledge import AgentKnowledge
from agno.vectordb.mongodb import MongoDb
from dotenv import load_dotenv

from backend.settings import get_app_settings
from backend.utils.llm import get_model, get_embedding_model

if __name__ == "__main__":
    load_dotenv()
    app_settings = get_app_settings()
    model = get_model(app_settings.llm_config)
    db_config = app_settings.db_config
    embedder = get_embedding_model(app_settings.vector_store_config)
    print(db_config.get_connection_string())
    print(embedder)
    vector_db = MongoDb(
        collection_name="vector_store",
        database=db_config.dbname,
        db_url=db_config.get_connection_string(),
        embedder=embedder,
    )
    vector_db._get_client()

    knowledge_base = AgentKnowledge(vector_db=vector_db)
    # adjust wait_after_insert and wait_until_index_ready to your needs
    # document = Document(
    #     content="Mavi is a software engineer who specializes in developing web applications.",
    #     name="Mavi",
    #     meta_data={
    #         "company": "mavi"
    #     }
    # )
    # knowledge_base.load(recreate=True)

    # knowledge_base.load_documents([document])  # Comment out after first run

    agent = Agent(
        model=model,
        knowledge=knowledge_base,
        show_tool_calls=True,
        search_knowledge=True,
    )
    agent.print_response("Tell about the revenue over time of asapp", markdown=True)
