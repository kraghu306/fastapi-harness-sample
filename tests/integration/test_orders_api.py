
"""
Integration tests for the orders API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import UUID, uuid4

from app.main import app
from app.orders.models import OrderStatus

client = TestClient(app)

@pytest.fixture
def sample_user_id():
    """Fixture providing a sample user ID."""
    return str(uuid4())

@pytest.fixture
def sample_order_data(sample_user_id):
    """Fixture providing sample order data."""
    return {
        "user_id": sample_user_id,
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "unit_price": "19.99"
            }
        ],
        "shipping_address": "123 Test St"
    }

def test_get_orders():
    """Test getting all orders."""
    response = client.get("/orders/")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert len(orders) > 0

def test_create_order(sample_order_data):
    """Test creating a new order."""
    response = client.post("/orders/", json=sample_order_data)
    assert response.status_code == 200
    order = response.json()
    assert order["user_id"] == sample_order_data["user_id"]
    assert len(order["items"]) == len(sample_order_data["items"])
    assert order["status"] == OrderStatus.PENDING
    assert order["payment_status"] is False

def test_get_order_not_found():
    """Test getting a non-existent order."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/orders/{non_existent_id}")
    assert response.status_code == 404

def test_update_order_status(sample_order_data):
    """Test updating an order's status."""
    # First create an order
    create_response = client.post("/orders/", json=sample_order_data)
    order_id = create_response.json()["id"]
    
    # Update the order status
    new_status = OrderStatus.PROCESSING
    response = client.put(f"/orders/{order_id}/status", params={"status": new_status.value})
    assert response.status_code == 200
    updated_order = response.json()
    assert updated_order["status"] == new_status

def test_get_user_orders(sample_user_id, sample_order_data):
    """Test getting orders for a specific user."""
    # Create an order for the user
    client.post("/orders/", json=sample_order_data)
    
    # Get user's orders
    response = client.get(f"/orders/user/{sample_user_id}")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert all(order["user_id"] == sample_user_id for order in orders)

def test_get_orders_by_status(sample_order_data):
    """Test getting orders by status."""
    # Create an order
    client.post("/orders/", json=sample_order_data)
    
    # Get orders by status
    response = client.get(f"/orders/status/{OrderStatus.PENDING.value}")
    assert response.status_code == 200
    orders = response.json()
    assert isinstance(orders, list)
    assert all(order["status"] == OrderStatus.PENDING.value for order in orders)

def test_get_order_statistics(sample_order_data):
    """Test getting order statistics."""
    # Create an order
    client.post("/orders/", json=sample_order_data)
    
    # Get statistics
    response = client.get("/orders/statistics")
    assert response.status_code == 200
    stats = response.json()
    assert "total_orders" in stats
    assert "total_revenue" in stats
    assert "average_order_value" in stats
    assert stats["total_orders"] > 0
    assert stats["total_revenue"] > 0

def test_create_order_duplicate_test(sample_order_data):
    """Test creating an order (duplicate test for verification)."""
    response = client.post("/orders/", json=sample_order_data)
    assert response.status_code == 200
    order = response.json()
    assert order["user_id"] == sample_order_data["user_id"]
    assert len(order["items"]) == len(sample_order_data["items"])

@pytest.mark.parametrize("status", [
    OrderStatus.PENDING,
    OrderStatus.PROCESSING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELLED
])
def test_order_status_workflow(sample_order_data, status):
    """Parametrized test for order status workflow."""
    # Create an order
    create_response = client.post("/orders/", json=sample_order_data)
    order_id = create_response.json()["id"]
    
    # Update status
    response = client.put(f"/orders/{order_id}/status", params={"status": status.value})
    assert response.status_code == 200
    updated_order = response.json()
    assert updated_order["status"] == status 
