import functions_framework
from config import settings
from utils import (
    embedder,
    create_qdrant_client,
    create_qdrant_collection,
    insert_data_into_qdrant,
    extract_text_and_metadata,
    get_logger,
)
from agents import team_agents

logger = get_logger()

# Connect to Qdrant
client_connection = create_qdrant_client()


@functions_framework.cloud_event
def offline_pipeline(cloud_event):
    """Event-based Cloud Function to ingest data into Qdrant."""
    try:
        logger.info("Starting offline pipeline...")
        data, full_document = extract_text_and_metadata(
            bucket_name=settings.BUCKET_NAME, extract_all=True
        )
        logger.info(f"Extracted data: {data}")
        logger.info(f"Extracted full_document: {full_document[0:20]}")

        create_qdrant_collection(
            qdrant_client=client_connection,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            vector_dimensions=settings.EMBEDDING_DIMENSIONS,
        )

        logger.info("Starting insertion...")
        insert_data_into_qdrant(
            data,
            client_connection,
            collection_name=settings.QDRANT_COLLECTION_NAME,
            embedder=embedder,
        )

        logger.info("Data inserted into Qdrant successfully.")

        logger.info("Start Agents...")
        team_agents.print_response(full_document)

    except Exception as e:
        return {"error": str(e)}, 500
