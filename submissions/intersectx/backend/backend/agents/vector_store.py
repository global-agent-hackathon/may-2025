from typing import List
from agno.document import Document
from agno.knowledge import AgentKnowledge
from agno.vectordb.mongodb import MongoDb
from backend.settings import VectorStoreConfig, MongoConnectionDetails
from backend.utils.llm import get_embedding_model


class VectorStore:
    def __init__(
        self,
        mongo_config: MongoConnectionDetails,
        vector_store_config: VectorStoreConfig,
    ):
        self.embedder = get_embedding_model(vector_store_config)
        self.vectorstore = MongoDb(
            embedder=self.embedder,
            collection_name=vector_store_config.mongo_collection,
            db_url=mongo_config.get_connection_string(),
            database=mongo_config.dbname,
            distance_metric="cosine",
        )
        self.vectorstore._get_client()
        self.agent_knowledge = AgentKnowledge(vector_db=self.vectorstore)

    async def add_documents(self, documents: List[Document], company: str):
        """
        For each Document, embed the content and set the embedding field, then load all documents to the DB.
        """
        filters = {"company": company}
        return await self.agent_knowledge.async_load_documents(
            documents, filters=filters
        )
