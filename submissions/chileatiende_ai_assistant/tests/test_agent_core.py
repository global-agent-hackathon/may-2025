import pytest
from unittest.mock import patch, MagicMock
from app.agent_core.agent_setup import get_agent, _agent, _agent_storage, get_agent_storage # Import _agent and _agent_storage to reset them
import os
# Need to import FirecrawlApp for patching its method
from firecrawl import FirecrawlApp

# Helper function to reset globals for test isolation
@pytest.fixture(autouse=True)
def reset_agent_globals():
    global _agent, _agent_storage
    _agent = None
    _agent_storage = None
    yield # test runs here
    _agent = None
    _agent_storage = None

def test_get_agent_missing_google_key(test_client):
    """Test get_agent when GOOGLE_API_KEY is missing."""
    app = test_client.application
    with app.app_context():
        # Simulate GOOGLE_API_KEY being None and FIRECRAWL_API_KEY being present
        with patch.dict(app.config, {
            'GOOGLE_API_KEY': None,
            'FIRECRAWL_API_KEY': 'False_API_KEY'
        }):
            with pytest.raises(ValueError, match="GOOGLE_API_KEY no configurada en .env"):
                get_agent()

def test_get_agent_missing_firecrawl_key(test_client):
    """Test get_agent when FIRECRAWL_API_KEY is missing. Expects ValueError from FirecrawlTool."""
    app = test_client.application
    with app.app_context():
        # Simulate FIRECRAWL_API_KEY being None and GOOGLE_API_KEY being present
        with patch.dict(app.config, {
            'FIRECRAWL_API_KEY': None,
            'GOOGLE_API_KEY': 'False_API_KEY'
        }):
            with pytest.raises(ValueError, match="Firecrawl API key no proporcionada"):
                get_agent() # This should now raise ValueError due to FirecrawlTool

def test_get_agent_successful_initialization(test_client):
    """Test successful agent initialization when all configs are present."""
    app = test_client.application
    # Ensure DATA_DIR exists for SqliteStorage, create if not (idempotent)
    data_path = app.config.get('DATA_DIR')
    if data_path and not os.path.exists(data_path):
        os.makedirs(data_path, exist_ok=True)

    # Also ensure dummy API keys are in config if not already by .env -> TestConfig
    # This is more of a safeguard for the test environment
    current_google_key = app.config.get('GOOGLE_API_KEY')
    current_firecrawl_key = app.config.get('FIRECRAWL_API_KEY')

    # We rely on TestConfig (and .env) to provide valid or dummy keys.
    # If GOOGLE_API_KEY or FIRECRAWL_API_KEY is None here, get_agent will fail as tested elsewhere.
    # We just need to ensure they are not None for this happy path test.
    assert current_google_key is not None, "Test setup error: GOOGLE_API_KEY is None in app.config"
    assert current_firecrawl_key is not None, "Test setup error: FIRECRAWL_API_KEY is None in app.config"

    with app.app_context():
        agent = get_agent()
        assert agent is not None
        from agno.agent import Agent # Local import for isinstance check
        assert isinstance(agent, Agent)
        storage = get_agent_storage()
        assert storage is not None
        from agno.storage.sqlite import SqliteStorage # local import
        assert isinstance(storage, SqliteStorage)

# Tests for chat_handler.py
from app.agent_core.chat_handler import handle_message

@patch('app.agent_core.chat_handler.get_agent')
def test_handle_message_agent_run_exception(mock_get_agent, test_client):
    """Test handle_message when agent.run() raises an exception."""
    mock_agent_instance = MagicMock()
    mock_agent_instance.run.side_effect = Exception("Simulated agent error")
    mock_get_agent.return_value = mock_agent_instance

    app = test_client.application # For app.logger access
    with app.app_context():
        with patch.object(app.logger, 'error') as mock_logger_error:
            response = handle_message("Hola, hablas con Gustavo", "user1", "session1")
            assert response
            mock_logger_error.assert_called_once()
            # Check that the error message includes the exception details
            args, _ = mock_logger_error.call_args
            assert args[0]

@patch('app.agent_core.chat_handler.get_agent')
def test_handle_message_unexpected_agent_response(mock_get_agent, test_client):
    """Test handle_message with an unexpected agent response type (not string, no .content)."""
    mock_agent_instance = MagicMock()
    # Simulate agent.run() returning an object without .content and not a string (e.g., an int)
    mock_agent_instance.run.return_value = 123 # An unexpected type
    mock_get_agent.return_value = mock_agent_instance

    app = test_client.application
    with app.app_context():
        with patch.object(app.logger, 'error') as mock_logger_error:
            response = handle_message("Hola, hablas con Gustavo", "user1", "session1")
            assert response == "Lo siento, ocurrió un error inesperado al procesar tu solicitud."
            mock_logger_error.assert_called_once()
            args, _ = mock_logger_error.call_args
            assert len(args) >= 0

@patch('app.agent_core.chat_handler.get_agent')
def test_handle_message_agent_returns_string(mock_get_agent, test_client):
    """Test handle_message when agent.run() directly returns a string."""
    mock_agent_instance = MagicMock()
    mock_agent_instance.run.return_value = "Direct string response from agent"
    mock_get_agent.return_value = mock_agent_instance

    app = test_client.application
    with app.app_context(): # app_context might not be strictly necessary if logger isn't used on this path
        response = handle_message("tHola, hablas con Gustavo", "user1", "session1")
        assert response == "Direct string response from agent"

# Tests for FirecrawlTool in agent_config.py
from app.agent_core.agent_config import FirecrawlTool, FIRECRAWL_INSTRUCTION, FIRECRAWL_TEMPLATE

@pytest.fixture
def firecrawl_tool_instance(test_client): # Use test_client for app_context if logger is used
    """Provides an instance of FirecrawlTool with a dummy API key."""
    # The tool init raises ValueError if api_key is None.
    # For testing the .search() method, we need a valid (dummy) key.
    app = test_client.application
    # Ensure TestConfig provides a dummy key, or set one explicitly for the tool if needed
    # For simplicity, we assume TestConfig or .env provides a key for FirecrawlTool instantiation.
    # If a test specifically needs to check behavior with a *real* key (live test), that's separate.
    api_key = app.config.get('FIRECRAWL_API_KEY', None)
    if not api_key: # Should not happen if TestConfig is set up as we did
        api_key = 'False_API_KEY'
    return FirecrawlTool(api_key=api_key, instruction=FIRECRAWL_INSTRUCTION, template=FIRECRAWL_TEMPLATE)

def test_firecrawl_tool_search_invalid_query(firecrawl_tool_instance):
    """Test FirecrawlTool.search with an invalid (too short) query."""
    response = firecrawl_tool_instance.search("abc")
    assert response == "Error: No se proporcionó una consulta de búsqueda válida (mínimo 5 caracteres)."
    response_empty = firecrawl_tool_instance.search("")
    assert response_empty == "Error: No se proporcionó una consulta de búsqueda válida (mínimo 5 caracteres)."

@patch.object(FirecrawlApp, 'search') # Patching the search method of the SDK's app object
def test_firecrawl_tool_search_successful(mock_sdk_search, firecrawl_tool_instance, test_client):
    """Test FirecrawlTool.search with a successful response from the SDK."""
    # Mock the data item as a dictionary, which is what result.get() would expect
    mock_data_item = {
        'url': 'https://www.chileatiende.gob.cl/fichas/VALID123',
        'title': 'Test Title',
        'markdown': 'Test Markdown Content'
    }
    
    mock_sdk_search_response = MagicMock() # This is the object returned by self.app.search()
    # This object is expected to have a .data attribute which is a list of results
    mock_sdk_search_response.data = [mock_data_item] 
    mock_sdk_search.return_value = mock_sdk_search_response

    response = firecrawl_tool_instance.search("Como obtengo la licencia de conducir")
    assert "Test Title" in response
    assert "Test Markdown Content" in response
    assert "https://www.chileatiende.gob.cl/fichas/" in response
    mock_sdk_search.assert_called_once()

@patch.object(FirecrawlApp, 'search')
def test_firecrawl_tool_search_results_filtered_out(mock_sdk_search, firecrawl_tool_instance, test_client):
    """Test FirecrawlTool.search when all results are filtered out."""
    mock_search_result_item_invalid_url = MagicMock()
    mock_search_result_item_invalid_url.configure_mock(**{
        'url': 'https://www.example.com/otherpage',
        'title': 'Filtered Title',
        'markdown': 'Filtered Content'
    })
    mock_search_result_item_pdf = MagicMock()
    mock_search_result_item_pdf.configure_mock(**{
        'url': 'https://www.chileatiende.gob.cl/fichas/anything.pdf',
        'title': 'PDF Title',
        'markdown': 'PDF Content'
    })
    mock_sdk_search_response = MagicMock()
    mock_sdk_search_response.data = [mock_search_result_item_invalid_url, mock_search_result_item_pdf]
    mock_sdk_search.return_value = mock_sdk_search_response

    response = firecrawl_tool_instance.search("Como obtengo un certificado de residencia?")
    assert response == "No se encontraron fichas de ChileAtiende relevantes para tu búsqueda."

@patch.object(FirecrawlApp, 'search')
def test_firecrawl_tool_search_no_results_from_sdk(mock_sdk_search, firecrawl_tool_instance, test_client):
    """Test FirecrawlTool.search when SDK returns no results (empty data)."""
    mock_sdk_search_response = MagicMock()
    mock_sdk_search_response.data = [] # Empty data list
    mock_sdk_search.return_value = mock_sdk_search_response
    response1 = firecrawl_tool_instance.search("Como obtengo certificado de residencia")
    assert response1 == "No se obtuvieron resultados de la búsqueda."

    mock_sdk_search.return_value = None # SDK returns None
    response2 = firecrawl_tool_instance.search("Como obtengo certificado de residencia")
    assert response2 == "No se obtuvieron resultados de la búsqueda."

@patch.object(FirecrawlApp, 'search')
def test_firecrawl_tool_search_sdk_exception(mock_sdk_search, firecrawl_tool_instance, test_client):
    """Test FirecrawlTool.search when the SDK's search method raises an exception."""
    mock_sdk_search.side_effect = Exception("SDK network error")
    
    app = test_client.application # For app.logger context
    with app.app_context():
        with patch.object(app.logger, 'error') as mock_logger_error:
            response = firecrawl_tool_instance.search("Como obtengo certificado de residencia")
            assert response == "Error al realizar la búsqueda: No se pudo conectar con el servicio externo."
            mock_logger_error.assert_called_once()
            args, _ = mock_logger_error.call_args
            assert "Error en FirecrawlTool.search: SDK network error" in args[0]