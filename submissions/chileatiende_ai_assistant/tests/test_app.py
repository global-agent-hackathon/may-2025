def test_app_creation(test_client):
    """Test that the Flask app is created and accessible."""
    assert test_client.application is not None

def test_index_route(test_client):
    """Test the index route (/) returns a successful response."""
    response = test_client.get('/')
    assert response.status_code == 200
    assert b"Asistente ChileAtiende" in response.data # Check for a keyword in your index.html 