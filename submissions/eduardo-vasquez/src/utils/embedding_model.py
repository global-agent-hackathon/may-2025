from openai import OpenAI
from utils.clients import get_openai_client
from config import settings
from utils.custom_logging import get_logger

logger = get_logger()

openai_client = get_openai_client()


class Embedder:
    def __init__(self, provider: str, model_name: str = None):
        self.provider = provider

        if provider == "openai":
            self.model = model_name or "text-embedding-ada-002"

    def encode(self, text: str, client: OpenAI = openai_client) -> list:

        if self.provider == "openai":
            response = client.embeddings.create(model=self.model, input=[text])
            return response.data[0].embedding


embedder = Embedder(
    provider=settings.EMBEDDING_PROVIDER, model_name=settings.EMBEDDING_MODEL
)


def embed_text(text: str, embedder: Embedder) -> list:
    """
    Embeds the text using the provided model.

    Args:
        text (str): The text to embed.
        embed_model (Embedder): The Embedder model to use for embedding.

    Returns:
        list: The vector representation of the text.
    """
    try:
        return embedder.encode(text)
    except Exception as e:
        logger.error(f"Error embedding text: {text[:30]}... | Error: {str(e)}")
