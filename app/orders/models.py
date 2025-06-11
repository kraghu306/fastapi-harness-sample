"""
Order models and mock data for the orders module.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional, Union
from uuid import UUID, uuid4

class OrderStatus(str, Enum):
    """Order status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

@dataclass
class OrderItem:
    """Order item model."""
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: Decimal
    total_price: Decimal

@dataclass
class Order:
    """Order model with mock data generation capabilities."""
    id: UUID
    user_id: UUID
    items: List[OrderItem]
    status: OrderStatus
    created_at: datetime
    updated_at: datetime
    total_amount: Decimal
    shipping_address: str
    payment_status: bool = False

class OrderService:
    """Service class for order operations with mock data."""
    
    def __init__(self):
        self._orders: Dict[UUID, Order] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock order data."""
        mock_orders = [
            Order(
                id=uuid4(),
                user_id=uuid4(),
                items=[
                    OrderItem(
                        id=uuid4(),
                        product_id=uuid4(),
                        quantity=2,
                        unit_price=Decimal("19.99"),
                        total_price=Decimal("39.98")
                    )
                ],
                status=OrderStatus.PENDING,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                total_amount=Decimal("39.98"),
                shipping_address="123 Main St, City, Country"
            ),
            Order(
                id=uuid4(),
                user_id=uuid4(),
                items=[
                    OrderItem(
                        id=uuid4(),
                        product_id=uuid4(),
                        quantity=1,
                        unit_price=Decimal("99.99"),
                        total_price=Decimal("99.99")
                    )
                ],
                status=OrderStatus.DELIVERED,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                total_amount=Decimal("99.99"),
                shipping_address="456 Oak St, City, Country",
                payment_status=True
            )
        ]
        for order in mock_orders:
            self._orders[order.id] = order
    
    def get_order(self, order_id: UUID) -> Optional[Order]:
        """Get an order by ID."""
        return self._orders.get(order_id)
    
    def get_all_orders(self) -> List[Order]:
        """Get all orders."""
        return list(self._orders.values())
    
    def create_order(self, user_id: UUID, items: List[Union[dict, OrderItem]], shipping_address: str) -> Order:
        """Create a new order."""
        # Validate input
        if not items:
            raise ValueError("Order must have at least one item")
        
        # Validate user_id is a proper UUID
        if isinstance(user_id, str):
            try:
                user_id = UUID(user_id)
            except ValueError:
                raise ValueError("Invalid user_id format")
        
        # Convert input items to OrderItem objects if they are dictionaries
        order_items = [
            item if isinstance(item, OrderItem) else OrderItem(
                id=uuid4(),
                product_id=item['product_id'],
                quantity=max(1, abs(item['quantity'])),  # Ensure positive quantity
                unit_price=Decimal(str(item['unit_price'])),
                total_price=Decimal(str(item['unit_price'])) * max(1, abs(item['quantity']))
            )
            for item in items
        ]
        total_amount = sum(item.total_price for item in order_items)
        order = Order(
            id=uuid4(),
            user_id=user_id,
            items=order_items,
            status=OrderStatus.PENDING,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            total_amount=total_amount,
            shipping_address=shipping_address
        )
        self._orders[order.id] = order
        return order
    
    def update_order_status(self, order_id: UUID, status: OrderStatus) -> Optional[Order]:
        """Update an order's status."""
        order = self._orders.get(order_id)
        if order:
            order.status = status
            order.updated_at = datetime.now()
        return order
    
    def get_user_orders(self, user_id: UUID) -> List[Order]:
        """Get all orders for a user."""
        return [order for order in self._orders.values() if order.user_id == user_id]
    
    def get_orders_by_status(self, status: OrderStatus) -> List[Order]:
        """Get all orders with a specific status."""
        return [order for order in self._orders.values() if order.status == status]
    
    def calculate_order_statistics(self) -> Dict[str, float]:
        """Calculate order statistics."""
        total_orders = len(self._orders)
        total_revenue = float(sum(order.total_amount for order in self._orders.values()))
        avg_order_value = total_revenue / total_orders if total_orders > 0 else 0.0
        return {
            "total_orders": float(total_orders),
            "total_revenue": total_revenue,
            "average_order_value": avg_order_value
        } 