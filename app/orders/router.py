
"""
FastAPI router for order operations.
"""
from typing import List
from uuid import UUID
import logging

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, conint, condecimal
from fastapi.encoders import jsonable_encoder

from app.orders.models import Order, OrderItem, OrderService, OrderStatus

router = APIRouter(prefix="/orders", tags=["orders"])
order_service = OrderService()

logging.basicConfig(level=logging.WARNING)

class OrderItemCreate(BaseModel):
    """Schema for creating an order item."""
    product_id: UUID
    quantity: conint(gt=0)
    unit_price: condecimal(gt=0)

class OrderCreate(BaseModel):
    """Schema for creating a new order."""
    user_id: UUID
    items: List[OrderItemCreate]
    shipping_address: str

class OrderItemResponse(BaseModel):
    """Schema for order item response."""
    id: UUID
    product_id: UUID
    quantity: int
    unit_price: float
    total_price: float

    class Config:
        """Pydantic config."""
        from_attributes = True

class OrderResponse(BaseModel):
    """Schema for order response."""
    id: UUID
    user_id: UUID
    items: List[OrderItemResponse]
    status: OrderStatus
    created_at: str
    updated_at: str
    total_amount: float
    shipping_address: str
    payment_status: bool

    class Config:
        """Pydantic config."""
        from_attributes = True

class OrderStatistics(BaseModel):
    """Schema for order statistics."""
    total_orders: float
    total_revenue: float
    average_order_value: float

@router.get("/statistics", response_model=OrderStatistics)
async def get_order_statistics():
    """Get order statistics."""
    stats = order_service.calculate_order_statistics()
    logging.warning(f"Order statistics: {stats} | Types: {[type(v) for v in stats.values()]}")
    print(f"Order statistics: {stats} | Types: {[type(v) for v in stats.values()]}")
    return OrderStatistics(**stats)

@router.get("/", response_model=List[OrderResponse])
async def get_orders():
    """Get all orders."""
    orders = order_service.get_all_orders()
    return jsonable_encoder(orders)

@router.get("/{order_id}", response_model=OrderResponse)
async def get_order(order_id: UUID):
    """Get an order by ID."""
    order = order_service.get_order(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return jsonable_encoder(order)

@router.post("/", response_model=OrderResponse)
async def create_order(order_data: OrderCreate):
    """Create a new order."""
    order = order_service.create_order(**order_data.model_dump())
    return jsonable_encoder(order)

@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(order_id: UUID, status: OrderStatus):
    """Update the status of an order."""
    order = order_service.update_order_status(order_id, status)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    return jsonable_encoder(order)

@router.get("/user/{user_id}", response_model=List[OrderResponse])
async def get_user_orders(user_id: UUID):
    """Get all orders for a user."""
    orders = order_service.get_user_orders(user_id)
    return jsonable_encoder(orders)

@router.get("/status/{status}", response_model=List[OrderResponse])
async def get_orders_by_status(status: OrderStatus):
    """Get all orders with a specific status."""
    orders = order_service.get_orders_by_status(status)
    return jsonable_encoder(orders) 
