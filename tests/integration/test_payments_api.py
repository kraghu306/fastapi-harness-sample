"""
Integration tests for the payments API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import UUID, uuid4

from app.main import app
from app.payments.models import PaymentMethod, PaymentStatus

client = TestClient(app)

@pytest.fixture
def sample_order_id():
    """Fixture providing a sample order ID."""
    return str(uuid4())

@pytest.fixture
def sample_payment_data(sample_order_id):
    """Fixture providing sample payment data."""
    return {
        "order_id": sample_order_id,
        "amount": "99.99",
        "currency": "USD",
        "method": "credit_card"
    }

def test_get_payments():
    """Test getting all payments."""
    response = client.get("/payments/")
    assert response.status_code == 200
    payments = response.json()
    assert isinstance(payments, list)
    assert len(payments) > 0

def test_create_payment(sample_payment_data):
    """Test creating a new payment."""
    response = client.post("/payments/", json=sample_payment_data)
    assert response.status_code == 200
    payment = response.json()
    assert payment["order_id"] == sample_payment_data["order_id"]
    assert payment["amount"] == float(sample_payment_data["amount"])
    assert payment["currency"] == sample_payment_data["currency"]
    assert payment["method"] == sample_payment_data["method"]
    assert payment["status"] == PaymentStatus.PENDING

def test_get_payment_not_found():
    """Test getting a non-existent payment."""
    non_existent_id = "00000000-0000-0000-0000-000000000000"
    response = client.get(f"/payments/{non_existent_id}")
    assert response.status_code == 404

def test_process_payment(sample_payment_data):
    """Test processing a payment."""
    # First create a payment
    create_response = client.post("/payments/", json=sample_payment_data)
    payment_id = create_response.json()["id"]
    
    # Process the payment
    response = client.post(f"/payments/{payment_id}/process")
    assert response.status_code == 200
    processed_payment = response.json()
    assert processed_payment["status"] in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]

def test_refund_payment(sample_payment_data):
    """Test refunding a payment."""
    # First create and process a payment
    create_response = client.post("/payments/", json=sample_payment_data)
    payment_id = create_response.json()["id"]
    
    # Process the payment until it's completed
    while True:
        process_response = client.post(f"/payments/{payment_id}/process")
        if process_response.json()["status"] == PaymentStatus.COMPLETED:
            break
    
    # Refund the payment
    refund_amount = "50.00"
    response = client.post(
        f"/payments/{payment_id}/refund",
        params={"amount": refund_amount}
    )
    assert response.status_code == 200
    refunded_payment = response.json()
    assert refunded_payment["status"] == PaymentStatus.REFUNDED
    assert float(refunded_payment["refund_amount"]) == float(refund_amount)

def test_get_payments_by_status(sample_payment_data):
    """Test getting payments by status."""
    # Create a payment
    client.post("/payments/", json=sample_payment_data)
    
    # Get payments by status
    response = client.get(f"/payments/status/{PaymentStatus.PENDING.value}")
    assert response.status_code == 200
    payments = response.json()
    assert isinstance(payments, list)
    assert all(payment["status"] == PaymentStatus.PENDING.value for payment in payments)

def test_get_payments_by_method(sample_payment_data):
    """Test getting payments by method."""
    # Create a payment
    client.post("/payments/", json=sample_payment_data)
    
    # Get payments by method
    response = client.get(f"/payments/method/{PaymentMethod.CREDIT_CARD.value}")
    assert response.status_code == 200
    payments = response.json()
    assert isinstance(payments, list)
    assert all(payment["method"] == PaymentMethod.CREDIT_CARD.value for payment in payments)

def test_get_payment_statistics(sample_payment_data):
    """Test getting payment statistics."""
    # Create a payment
    client.post("/payments/", json=sample_payment_data)
    
    # Get statistics
    response = client.get("/payments/statistics")
    if response.status_code != 200:
        print("DEBUG 422 response:", response.json())
    assert response.status_code == 200
    stats = response.json()
    assert "total_payments" in stats
    assert "total_amount" in stats
    assert "completed_amount" in stats
    assert "refunded_amount" in stats
    assert "net_amount" in stats

def test_create_payment_duplicate_test(sample_payment_data):
    """Test creating a payment (duplicate test for verification)."""
    response = client.post("/payments/", json=sample_payment_data)
    assert response.status_code == 200
    payment = response.json()
    assert payment["order_id"] == sample_payment_data["order_id"]
    assert payment["amount"] == float(sample_payment_data["amount"])

@pytest.mark.parametrize("method", [
    PaymentMethod.CREDIT_CARD,
    PaymentMethod.DEBIT_CARD,
    PaymentMethod.BANK_TRANSFER,
    PaymentMethod.PAYPAL
])
def test_payment_methods_workflow(sample_order_id, method):
    """Parametrized test for different payment methods workflow."""
    payment_data = {
        "order_id": sample_order_id,
        "amount": "100.00",
        "currency": "USD",
        "method": method
    }
    
    # Create payment
    create_response = client.post("/payments/", json=payment_data)
    assert create_response.status_code == 200
    payment = create_response.json()
    assert payment["method"] == method
    
    # Process payment
    process_response = client.post(f"/payments/{payment['id']}/process")
    assert process_response.status_code == 200
    processed_payment = process_response.json()
    assert processed_payment["status"] in [PaymentStatus.COMPLETED, PaymentStatus.FAILED] 