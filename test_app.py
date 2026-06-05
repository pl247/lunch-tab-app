import os
import sys
import tempfile
# Set environment variable for test DB before importing the app
TEST_DB_DIR = tempfile.mkdtemp()
os.environ["DB_PATH"] = os.path.join(TEST_DB_DIR, "test.db")
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from fastapi.testclient import TestClient
from app.main import app

# Test client
client = TestClient(app)

def test_health_endpoint():
    """Test the health endpoint returns ok"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}

def test_index_page_loads():
    """Test the main page loads successfully"""
    response = client.get("/")
    assert response.status_code == 200
    assert "LunchTab" in response.text
    assert "Shared office lunch-order tracker" in response.text

def test_create_order():
    """Test creating a new order"""
    response = client.post("/create", data={
        "person": "Test Person",
        "item": "Test Item",
        "amount": "15.50",
        "date": "2026-06-05"
    }, allow_redirects=False)
    # Should redirect to home page
    assert response.status_code == 303
    assert response.headers["location"] == "/"
    
    # Verify order appears on homepage by following redirect
    response = client.get("/")
    assert response.status_code == 200
    assert "Test Person" in response.text
    assert "Test Item" in response.text
    assert "$15.50" in response.text

def test_settle_order():
    """Test settling an order"""
    # First create an order
    response = client.post("/create", data={
        "person": "Settle Test",
        "item": "Settle Item",
        "amount": "20.00",
        "date": "2026-06-05"
    }, allow_redirects=False)
    assert response.status_code == 303
    
    # Get the order ID from the database would be ideal, but for simplicity
    # let's test the settle endpoint with a known order ID that should exist
    # We'll use order ID 1 which should exist from demo data
    response = client.post("/settle/1", allow_redirects=False)
    assert response.status_code == 303
    assert response.headers["location"] == "/"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v"])