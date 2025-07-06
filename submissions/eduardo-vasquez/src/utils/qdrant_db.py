from qdrant_client import QdrantClient
from config import settings
from qdrant_client.models import (
    VectorParams,
    Distance,
    PointStruct,
    PayloadSchemaType,
    Filter,
    FieldCondition,
    MatchValue,
)
from utils.embedding_model import embed_text, Embedder, embedder
import uuid
from typing import Any
from utils.custom_logging import get_logger

logger = get_logger()


def create_qdrant_client() -> QdrantClient:
    """
    Creates a connection to the Qdrant client.

    Args:
       env (str): The environment mode ('dev' or 'prod').

    Returns:
        QdrantClient: An instance of the QdrantClient if the connection is successful.
    """
    try:
        # Try to create a Qdrant client connection
        logger.info("Start Qdrant connection")
        client = QdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        return client
    except Exception as e:
        # Log the error and return None
        logger.error(f"Failed to connect to Qdrant: {str(e)}")


def create_qdrant_collection(
    qdrant_client: QdrantClient,
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
    vector_dimensions: int = settings.EMBEDDING_DIMENSIONS,
) -> None:
    """Creates a Qdrant collection if it does not already exist.

    Args:
        qdrant_client (QdrantClient): The Qdrant client instance to interact with.
        collection_name (str, optional): The name of the collection to create.
            Defaults to settings.QDRANT_COLLECTION_NAME.
        vector_dimensions (int, optional): The dimensionality of vectors to store.
            Defaults to settings.EMBEDDING_DIMENSIONS.

    Raises:
        ValueError: If an error occurs while creating the collection.
    """
    try:
        # Check if the collection already exists
        if not qdrant_client.collection_exists(collection_name):
            # Proceed to create the collection with the provided configurations
            qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=vector_dimensions, distance=Distance.COSINE
                ),
            )
            logger.info(
                f"Collection '{collection_name}' has been successfully created."
            )
        else:
            logger.info(f"Collection '{collection_name}' already exists.")

    except Exception as e:
        # Catch any error that occurs during the collection creation process
        logger.error(f"Failed to create collection '{collection_name}': {str(e)}")


def prepare_points(data: list, embedder: Embedder) -> list:
    """
    Prepares points for upsert into Qdrant.

    Args:
        data (list): List of dictionaries containing 'text' and 'metadata'.
        embedder (Embedder): The Embedder model to use for embedding text.

    Returns:
        list: A list of PointStruct objects for insertion into Qdrant.
    """
    try:
        logger.info("Starting to prepare points for Qdrant...")
        points = []
        for item in data:
            vector = embed_text(item["text"], embedder)
            point = PointStruct(
                id=str(uuid.uuid4()),  # Generate a unique UUID
                vector=vector,
                payload={
                    "meta_data": item.get("metadata", {}),
                    "content": item.get("text", ""),
                    "name": item.get("name", {}),
                    "usage": None,
                },
            )
            points.append(point)
        logger.info("Finished preparing points for Qdrant...")
        return points
    except Exception as e:
        logger.error(
            f"Error preparing point for text: {item['text'][:30]}... | Error: {str(e)}"
        )


def insert_data_into_qdrant(
    data: list, qdrant_client: QdrantClient, collection_name: str, embedder: Embedder
) -> None:
    """
    Embeds text and inserts metadata into Qdrant.

    Args:
        data (list): List of dictionaries containing 'text' and 'metadata'.
        qdrant_client (QdrantClient): The Qdrant client instance to use for insertion.
        collection_name (str): The name of the Qdrant collection where the data will be stored.
        embed_model (Embedder): The model used to embed the text.

    Returns:
        None
    """
    try:
        logger.info("Starting prepare_points...")
        points = prepare_points(data, embedder)
        logger.info(f"Prepared {len(points)} points for insertion into Qdrant.")
        logger.info(f"Points {points}")
        qdrant_client.upsert(collection_name=collection_name, points=points)
        logger.info(
            f"Successfully inserted {len(points)} points into '{collection_name}' collection."
        )
    except Exception as e:
        logger.error(
            f"Error inserting data into Qdrant collection '{collection_name}': {str(e)}"
        )


# insert_data_into_qdrant(data, client_connection, collection_name="meetings-test2", embedder=embedder)


def create_payload_index(
    qdrant_client: QdrantClient,
    field_name: str,
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
    field_schema: PayloadSchemaType = PayloadSchemaType.KEYWORD,
):
    """
    Creates a payload index for a given collection and field.

    Args:
        client_connection: The client connection object to interact with the database.
        collection_name (str): The name of the collection.
        field_name (str): The name of the field to index.
        field_schema: The schema type for the field.
    """
    try:
        logger.info(
            f"Creating payload index for collection: {collection_name}, field: {field_name}"
        )
        qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name=field_name,
            field_schema=field_schema,
        )

    except Exception as e:
        logger.error(
            f"Error creating payload index for collection: {collection_name}, field: {field_name}: {e}",
            exc_info=True,
        )


def search_in_qdrant(
    qdrant_client: QdrantClient,
    input_question: str,
    embedder: Embedder = embedder,
    collection_name: str = settings.QDRANT_COLLECTION_NAME,
    k: int = 5,
    metadata_filters: dict = None,
    is_summary: str = False,
) -> list:
    """
        Searches for similar vectors in Qdrant, with optional metadata filtering.

        Args:
            qdrant_client (QdrantClient): The Qdrant client instance to use for searching.
            input_question (str): The text query to search for.
            embed_model (Embedder): The embedding model for vectorizing the query.
            collection_name (str): The name of the Qdrant collection to search in.
            k (int, optional): The maximum number of results to return. Defaults to 5.
            metadata_filters (dict, optional): Key-value pairs to filter results based on metadata.
    a
        Returns:
            list: A list of search results.
    """
    try:
        query_vector = embed_text(input_question, embedder)
        query_filter = None

        # If metadata_filters is provided, construct the Qdrant filter
        if metadata_filters:
            filter_conditions = []
            for key, value in metadata_filters.items():
                # Extract the first value if the input is a list
                single_value = value[0] if isinstance(value, list) and value else value

                filter_conditions.append(
                    FieldCondition(key=key, match=MatchValue(value=single_value))
                )

            query_filter = Filter(must=filter_conditions)

        # Messages to retrieve
        k_retrieved = 100 if is_summary else k

        # Perform the query with or without filters
        results = qdrant_client.query_points(
            collection_name=collection_name,
            query=query_vector,
            limit=k_retrieved,
            query_filter=query_filter,  # This is None if no filters were provided
        )

        return results
    except Exception as e:
        logger.error(
            f"Error searching in Qdrant collection '{collection_name}': {str(e)}"
        )


def process_qdrant_conversation(qdrant_results: Any) -> str:
    """
    Extracts, sorts, and formats conversation data from Qdrant results.

    Args:
        qdrant_results (Any): The results containing conversation points.

    Returns:
        str: A formatted conversation string.
    """
    try:
        logger.info("Extracing relevant data from Qdrant payload...")
        # Step 1: Extract relevant data
        conversation_data = [
            {
                "message_number": point.payload["message_number"],
                "speaker_name": point.payload["speaker_name"],
                "text": point.payload["text"],
            }
            for point in qdrant_results.points
        ]
        logger.info("Sorting the conversation...")
        # Step 2: Sort the list by 'message_number'
        conversation_data_sorted = sorted(
            conversation_data, key=lambda x: x["message_number"]
        )

        logger.info("Formatting the conversation...")
        # Step 3: Format the conversation by speaker and text
        conversation = "\n".join(
            [
                f"{point['speaker_name']}: \"{point['text']}\""
                for point in conversation_data_sorted
            ]
        )

        return conversation
    except Exception as e:
        logger.error(f"Error formatting conversation: {e}")


# if __name__ in "__main__":
#     # Import the function for extracting text and metadata from GCS
#     from utils.data_extraction import extract_text_and_metadata

#     # Step 1: Initialize the Qdrant client
#     qdrant_client = create_qdrant_client()

#     # Step 2: Create a new Qdrant collection for storing embeddings and metadata
#     create_qdrant_collection(
#         qdrant_client=qdrant_client,
#         collection_name=settings.QDRANT_COLLECTION_NAME,
#         vector_dimensions=settings.EMBEDDING_DIMENSIONS,
#     )

#     # Step 3: Extract text and metadata from DOCX files stored in the GCS bucket
#     data = extract_text_and_metadata(bucket_name=settings.BUCKET_NAME, extract_all=True)

#     # Step 4: Insert the extracted data (including embeddings) into the Qdrant collection
#     insert_data_into_qdrant(
#         data=data,
#         qdrant_client=qdrant_client,
#         collection_name=settings.QDRANT_COLLECTION_NAME,
#         embedder=embedder,
#     )

#     # Step 5: Create indexes on specific metadata fields to optimize filtered searches
#     create_payload_index(qdrant_client, field_name="speaker_name")
#     create_payload_index(qdrant_client, field_name="meeting_title")
