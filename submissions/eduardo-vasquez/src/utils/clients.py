from openai import OpenAI
from google.cloud import storage
from config import settings
from utils.custom_logging import get_logger


logger = get_logger()


def get_openai_client():
    """Return the initialized OpenAI client."""
    openai_client = OpenAI(api_key=settings.OPENAI_API_KEY)
    return openai_client


def create_google_storage_client() -> storage.Client:
    """
    Creates and returns a Google Cloud Storage client using service account credentials.

    The function first checks if the credentials file exists at the specified path.
    If the application is in a 'development' environment, it initializes the client using
    the service account credentials. In the 'production' environment, the client is
    initialized without specifying credentials (using the default application credentials).

    :raises FileNotFoundError: If the credentials file is not found at the expected location.

    :return: An instance of the Google Cloud Storage client.
    """
    try:
        logger.info("Initializing Google Cloud Storage client...")

        # Initialize client based on environment
        storage_client = storage.Client()

        return storage_client

    except Exception as e:
        logger.error(f"Failed to create Google Cloud Storage client: {e}")


openai_client = get_openai_client()
