# core/weaviate_client.py
import weaviate
import weaviate.classes as wvc 
from weaviate.classes.init import Auth
from core.config import settings

_weaviate_client_instance = None
WEAVIATE_CLASS_NAME = "EmailMemory" 

def get_weaviate_client():
    global _weaviate_client_instance
    if _weaviate_client_instance is None:
        if not settings.WEAVIATE_URL:
            print("Warning: WEAVIATE_URL not configured. Weaviate integration will be skipped.")
            return None
        
        auth_config = None
        headers = {}

        if settings.WEAVIATE_API_KEY:
            headers["Authorization"] = f"Bearer {settings.WEAVIATE_API_KEY}"

        try:
            _weaviate_client_instance = weaviate.connect_to_weaviate_cloud(
                cluster_url=settings.WEAVIATE_URL,
                auth_credentials=Auth.api_key(settings.WEAVIATE_API_KEY),
            )
            print(f"Attempting to connect to Weaviate at {settings.WEAVIATE_URL}...")
            if not _weaviate_client_instance.is_ready():
                 raise ConnectionError("Weaviate client is not ready. Check connection and credentials.")
            print("Weaviate client initialized and ready.")
            ensure_email_memory_schema(_weaviate_client_instance)
        except Exception as e:
            print(f"Error initializing Weaviate client: {e}")
            _weaviate_client_instance = None
    return _weaviate_client_instance

def ensure_email_memory_schema(client: weaviate.WeaviateClient): # Use WeaviateClient type hint
    """
    Ensures the EmailMemory class schema exists in Weaviate.
    """
    if client is None:
        print("Weaviate client not initialized, cannot ensure schema.")
        return

    try:
        if client.collections.exists(WEAVIATE_CLASS_NAME):
            print(f"Weaviate class '{WEAVIATE_CLASS_NAME}' already exists.")
            return

        print(f"Creating Weaviate class '{WEAVIATE_CLASS_NAME}'...")

        properties = [
            wvc.Property(name="appUserId", data_type=wvc.DataType.TEXT, description="Application's User ID"),
            wvc.Property(name="messageId", data_type=wvc.DataType.TEXT, description="Unique message ID (Gmail ID or app-generated)"),
            wvc.Property(name="sourceType", data_type=wvc.DataType.TEXT, description="e.g., email_received, email_sent_by_app"),
            wvc.Property(name="fromAddress", data_type=wvc.DataType.TEXT), 
            wvc.Property(name="fromName", data_type=wvc.DataType.TEXT),
            wvc.Property(name="toAddress", data_type=wvc.DataType.TEXT, skip_vectorization=True),
            wvc.Property(name="subject", data_type=wvc.DataType.TEXT),
            wvc.Property(name="bodyPlainText", data_type=wvc.DataType.TEXT, description="The main content for vectorization"),
            wvc.Property(name="tags", data_type=wvc.DataType.TEXT_ARRAY), 
            wvc.Property(name="messageTimestampISO", data_type=wvc.DataType.DATE, description="Timestamp of the email in ISO format (UTC)"),
        ]

        vectorizer_config = wvc.Configure.Vectorizer.none()

        client.collections.create(
            name=WEAVIATE_CLASS_NAME,
            properties=properties,
            vectorizer_config=vectorizer_config,
            inverted_index_config=wvc.Configure.inverted_index(
                bm25_k1=1.2,
                bm25_b=0.75,
                stopwords_preset="en",
                stopwords_additions=None,
                stopwords_removals=None
            )
        )
        print(f"Weaviate class '{WEAVIATE_CLASS_NAME}' created successfully.")

    except Exception as e:
        print(f"Error creating or checking Weaviate schema '{WEAVIATE_CLASS_NAME}': {e}")