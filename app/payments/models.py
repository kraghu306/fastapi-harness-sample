
"""
Payment models and mock data for the payments module.
"""
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4

class PaymentStatus(str, Enum):
    """Payment status enumeration."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"

class PaymentMethod(str, Enum):
    """Payment method enumeration."""
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    BANK_TRANSFER = "bank_transfer"
    PAYPAL = "paypal"

@dataclass
class Payment:
    """Payment model with mock data generation capabilities."""
    id: UUID
    order_id: UUID
    amount: Decimal
    currency: str
    status: PaymentStatus
    method: PaymentMethod
    created_at: datetime
    updated_at: datetime
    transaction_id: Optional[str] = None
    error_message: Optional[str] = None
    refund_amount: Optional[Decimal] = None

class PaymentService:
    """Service class for payment operations with mock data."""
    
    def __init__(self):
        self._payments: Dict[UUID, Payment] = {}
        self._initialize_mock_data()
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock payment data."""
        mock_payments = [
            Payment(
                id=uuid4(),
                order_id=uuid4(),
                amount=Decimal("99.99"),
                currency="USD",
                status=PaymentStatus.COMPLETED,
                method=PaymentMethod.CREDIT_CARD,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                transaction_id="tx_123456"
            ),
            Payment(
                id=uuid4(),
                order_id=uuid4(),
                amount=Decimal("49.99"),
                currency="USD",
                status=PaymentStatus.FAILED,
                method=PaymentMethod.DEBIT_CARD,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                error_message="Insufficient funds"
            )
        ]
        for payment in mock_payments:
            self._payments[payment.id] = payment
    
    def get_payment(self, payment_id: UUID) -> Optional[Payment]:
        """Get a payment by ID."""
        return self._payments.get(payment_id)
    
    def get_all_payments(self) -> List[Payment]:
        """Get all payments."""
        return list(self._payments.values())
    
    def create_payment(self, order_id: UUID, amount: Decimal, currency: str, method: PaymentMethod) -> Payment:
        """Create a new payment."""
        # Validate amount
        if amount <= 0:
            raise ValueError("Payment amount must be greater than zero")
        
        # Validate currency
        valid_currencies = ["USD", "EUR", "GBP", "JPY", "CAD", "AUD"]
        if currency not in valid_currencies:
            raise ValueError(f"Unsupported currency: {currency}")
        
        payment = Payment(
            id=uuid4(),
            order_id=order_id,
            amount=amount,
            currency=currency,
            status=PaymentStatus.PENDING,
            method=method,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._payments[payment.id] = payment
        return payment
    
    def process_payment(self, payment_id: UUID) -> Optional[Payment]:
        """Process a payment (mock implementation)."""
        payment = self._payments.get(payment_id)
        if payment:
            # Simulate payment processing with random success/failure
            import random
            if random.random() < 0.8:  # 80% success rate
                payment.status = PaymentStatus.COMPLETED
                payment.transaction_id = f"tx_{uuid4().hex[:8]}"
            else:
                payment.status = PaymentStatus.FAILED
                payment.error_message = "Payment processing failed"
            payment.updated_at = datetime.now()
        return payment
    
    def refund_payment(self, payment_id: UUID, amount: Optional[Decimal] = None) -> Optional[Payment]:
        """Refund a payment."""
        payment = self._payments.get(payment_id)
        if payment and payment.status == PaymentStatus.COMPLETED:
            refund_amount = amount or payment.amount
            payment.status = PaymentStatus.REFUNDED
            payment.refund_amount = refund_amount
            payment.updated_at = datetime.now()
        return payment
    
    def get_payments_by_status(self, status: PaymentStatus) -> List[Payment]:
        """Get all payments with a specific status."""
        return [payment for payment in self._payments.values() if payment.status == status]
    
    def get_payments_by_method(self, method: PaymentMethod) -> List[Payment]:
        """Get all payments with a specific method."""
        return [payment for payment in self._payments.values() if payment.method == method]
    
    def get_payment_statistics(self) -> Dict[str, float]:
        """Calculate payment statistics."""
        total_payments = float(len(self._payments))
        total_amount = float(sum(payment.amount for payment in self._payments.values()))
        completed_amount = float(sum(
            payment.amount for payment in self._payments.values()
            if payment.status == PaymentStatus.COMPLETED
        ))
        refunded_amount = float(sum(
            payment.refund_amount or 0
            for payment in self._payments.values()
            if payment.status == PaymentStatus.REFUNDED
        ))
        return {
            "total_payments": total_payments,
            "total_amount": total_amount,
            "completed_amount": completed_amount,
            "refunded_amount": refunded_amount,
            "net_amount": completed_amount - refunded_amount
        } 
