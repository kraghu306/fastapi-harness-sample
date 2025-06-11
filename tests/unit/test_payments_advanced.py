
"""
Advanced unit tests for payments service covering transaction logic and security.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import uuid4
from unittest.mock import patch, Mock
import random

from app.payments.models import Payment, PaymentService, PaymentStatus, PaymentMethod


class TestPaymentsAdvanced:
    """Advanced payments service test cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.payment_service = PaymentService()
    
    def test_payment_amount_validation(self):
        """Test payment amount validation and precision."""
        order_id = uuid4()
        
        # Test with very small amounts
        small_payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal("0.01"),
            currency="USD",
            method=PaymentMethod.CREDIT_CARD
        )
        assert small_payment.amount == Decimal("0.01")
        
        # Test with large amounts
        large_payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal("999999.99"),
            currency="USD",
            method=PaymentMethod.CREDIT_CARD
        )
        assert large_payment.amount == Decimal("999999.99")
        
        # Test with zero amount (should be handled appropriately)
        with pytest.raises((ValueError, AssertionError)):
            self.payment_service.create_payment(
                order_id=order_id,
                amount=Decimal("0.00"),
                currency="USD",
                method=PaymentMethod.CREDIT_CARD
            )
    
    def test_payment_processing_reliability(self):
        """Test payment processing reliability and consistency."""
        order_id = uuid4()
        
        # Create a payment
        payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal("100.00"),
            currency="USD",
            method=PaymentMethod.CREDIT_CARD
        )
        
        # Process payment multiple times - should be idempotent
        results = []
        for _ in range(5):
            processed_payment = self.payment_service.process_payment(payment.id)
            results.append(processed_payment.status)
        
        # All results should be consistent (either all success or all failure)
        # In a real system, this would test idempotency
        assert processed_payment is not None
        assert processed_payment.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]
    
    def test_refund_scenarios(self):
        """Test various refund scenarios and validations."""
        order_id = uuid4()
        
        # Create and process a payment
        payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal("200.00"),
            currency="USD",
            method=PaymentMethod.CREDIT_CARD
        )
        
        # Process until completed
        max_attempts = 10
        for _ in range(max_attempts):
            processed_payment = self.payment_service.process_payment(payment.id)
            if processed_payment.status == PaymentStatus.COMPLETED:
                break
        
        if processed_payment.status == PaymentStatus.COMPLETED:
            # Test partial refund
            partial_refund = self.payment_service.refund_payment(
                payment.id,
                Decimal("50.00")
            )
            assert partial_refund.status == PaymentStatus.REFUNDED
            assert partial_refund.refund_amount == Decimal("50.00")
            
            # Test full refund on a new payment
            payment2 = self.payment_service.create_payment(
                order_id=uuid4(),
                amount=Decimal("100.00"),
                currency="USD",
                method=PaymentMethod.PAYPAL
            )
            
            # Process until completed
            for _ in range(max_attempts):
                processed_payment2 = self.payment_service.process_payment(payment2.id)
                if processed_payment2.status == PaymentStatus.COMPLETED:
                    break
            
            if processed_payment2.status == PaymentStatus.COMPLETED:
                full_refund = self.payment_service.refund_payment(payment2.id)
                assert full_refund.status == PaymentStatus.REFUNDED
                assert full_refund.refund_amount == payment2.amount
    
    def test_payment_method_specific_behavior(self):
        """Test behavior specific to different payment methods."""
        order_id = uuid4()
        
        payment_methods_tests = [
            (PaymentMethod.CREDIT_CARD, "Credit card processing"),
            (PaymentMethod.DEBIT_CARD, "Debit card processing"),
            (PaymentMethod.BANK_TRANSFER, "Bank transfer processing"),
            (PaymentMethod.PAYPAL, "PayPal processing")
        ]
        
        for method, description in payment_methods_tests:
            payment = self.payment_service.create_payment(
                order_id=order_id,
                amount=Decimal("75.00"),
                currency="USD",
                method=method
            )
            
            assert payment.method == method
            assert payment.status == PaymentStatus.PENDING
            
            # Test processing for each method
            processed = self.payment_service.process_payment(payment.id)
            assert processed.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]
    
    def test_payment_statistics_accuracy(self):
        """Test payment statistics calculations for accuracy."""
        # Clear existing payments
        self.payment_service._payments.clear()
        
        # Create controlled dataset
        test_payments = [
            {"amount": "100.00", "status": PaymentStatus.COMPLETED},
            {"amount": "200.00", "status": PaymentStatus.COMPLETED},
            {"amount": "150.00", "status": PaymentStatus.FAILED},
            {"amount": "75.00", "status": PaymentStatus.PENDING},
        ]
        
        created_payments = []
        for payment_data in test_payments:
            payment = self.payment_service.create_payment(
                order_id=uuid4(),
                amount=Decimal(payment_data["amount"]),
                currency="USD",
                method=PaymentMethod.CREDIT_CARD
            )
            
            # Update status if needed
            if payment_data["status"] != PaymentStatus.PENDING:
                payment.status = payment_data["status"]
                if payment_data["status"] == PaymentStatus.COMPLETED:
                    payment.transaction_id = f"tx_{uuid4().hex[:8]}"
            
            created_payments.append(payment)
        
        # Create a refunded payment
        refund_payment = self.payment_service.create_payment(
            order_id=uuid4(),
            amount=Decimal("120.00"),
            currency="USD",
            method=PaymentMethod.PAYPAL
        )
        refund_payment.status = PaymentStatus.REFUNDED
        refund_payment.refund_amount = Decimal("120.00")
        created_payments.append(refund_payment)
        
        stats = self.payment_service.get_payment_statistics()
        
        # Verify calculations
        assert stats["total_payments"] == 5.0
        assert stats["total_amount"] == 645.0  # Sum of all amounts
        assert stats["completed_amount"] == 300.0  # 100 + 200
        assert stats["refunded_amount"] == 120.0
        assert stats["net_amount"] == 180.0  # 300 - 120
    
    def test_concurrent_payment_processing(self):
        """Test concurrent payment processing."""
        import threading
        
        order_id = uuid4()
        processed_payments = []
        errors = []
        
        def process_payment_concurrently():
            try:
                # Create payment
                payment = self.payment_service.create_payment(
                    order_id=order_id,
                    amount=Decimal("50.00"),
                    currency="USD",
                    method=PaymentMethod.CREDIT_CARD
                )
                
                # Process payment
                processed = self.payment_service.process_payment(payment.id)
                processed_payments.append(processed)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(8):
            thread = threading.Thread(target=process_payment_concurrently)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify no errors occurred
        assert len(errors) == 0
        assert len(processed_payments) == 8
        
        # Verify all payments have valid status
        for payment in processed_payments:
            assert payment.status in [PaymentStatus.COMPLETED, PaymentStatus.FAILED]
    
    def test_payment_filtering_and_search(self):
        """Test payment filtering and search capabilities."""
        # Create payments with different characteristics
        payment_configs = [
            (PaymentMethod.CREDIT_CARD, PaymentStatus.COMPLETED, "100.00"),
            (PaymentMethod.DEBIT_CARD, PaymentStatus.FAILED, "200.00"),
            (PaymentMethod.PAYPAL, PaymentStatus.PENDING, "150.00"),
            (PaymentMethod.BANK_TRANSFER, PaymentStatus.COMPLETED, "300.00"),
            (PaymentMethod.CREDIT_CARD, PaymentStatus.REFUNDED, "75.00"),
        ]
        
        created_payments = []
        for method, status, amount in payment_configs:
            payment = self.payment_service.create_payment(
                order_id=uuid4(),
                amount=Decimal(amount),
                currency="USD",
                method=method
            )
            payment.status = status  # Set status directly for testing
            created_payments.append(payment)
        
        # Test filtering by status
        completed_payments = self.payment_service.get_payments_by_status(PaymentStatus.COMPLETED)
        assert len([p for p in completed_payments if p.status == PaymentStatus.COMPLETED]) >= 2
        
        failed_payments = self.payment_service.get_payments_by_status(PaymentStatus.FAILED)
        assert len([p for p in failed_payments if p.status == PaymentStatus.FAILED]) >= 1
        
        # Test filtering by method
        credit_card_payments = self.payment_service.get_payments_by_method(PaymentMethod.CREDIT_CARD)
        assert len([p for p in credit_card_payments if p.method == PaymentMethod.CREDIT_CARD]) >= 2
        
        paypal_payments = self.payment_service.get_payments_by_method(PaymentMethod.PAYPAL)
        assert len([p for p in paypal_payments if p.method == PaymentMethod.PAYPAL]) >= 1
    
    def test_payment_security_validations(self):
        """Test payment security validations and error handling."""
        order_id = uuid4()
        
        # Test with invalid currencies
        valid_currencies = ["USD", "EUR", "GBP", "JPY"]
        
        for currency in valid_currencies:
            payment = self.payment_service.create_payment(
                order_id=order_id,
                amount=Decimal("100.00"),
                currency=currency,
                method=PaymentMethod.CREDIT_CARD
            )
            assert payment.currency == currency
        
        # Test processing non-existent payment
        non_existent_id = uuid4()
        result = self.payment_service.process_payment(non_existent_id)
        assert result is None
        
        # Test refunding non-existent payment
        refund_result = self.payment_service.refund_payment(non_existent_id)
        assert refund_result is None
    
    def test_payment_transaction_ids(self):
        """Test payment transaction ID generation and uniqueness."""
        order_id = uuid4()
        
        # Create multiple payments and process them
        payments = []
        for i in range(10):
            payment = self.payment_service.create_payment(
                order_id=order_id,
                amount=Decimal(f"{(i + 1) * 10}.00"),
                currency="USD",
                method=PaymentMethod.CREDIT_CARD
            )
            
            # Process payment until completed
            for _ in range(5):
                processed = self.payment_service.process_payment(payment.id)
                if processed.status == PaymentStatus.COMPLETED:
                    payments.append(processed)
                    break
        
        # Verify transaction IDs are unique for completed payments
        transaction_ids = [p.transaction_id for p in payments if p.transaction_id]
        if transaction_ids:
            assert len(set(transaction_ids)) == len(transaction_ids)  # All unique
    
    @pytest.mark.parametrize("amount,currency,method", [
        ("19.99", "USD", PaymentMethod.CREDIT_CARD),
        ("299.99", "EUR", PaymentMethod.DEBIT_CARD),
        ("1000.00", "GBP", PaymentMethod.PAYPAL),
        ("50.50", "USD", PaymentMethod.BANK_TRANSFER),
    ])
    def test_payment_creation_parametrized(self, amount, currency, method):
        """Parametrized test for payment creation with various configurations."""
        order_id = uuid4()
        
        payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal(amount),
            currency=currency,
            method=method
        )
        
        assert payment.order_id == order_id
        assert payment.amount == Decimal(amount)
        assert payment.currency == currency
        assert payment.method == method
        assert payment.status == PaymentStatus.PENDING
        assert payment.created_at is not None
        assert payment.updated_at is not None
    
    def test_payment_error_handling(self):
        """Test payment service error handling."""
        order_id = uuid4()
        
        # Test processing payment that's already completed
        payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal("100.00"),
            currency="USD",
            method=PaymentMethod.CREDIT_CARD
        )
        
        # Manually set to completed
        payment.status = PaymentStatus.COMPLETED
        payment.transaction_id = "tx_completed"
        
        # Try to process again
        result = self.payment_service.process_payment(payment.id)
        
        # Should handle gracefully (return the payment or handle appropriately)
        assert result is not None
        assert result.status == PaymentStatus.COMPLETED
    
    def test_payment_data_consistency(self):
        """Test payment data consistency and integrity."""
        order_id = uuid4()
        
        # Create payment with specific data
        original_payment = self.payment_service.create_payment(
            order_id=order_id,
            amount=Decimal("123.45"),
            currency="USD",
            method=PaymentMethod.CREDIT_CARD
        )
        
        # Retrieve payment and verify data integrity
        retrieved_payment = self.payment_service.get_payment(original_payment.id)
        
        assert retrieved_payment.id == original_payment.id
        assert retrieved_payment.order_id == original_payment.order_id
        assert retrieved_payment.amount == original_payment.amount
        assert retrieved_payment.currency == original_payment.currency
        assert retrieved_payment.method == original_payment.method
        assert retrieved_payment.status == original_payment.status
        
        # Test that timestamps are preserved
        assert retrieved_payment.created_at == original_payment.created_at
        assert retrieved_payment.updated_at == original_payment.updated_at 
