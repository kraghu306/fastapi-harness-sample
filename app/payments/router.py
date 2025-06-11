
"""
FastAPI router for payment operations.
"""
from typing import List, Optional
from uuid import UUID
import logging
from decimal import Decimal

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, condecimal, field_validator
from fastapi.encoders import jsonable_encoder

from app.payments.models import Payment, PaymentMethod, PaymentService, PaymentStatus

router = APIRouter(prefix="/payments", tags=["payments"])
payment_service = PaymentService()

logging.basicConfig(level=logging.WARNING)

class PaymentCreate(BaseModel):
    """Schema for creating a new payment."""
    order_id: UUID
    amount: Decimal  # Accepts string or number, Pydantic will coerce
    currency: str
    method: PaymentMethod

    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

class PaymentResponse(BaseModel):
    """Schema for payment response."""
    id: UUID
    order_id: UUID
    amount: float
    currency: str
    status: PaymentStatus
    method: PaymentMethod
    created_at: str
    updated_at: str
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    refund_amount: Optional[float] = None

    class Config:
        """Pydantic config."""
        from_attributes = True

class PaymentStatistics(BaseModel):
    """Schema for payment statistics."""
    total_payments: float
    total_amount: float
    completed_amount: float
    refunded_amount: float
    net_amount: float

@router.get("/", response_model=List[PaymentResponse])
async def get_payments():
    """Get all payments."""
    payments = payment_service.get_all_payments()
    return jsonable_encoder(payments)

@router.get("/statistics", response_model=PaymentStatistics)
async def get_payment_statistics():
    """Get payment statistics."""
    stats = payment_service.get_payment_statistics()
    return PaymentStatistics(
        total_payments=stats["total_payments"],
        total_amount=stats["total_amount"],
        completed_amount=stats["completed_amount"],
        refunded_amount=stats["refunded_amount"],
        net_amount=stats["net_amount"]
    )

@router.get("/status/{status}", response_model=List[PaymentResponse])
async def get_payments_by_status(status: PaymentStatus):
    """Get all payments with a specific status."""
    payments = payment_service.get_payments_by_status(status)
    return jsonable_encoder(payments)

@router.get("/method/{method}", response_model=List[PaymentResponse])
async def get_payments_by_method(method: PaymentMethod):
    """Get all payments with a specific method."""
    payments = payment_service.get_payments_by_method(method)
    return jsonable_encoder(payments)

@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(payment_id: UUID):
    """Get a payment by ID."""
    payment = payment_service.get_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return jsonable_encoder(payment)

@router.post("/", response_model=PaymentResponse)
async def create_payment(payment_data: PaymentCreate):
    """Create a new payment."""
    try:
        logging.warning(f"Incoming payment_data: {payment_data}")
        payment = payment_service.create_payment(
            order_id=payment_data.order_id,
            amount=payment_data.amount,
            currency=payment_data.currency,
            method=payment_data.method if isinstance(payment_data.method, PaymentMethod) else PaymentMethod(payment_data.method)
        )
        return jsonable_encoder(payment)
    except Exception as e:
        logging.error(f"Error in create_payment: {e}")
        raise

@router.post("/{payment_id}/process", response_model=PaymentResponse)
async def process_payment(payment_id: UUID):
    """Process a payment."""
    payment = payment_service.process_payment(payment_id)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")
    return jsonable_encoder(payment)

@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(payment_id: UUID, amount: Optional[str] = None):
    """Refund a payment."""
    try:
        refund_amount = Decimal(amount) if amount else None
        if refund_amount is not None and refund_amount <= 0:
            raise ValueError("Refund amount must be greater than 0")
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=422, detail=f"Invalid refund amount: {e}")

    payment = payment_service.refund_payment(payment_id, refund_amount)
    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found or cannot be refunded")
    return jsonable_encoder(payment) 
