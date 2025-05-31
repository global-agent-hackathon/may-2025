import json
from unittest.mock import patch

def test_chat_api_no_message(test_client):
    """Test the chat API without a message, should return an error or specific response."""
    response = test_client.post('/api/chat', data=json.dumps({}), content_type='application/json')
    assert response.status_code == 400 # Assuming bad request if no message

def test_chat_api_with_message(test_client):
    """Test the chat API with a message."""
    data = {'message': 'Hola'}
    response = test_client.post('/api/chat', data=json.dumps(data), content_type='application/json')
    assert response.status_code == 200
    response_data = response.json
    assert 'response' in response_data

def test_chat_api_handle_message_exception(test_client):
    """Test the chat API when handle_message raises an exception."""
    data = {'message': 'Test exception'}
    
    # Patch 'handle_message' in the context of 'app.api.routes' module
    with patch('app.api.routes.handle_message') as mock_handle_message:
        mock_handle_message.side_effect = Exception("Test simulated error")
        
        response = test_client.post('/api/chat', data=json.dumps(data), content_type='application/json')
        
    assert response.status_code == 500
    response_data = response.json
    assert 'error' in response_data
    assert response_data['error'] == 'Ocurrió un error interno al procesar tu solicitud.'
    mock_handle_message.assert_called_once() 