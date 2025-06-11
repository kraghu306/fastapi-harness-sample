"""
Unit tests for the payments module.
"""
import pytest
from datetime import datetime
from decimal import Decimal
from uuid import UUID, uuid4

from app.payments.models import Payment, PaymentMethod, PaymentService, PaymentStatus

@pytest.fixture
def payment_service():
    """Fixture providing a PaymentService instance."""
    return PaymentService()

@pytest.fixture
def sample_payment():
    """Fixture providing a sample payment."""
    return Payment(
        id=uuid4(),
        order_id=uuid4(),
        amount=Decimal("99.99"),
        currency="USD",
        status=PaymentStatus.PENDING,
        method=PaymentMethod.CREDIT_CARD,
        created_at=datetime.now(),
        updated_at=datetime.now()
    )

def test_get_payment(payment_service, sample_payment):
    """Test getting a payment by ID."""
    payment_service._payments[sample_payment.id] = sample_payment
    
    retrieved_payment = payment_service.get_payment(sample_payment.id)
    assert retrieved_payment is not None
    assert retrieved_payment.id == sample_payment.id
    assert retrieved_payment.order_id == sample_payment.order_id
    assert retrieved_payment.amount == sample_payment.amount

def test_get_all_payments(payment_service):
    """Test getting all payments."""
    payments = payment_service.get_all_payments()
    assert isinstance(payments, list)
    assert len(payments) > 0
    assert all(isinstance(payment, Payment) for payment in payments)

def test_create_payment(payment_service):
    """Test creating a new payment."""
    order_id = uuid4()
    amount = Decimal("50.00")
    currency = "USD"
    method = PaymentMethod.CREDIT_CARD
    
    payment = payment_service.create_payment(order_id, amount, currency, method)
    
    assert isinstance(payment, Payment)
    assert payment.order_id == order_id
    assert payment.amount == amount
    assert payment.currency == currency
    assert payment.method == method
    assert payment.status == PaymentStatus.PENDING

def test_process_payment(payment_service, sample_payment):
    """Test processing a payment."""
    payment_service._payments[sample_payment.id] = sample_payment
    
    processed_payment = payment_service.process_payment(sample_payment.id)
    assert processed_payment is not None
    assert processed_payment.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]
    assert processed_payment.updated_at > sample_payment.created_at

def test_refund_payment(payment_service, sample_payment):
    """Test refunding a payment."""
    # First complete the payment
    sample_payment.status = PaymentStatus.COMPLETED
    payment_service._payments[sample_payment.id] = sample_payment
    
    refund_amount = Decimal("50.00")
    refunded_payment = payment_service.refund_payment(sample_payment.id, refund_amount)
    
    assert refunded_payment is not None
    assert refunded_payment.status == PaymentStatus.REFUNDED
    assert refunded_payment.refund_amount == refund_amount

def test_get_payments_by_status(payment_service, sample_payment):
    """Test getting payments by status."""
    payment_service._payments[sample_payment.id] = sample_payment
    
    status_payments = payment_service.get_payments_by_status(PaymentStatus.PENDING)
    assert isinstance(status_payments, list)
    assert all(payment.status == PaymentStatus.PENDING for payment in status_payments)

def test_get_payments_by_method(payment_service, sample_payment):
    """Test getting payments by method."""
    payment_service._payments[sample_payment.id] = sample_payment
    
    method_payments = payment_service.get_payments_by_method(PaymentMethod.CREDIT_CARD)
    assert isinstance(method_payments, list)
    assert all(payment.method == PaymentMethod.CREDIT_CARD for payment in method_payments)

def test_get_payment_statistics(payment_service, sample_payment):
    """Test getting payment statistics."""
    payment_service._payments[sample_payment.id] = sample_payment
    
    stats = payment_service.get_payment_statistics()
    assert isinstance(stats, dict)
    assert "total_payments" in stats
    assert "total_amount" in stats
    assert "completed_amount" in stats
    assert "refunded_amount" in stats
    assert "net_amount" in stats

@pytest.mark.parametrize("method", [
    PaymentMethod.CREDIT_CARD,
    PaymentMethod.DEBIT_CARD,
    PaymentMethod.BANK_TRANSFER,
    PaymentMethod.PAYPAL
])
def test_payment_methods(payment_service, method):
    """Parametrized test for different payment methods."""
    order_id = uuid4()
    payment = payment_service.create_payment(
        order_id=order_id,
        amount=Decimal("100.00"),
        currency="USD",
        method=method
    )
    assert payment.method == method

@pytest.mark.parametrize("status", [
    PaymentStatus.PENDING,
    PaymentStatus.PROCESSING,
    PaymentStatus.COMPLETED,
    PaymentStatus.FAILED,
    PaymentStatus.REFUNDED
])
def test_payment_statuses(payment_service, sample_payment, status):
    """Parametrized test for different payment statuses."""
    payment_service._payments[sample_payment.id] = sample_payment
    sample_payment.status = status
    
    status_payments = payment_service.get_payments_by_status(status)
    assert len(status_payments) > 0
    assert all(payment.status == status for payment in status_payments) 