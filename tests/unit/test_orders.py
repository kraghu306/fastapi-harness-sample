
"""
Unit tests for the orders module.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.orders.models import Order, OrderItem, OrderService, OrderStatus

@pytest.fixture
def order_service():
    """Fixture providing an OrderService instance."""
    return OrderService()

@pytest.fixture
def sample_order_item():
    """Fixture providing a sample order item."""
    return OrderItem(
        id=uuid4(),
        product_id=uuid4(),
        quantity=2,
        unit_price=Decimal("19.99"),
        total_price=Decimal("39.98")
    )

@pytest.fixture
def sample_order(order_service, sample_order_item):
    """Fixture providing a sample order."""
    user_id = uuid4()
    return Order(
        id=uuid4(),
        user_id=user_id,
        items=[sample_order_item],
        status=OrderStatus.PENDING,
        created_at=datetime.now(),
        updated_at=datetime.now(),
        total_amount=Decimal("39.98"),
        shipping_address="123 Test St"
    )

def test_get_order(order_service, sample_order):
    """Test getting an order by ID."""
    order_service._orders[sample_order.id] = sample_order
    
    retrieved_order = order_service.get_order(sample_order.id)
    assert retrieved_order is not None
    assert retrieved_order.id == sample_order.id
    assert retrieved_order.user_id == sample_order.user_id
    assert len(retrieved_order.items) == len(sample_order.items)

def test_get_all_orders(order_service):
    """Test getting all orders."""
    orders = order_service.get_all_orders()
    assert isinstance(orders, list)
    assert len(orders) > 0
    assert all(isinstance(order, Order) for order in orders)

def test_create_order(order_service, sample_order_item):
    """Test creating a new order."""
    user_id = uuid4()
    items = [sample_order_item]
    shipping_address = "456 Test Ave"
    
    order = order_service.create_order(user_id, items, shipping_address)
    
    assert isinstance(order, Order)
    assert order.user_id == user_id
    assert len(order.items) == len(items)
    assert order.shipping_address == shipping_address
    assert order.status == OrderStatus.PENDING
    assert order.payment_status is False

def test_update_order_status(order_service, sample_order):
    """Test updating an order's status."""
    order_service._orders[sample_order.id] = sample_order
    
    new_status = OrderStatus.PROCESSING
    updated_order = order_service.update_order_status(sample_order.id, new_status)
    
    assert updated_order is not None
    assert updated_order.status == new_status
    assert updated_order.updated_at > sample_order.created_at

def test_get_user_orders(order_service, sample_order):
    """Test getting orders for a specific user."""
    order_service._orders[sample_order.id] = sample_order
    
    user_orders = order_service.get_user_orders(sample_order.user_id)
    assert isinstance(user_orders, list)
    assert len(user_orders) > 0
    assert all(order.user_id == sample_order.user_id for order in user_orders)

def test_get_orders_by_status(order_service, sample_order):
    """Test getting orders by status."""
    order_service._orders[sample_order.id] = sample_order
    
    status_orders = order_service.get_orders_by_status(OrderStatus.PENDING)
    assert isinstance(status_orders, list)
    assert all(order.status == OrderStatus.PENDING for order in status_orders)

def test_calculate_order_statistics(order_service, sample_order):
    """Test calculating order statistics."""
    order_service._orders[sample_order.id] = sample_order
    
    stats = order_service.calculate_order_statistics()
    assert isinstance(stats, dict)
    assert "total_orders" in stats
    assert "total_revenue" in stats
    assert "average_order_value" in stats
    assert stats["total_orders"] > 0
    assert stats["total_revenue"] > 0

@pytest.mark.parametrize("status", [
    OrderStatus.PENDING,
    OrderStatus.PROCESSING,
    OrderStatus.SHIPPED,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELLED
])
def test_order_status_enum(order_service, sample_order, status):
    """Parametrized test for order status updates."""
    order_service._orders[sample_order.id] = sample_order
    
    updated_order = order_service.update_order_status(sample_order.id, status)
    assert updated_order is not None
    assert updated_order.status == status

@pytest.mark.parametrize("quantity,unit_price,expected_total", [
    (1, Decimal("10.00"), Decimal("10.00")),
    (2, Decimal("15.00"), Decimal("30.00")),
    (3, Decimal("20.00"), Decimal("60.00")),
])
def test_order_item_calculation(quantity, unit_price, expected_total):
    """Parametrized test for order item price calculations."""
    item = OrderItem(
        id=uuid4(),
        product_id=uuid4(),
        quantity=quantity,
        unit_price=unit_price,
        total_price=quantity * unit_price
    )
    assert item.total_price == expected_total 
