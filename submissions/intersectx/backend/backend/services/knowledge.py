from backend.settings import VectorStoreConfig, MongoConnectionDetails
from agno.vectordb.mongodb import MongoDb
from agno.knowledge import AgentKnowledge
from backend.utils.llm import get_embedding_model


class KnowledgeBaseService:
    def __init__(
        self,
        db_config: MongoConnectionDetails,
        vector_store_config: VectorStoreConfig,
    ):
        self.db_config = db_config
        self.vector_store_config = vector_store_config
        self.embedder = get_embedding_model(vector_store_config)
        self.vector_db = MongoDb(
            collection_name=vector_store_config.mongo_collection,
            embedder=self.embedder,
            database=self.db_config.dbname,
            db_url=self.db_config.get_connection_string(),
            wait_until_index_ready=60,
            wait_after_insert=300,
        )

    def get_knowledge_base(self):
        return AgentKnowledge(vector_db=self.vector_db)
