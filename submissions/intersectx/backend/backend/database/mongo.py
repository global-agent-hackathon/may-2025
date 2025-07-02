from datetime import datetime
from typing import Optional, TYPE_CHECKING

from pydantic import BaseModel, Field

from backend.settings import MongoConnectionDetails
from backend.utils.logger import get_logger
from backend.utils.time_utils import show_time_taken

if TYPE_CHECKING:
    # Only imported for type checking
    from motor.motor_asyncio import AsyncIOMotorCollection, AsyncIOMotorDatabase
    from pymongo.collection import Collection
    from pymongo.synchronous.database import Database

LOG = get_logger()


class MongoIndexSpec(BaseModel):
    keys: list[tuple[str, int]] = Field(
        ..., description="List of (field, direction) tuples."
    )
    name: Optional[str] = Field(None, description="Name of the index.")
    unique: Optional[bool] = Field(
        False, description="Whether the index should enforce uniqueness."
    )
    background: Optional[bool] = Field(
        False, description="Whether to build the index in the background."
    )


class MongoDBConnector:
    def __init__(
        self,
        connection_details: MongoConnectionDetails,
        log_time_taken: bool = True,
        log_query: bool = False,
    ):
        self._connection_details = connection_details
        self._uri = str(self._connection_details)
        self._db_name = self._connection_details.dbname

        self.log_time_taken = log_time_taken
        self.log_query = log_query

    # sync implementations
    def get_collection(self, collection_name: str) -> "Collection":
        from pymongo import MongoClient

        client = MongoClient(self._uri)
        db = client[self._db_name]
        return db[collection_name]

    def get_database(self) -> "Database":
        from pymongo import MongoClient

        client = MongoClient(self._uri)
        return client[self._db_name]

    def query(self, collection_name: str, query: dict) -> list:
        s = datetime.now()
        collection_obj = self.get_collection(collection_name)

        result = list(collection_obj.find(query))

        if self.log_time_taken:
            show_time_taken(
                s,
                message=f"Executing {query if self.log_query else 'query'}",
                logger=LOG,
            )

        return result

    def aggregate(self, collection_name: str, pipeline: list) -> list:
        s = datetime.now()
        collection_obj = self.get_collection(collection_name)
        result = list(collection_obj.aggregate(pipeline))

        if self.log_time_taken:
            show_time_taken(
                s,
                message=f"Executing {pipeline if self.log_query else 'pipeline'}",
                logger=LOG,
            )

        return result

    def delete_collection(self, collection_name: str):
        db = self.get_database()
        try:
            db.drop_collection(collection_name)
        except Exception as e:
            LOG.info(f"Failed to delete collection due to {e}")

    def delete_records(self, collection_name: str, query: dict):
        collection_obj = self.get_collection(collection_name)
        try:
            collection_obj.delete_many(query)
        except Exception as e:
            LOG.info(f"Failed to delete collection due to {e}")

    def create_indexes(self, collection_name: str, indexes: list[MongoIndexSpec]):
        created_indices = []
        collection_obj = self.get_collection(collection_name)
        existing_indexes = collection_obj.index_information()
        LOG.info(f"Creating indexes for collection: {collection_name}")

        for index_spec in indexes:
            # Check if an index with the same key pattern and name already exists
            existing_index = next(
                (
                    idx_name
                    for idx_name, details in existing_indexes.items()
                    if details.get("key") == index_spec.keys
                    and details.get("name") == index_spec.name
                ),
                None,
            )

            if existing_index:
                LOG.info(
                    f"Index '{index_spec.name}' already exists. Skipping creation."
                )
            else:
                # Create the index if it doesn't exist
                index_name = collection_obj.create_index(
                    index_spec.keys,
                    name=index_spec.name,
                    unique=index_spec.unique,
                    background=index_spec.background,
                )
                created_indices.append(index_name)
                LOG.info(f"Created index: {index_name}")

        return created_indices

    # async implementations
    async def aget_collection(self, collection_name: str) -> "AsyncIOMotorCollection":
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(self._uri)
        db = client[self._db_name]
        return db[collection_name]

    async def aget_database(self) -> "AsyncIOMotorDatabase":
        from motor.motor_asyncio import AsyncIOMotorClient

        client = AsyncIOMotorClient(self._uri)
        return client[self._db_name]

    def insert_records(self, collection_name: str, records: list[dict]):
        collection_obj = self.get_collection(collection_name)
        try:
            collection_obj.insert_many(records)
        except Exception as e:
            LOG.info(f"Failed to insert records due to {e}")

    def update_records(
        self, collection_name: str, query_filter: dict, update_operation: dict
    ):
        collection_obj = self.get_collection(collection_name)
        try:
            collection_obj.update_many(query_filter, update_operation)
        except Exception as e:
            LOG.info(f"Failed to insert records due to {e}")

    async def aquery(self, collection_name: str, query: dict) -> list[dict]:
        s = datetime.now()
        collection_obj = await self.aget_collection(collection_name)
        result = await collection_obj.find(query).to_list(length=None)

        if self.log_time_taken:
            show_time_taken(
                s,
                message=f"Executing {query if self.log_query else 'query'}",
                logger=LOG,
            )

        return result

    async def aaggregate(self, collection_name: str, pipeline: list) -> list[dict]:
        s = datetime.now()
        collection_obj = await self.aget_collection(collection_name)
        result = await collection_obj.aggregate(pipeline).to_list(length=None)

        if self.log_time_taken:
            show_time_taken(
                s,
                message=f"Executing {pipeline if self.log_query else 'pipeline'}",
                logger=LOG,
            )

        return result

    async def adelete_collection(self, collection_name: str):
        db = await self.aget_database()
        try:
            await db.drop_collection(collection_name)
        except Exception as e:
            LOG.info(f"Failed to delete collection due to {e}")

    async def adelete_records(self, collection_name: str, query: dict):
        collection_obj = await self.aget_collection(collection_name)
        try:
            await collection_obj.delete_many(query)
        except Exception as e:
            LOG.info(
                f"Failed to delete records from {collection_name} due to {query} and error {e}"
            )
