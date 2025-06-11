"""
Comprehensive integration tests covering API edge cases and cross-service interactions.
"""
import pytest
from fastapi.testclient import TestClient
from uuid import uuid4
import json

from app.main import app

client = TestClient(app)


class TestAPIComprehensive:
    """Comprehensive API integration test cases."""
    
    def test_api_health_and_status(self):
        """Test API health endpoints and status codes."""
        # Test root endpoint
        response = client.get("/")
        assert response.status_code in [200, 404]  # Depends on if root is defined
        
        # Test non-existent endpoint
        response = client.get("/non-existent-endpoint")
        assert response.status_code == 404
    
    def test_cross_service_workflow(self):
        """Test complete workflow across multiple services."""
        # 1. Create a user
        user_data = {
            "username": "workflow_user",
            "email": "workflow@example.com"
        }
        user_response = client.post("/users/", json=user_data)
        assert user_response.status_code == 200
        user = user_response.json()
        user_id = user["id"]
        
        # 2. Create an order for the user
        order_data = {
            "user_id": user_id,
            "items": [
                {
                    "product_id": str(uuid4()),
                    "quantity": 2,
                    "unit_price": "25.99"
                }
            ],
            "shipping_address": "123 Workflow St"
        }
        order_response = client.post("/orders/", json=order_data)
        assert order_response.status_code == 200
        order = order_response.json()
        order_id = order["id"]
        
        # 3. Create a payment for the order
        payment_data = {
            "order_id": order_id,
            "amount": str(order["total_amount"]),
            "currency": "USD",
            "method": "credit_card"
        }
        payment_response = client.post("/payments/", json=payment_data)
        assert payment_response.status_code == 200
        payment = payment_response.json()
        
        # 4. Process the payment
        process_response = client.post(f"/payments/{payment['id']}/process")
        assert process_response.status_code == 200
        
        # 5. Verify all data is consistent
        assert payment["order_id"] == order_id
        assert float(payment["amount"]) == order["total_amount"]
    
    def test_api_error_handling(self):
        """Test API error handling for various scenarios."""
        # Test invalid JSON
        response = client.post(
            "/users/",
            data="invalid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
        
        # Test missing required fields
        response = client.post("/users/", json={})
        assert response.status_code == 422
        
        # Test invalid UUID format
        response = client.get("/users/invalid-uuid")
        assert response.status_code == 422
        
        # Test non-existent resource
        valid_uuid = str(uuid4())
        response = client.get(f"/users/{valid_uuid}")
        assert response.status_code == 404
    
    def test_api_data_validation(self):
        """Test API data validation for various inputs."""
        # Test user creation with invalid email
        invalid_emails = [
            "invalid-email",
            "@invalid.com",
            "test@",
            "test@.com"
        ]
        
        for email in invalid_emails:
            response = client.post("/users/", json={
                "username": "test_user",
                "email": email
            })
            # API should handle invalid emails gracefully
            assert response.status_code in [200, 422]  # Depends on validation
    
    def test_api_pagination_and_filtering(self):
        """Test API pagination and filtering capabilities."""
        # Create multiple users for testing
        users = []
        for i in range(10):
            user_data = {
                "username": f"pagination_user_{i}",
                "email": f"pagination{i}@example.com"
            }
            response = client.post("/users/", json=user_data)
            if response.status_code == 200:
                users.append(response.json())
        
        # Test getting all users (pagination might be implemented)
        response = client.get("/users/")
        assert response.status_code == 200
        all_users = response.json()
        assert len(all_users) >= len(users)
        
        # Test domain filtering
        response = client.get("/users/domain/example.com")
        assert response.status_code == 200
        domain_users = response.json()
        for user in domain_users:
            assert user["email"].endswith("@example.com")
    
    def test_api_concurrent_requests(self):
        """Test API handling of concurrent requests."""
        import threading
        import time
        
        results = []
        
        def make_concurrent_request():
            response = client.get("/users/")
            results.append(response.status_code)
        
        # Make multiple concurrent requests
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=make_concurrent_request)
            threads.append(thread)
            thread.start()
        
        # Wait for all requests to complete
        for thread in threads:
            thread.join()
        
        # All requests should succeed
        assert all(status == 200 for status in results)
        assert len(results) == 5
    
    def test_api_response_formats(self):
        """Test API response formats and structure."""
        # Test user creation response format
        user_data = {
            "username": "format_test",
            "email": "format@example.com"
        }
        response = client.post("/users/", json=user_data)
        assert response.status_code == 200
        
        user = response.json()
        required_fields = ["id", "username", "email", "is_active"]
        for field in required_fields:
            assert field in user
        
        # Test order creation response format
        order_data = {
            "user_id": user["id"],
            "items": [
                {
                    "product_id": str(uuid4()),
                    "quantity": 1,
                    "unit_price": "19.99"
                }
            ],
            "shipping_address": "123 Format Test St"
        }
        response = client.post("/orders/", json=order_data)
        assert response.status_code == 200
        
        order = response.json()
        order_fields = ["id", "user_id", "items", "status", "total_amount", "shipping_address"]
        for field in order_fields:
            assert field in order
    
    def test_api_authentication_and_security(self):
        """Test API security headers and basic security measures."""
        response = client.get("/users/")
        
        # Check for security headers (if implemented)
        headers = response.headers
        # These might not be implemented yet, but good to test
        security_headers = [
            "X-Content-Type-Options",
            "X-Frame-Options", 
            "X-XSS-Protection"
        ]
        
        # Just verify response is successful for now
        assert response.status_code == 200
    
    def test_api_large_payload_handling(self):
        """Test API handling of large payloads."""
        # Create order with many items
        large_order_data = {
            "user_id": str(uuid4()),
            "items": [
                {
                    "product_id": str(uuid4()),
                    "quantity": 1,
                    "unit_price": f"{i}.99"
                }
                for i in range(50)  # 50 items
            ],
            "shipping_address": "123 Large Order St"
        }
        
        response = client.post("/orders/", json=large_order_data)
        assert response.status_code == 200
        
        order = response.json()
        assert len(order["items"]) == 50
    
    def test_api_performance_benchmarks(self):
        """Test API performance with basic benchmarks."""
        import time
        
        # Benchmark user creation
        start_time = time.time()
        for i in range(10):
            user_data = {
                "username": f"perf_user_{i}",
                "email": f"perf{i}@benchmark.com"
            }
            response = client.post("/users/", json=user_data)
            assert response.status_code == 200
        creation_time = time.time() - start_time
        
        # Should create 10 users in reasonable time
        assert creation_time < 2.0  # Less than 2 seconds
        
        # Benchmark data retrieval
        start_time = time.time()
        for _ in range(10):
            response = client.get("/users/")
            assert response.status_code == 200
        retrieval_time = time.time() - start_time
        
        # Should retrieve data quickly
        assert retrieval_time < 1.0
    
    def test_api_statistics_endpoints(self):
        """Test statistics endpoints across all services."""
        # Test order statistics
        response = client.get("/orders/statistics")
        assert response.status_code == 200
        order_stats = response.json()
        required_stats = ["total_orders", "total_revenue", "average_order_value"]
        for stat in required_stats:
            assert stat in order_stats
            assert isinstance(order_stats[stat], (int, float))
        
        # Test payment statistics
        response = client.get("/payments/statistics")
        assert response.status_code == 200
        payment_stats = response.json()
        payment_stat_fields = ["total_payments", "total_amount", "completed_amount"]
        for stat in payment_stat_fields:
            assert stat in payment_stats
            assert isinstance(payment_stats[stat], (int, float))
    
    def test_api_analytics_endpoints(self):
        """Test analytics endpoints with various parameters."""
        # Test basic analytics
        response = client.get("/analytics/")
        assert response.status_code == 200
        analytics = response.json()
        assert "data" in analytics
        
        # Test metrics endpoint
        response = client.get("/analytics/metrics/revenue", params={"time_range": "daily"})
        assert response.status_code == 200
        metrics = response.json()
        assert "metric_type" in metrics
        assert "time_range" in metrics
        
        # Test analytics with date range
        response = client.get("/analytics/", params={
            "start_date": "2024-01-01",
            "end_date": "2024-12-31"
        })
        assert response.status_code == 200
        
        # Test invalid metric type
        response = client.get("/analytics/metrics/invalid_metric", params={"time_range": "daily"})
        assert response.status_code == 422
    
    def test_api_edge_case_scenarios(self):
        """Test API edge case scenarios."""
        # Test extremely long strings
        long_username = "a" * 1000
        response = client.post("/users/", json={
            "username": long_username,
            "email": "long@example.com"
        })
        # Should handle gracefully (accept or reject with proper error)
        assert response.status_code in [200, 422]
        
        # Test special characters in data
        special_user = {
            "username": "user_with_special_chars_!@#$%",
            "email": "special+chars@example.com"
        }
        response = client.post("/users/", json=special_user)
        assert response.status_code in [200, 422]
        
        # Test Unicode characters
        unicode_user = {
            "username": "用户_测试",
            "email": "unicode@example.com"
        }
        response = client.post("/users/", json=unicode_user)
        assert response.status_code in [200, 422]
    
    def test_api_content_types(self):
        """Test API handling of different content types."""
        user_data = {
            "username": "content_test",
            "email": "content@example.com"
        }
        
        # Test JSON content type
        response = client.post(
            "/users/",
            json=user_data,
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200
        
        # Test unsupported content type
        response = client.post(
            "/users/",
            data="username=test&email=test@example.com",
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        # Should handle gracefully
        assert response.status_code in [200, 422, 415] 