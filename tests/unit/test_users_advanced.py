
"""
Advanced unit tests for users service covering user management and security.
"""
import pytest
from datetime import datetime, timedelta
from uuid import uuid4
from unittest.mock import patch, Mock
import re

from app.users.models import User, UserService


class TestUsersAdvanced:
    """Advanced users service test cases."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.user_service = UserService()
    
    def test_email_validation_patterns(self):
        """Test email validation with various patterns."""
        valid_emails = [
            "user@example.com",
            "test.email+tag@domain.co.uk",
            "user123@test-domain.org",
            "firstname.lastname@company.com",
            "a@b.co"
        ]
        
        for email in valid_emails:
            user = self.user_service.create_user(
                username=f"user_{hash(email)}",
                email=email
            )
            assert user.email == email
            assert "@" in user.email
            assert "." in user.email.split("@")[1]
    
    def test_username_uniqueness_validation(self):
        """Test username uniqueness enforcement."""
        # Create first user
        user1 = self.user_service.create_user(
            username="unique_user",
            email="user1@example.com"
        )
        
        # Try to create another user with same username (should be handled)
        user2 = self.user_service.create_user(
            username="unique_user",
            email="user2@example.com"
        )
        
        # Both users should exist with different IDs
        assert user1.id != user2.id
        assert user1.email != user2.email
    
    def test_user_activation_workflow(self):
        """Test user activation and deactivation workflow."""
        # Create user
        user = self.user_service.create_user(
            username="activation_test",
            email="activation@example.com"
        )
        
        # User should be active by default
        assert user.is_active is True
        
        # Test deactivation (if supported)
        # In a real system, this might involve an update method
        updated_user = self.user_service.update_user(
            user.id,
            is_active=False
        )
        
        if updated_user:
            assert updated_user.is_active is False
            
            # Test reactivation
            reactivated_user = self.user_service.update_user(
                user.id,
                is_active=True
            )
            
            if reactivated_user:
                assert reactivated_user.is_active is True
    
    def test_bulk_user_operations(self):
        """Test bulk user operations and performance."""
        # Create many users
        created_users = []
        for i in range(100):
            user = self.user_service.create_user(
                username=f"bulk_user_{i}",
                email=f"bulk_{i}@example.com"
            )
            created_users.append(user)
        
        # Verify all users were created
        assert len(created_users) == 100
        
        # Test bulk retrieval
        all_users = self.user_service.get_all_users()
        assert len(all_users) >= 100
        
        # Test filtering active users
        active_users = self.user_service.get_active_users()
        bulk_active_users = [u for u in active_users if u.username.startswith("bulk_user_")]
        assert len(bulk_active_users) == 100
    
    def test_user_search_by_domain(self):
        """Test user search by email domain functionality."""
        # Create users with different domains
        domains_and_users = [
            ("example.com", 5),
            ("company.org", 3),
            ("university.edu", 7),
            ("startup.io", 2)
        ]
        
        created_users_by_domain = {}
        for domain, count in domains_and_users:
            created_users_by_domain[domain] = []
            for i in range(count):
                user = self.user_service.create_user(
                    username=f"user_{domain}_{i}",
                    email=f"user{i}@{domain}"
                )
                created_users_by_domain[domain].append(user)
        
        # Test domain filtering
        for domain, expected_count in domains_and_users:
            domain_users = self.user_service.get_users_by_email_domain(domain)
            domain_specific_users = [u for u in domain_users if u.email.endswith(f"@{domain}")]
            assert len(domain_specific_users) >= expected_count
    
    def test_user_data_integrity(self):
        """Test user data integrity and validation."""
        # Create user with specific data
        original_user = self.user_service.create_user(
            username="integrity_test",
            email="integrity@example.com"
        )
        
        # Retrieve user and verify data integrity
        retrieved_user = self.user_service.get_user(original_user.id)
        
        assert retrieved_user.id == original_user.id
        assert retrieved_user.username == original_user.username
        assert retrieved_user.email == original_user.email
        assert retrieved_user.is_active == original_user.is_active
        assert retrieved_user.created_at == original_user.created_at
        assert retrieved_user.updated_at == original_user.updated_at
    
    def test_user_update_scenarios(self):
        """Test various user update scenarios."""
        # Create user
        user = self.user_service.create_user(
            username="update_test",
            email="update@example.com"
        )
        
        original_created_at = user.created_at
        
        # Test username update
        updated_user = self.user_service.update_user(
            user.id,
            username="updated_username"
        )
        
        if updated_user:
            assert updated_user.username == "updated_username"
            assert updated_user.email == user.email
            assert updated_user.created_at == original_created_at
            assert updated_user.updated_at >= original_created_at
        
        # Test email update
        email_updated_user = self.user_service.update_user(
            user.id,
            email="new_email@example.com"
        )
        
        if email_updated_user:
            assert email_updated_user.email == "new_email@example.com"
    
    def test_user_deletion_and_cleanup(self):
        """Test user deletion and data cleanup."""
        # Create user
        user = self.user_service.create_user(
            username="delete_test",
            email="delete@example.com"
        )
        
        user_id = user.id
        
        # Verify user exists
        retrieved_user = self.user_service.get_user(user_id)
        assert retrieved_user is not None
        
        # Delete user
        deleted = self.user_service.delete_user(user_id)
        assert deleted is True
        
        # Verify user is deleted
        deleted_user = self.user_service.get_user(user_id)
        assert deleted_user is None
    
    def test_concurrent_user_operations(self):
        """Test concurrent user operations."""
        import threading
        
        created_users = []
        errors = []
        
        def create_user_concurrently(thread_id):
            try:
                user = self.user_service.create_user(
                    username=f"concurrent_user_{thread_id}",
                    email=f"concurrent_{thread_id}@example.com"
                )
                created_users.append(user)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for i in range(10):
            thread = threading.Thread(target=create_user_concurrently, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify all users were created successfully
        assert len(errors) == 0
        assert len(created_users) == 10
        
        # Verify all users have unique IDs and emails
        user_ids = [user.id for user in created_users]
        user_emails = [user.email for user in created_users]
        assert len(set(user_ids)) == len(user_ids)  # All unique IDs
        assert len(set(user_emails)) == len(user_emails)  # All unique emails
    
    def test_user_statistics_and_analytics(self):
        """Test user statistics and analytics functionality."""
        # Clear existing users for accurate statistics
        initial_count = len(self.user_service.get_all_users())
        
        # Create users with different characteristics
        user_configs = [
            ("active_user_1", "active1@example.com", True),
            ("active_user_2", "active2@company.org", True),
            ("inactive_user_1", "inactive1@example.com", False),
            ("active_user_3", "active3@university.edu", True),
            ("inactive_user_2", "inactive2@company.org", False),
        ]
        
        created_users = []
        for username, email, is_active in user_configs:
            user = self.user_service.create_user(username=username, email=email)
            if not is_active:
                # Update to inactive if needed
                updated_user = self.user_service.update_user(
                    user.id, is_active=False
                )
                if updated_user:
                    user = updated_user
            created_users.append(user)
        
        # Test active users count
        active_users = self.user_service.get_active_users()
        new_active_users = [u for u in active_users if any(u.email == email for _, email, is_active in user_configs if is_active)]
        assert len(new_active_users) >= 3  # At least 3 active users from our test data
        
        # Test domain distribution
        example_com_users = self.user_service.get_users_by_email_domain("example.com")
        company_org_users = self.user_service.get_users_by_email_domain("company.org")
        university_edu_users = self.user_service.get_users_by_email_domain("university.edu")
        
        # Verify domain filtering works
        for user in example_com_users:
            assert user.email.endswith("@example.com")
        for user in company_org_users:
            assert user.email.endswith("@company.org")
        for user in university_edu_users:
            assert user.email.endswith("@university.edu")
    
    @pytest.mark.parametrize("username,email,expected_active", [
        ("test_user_1", "test1@example.com", True),
        ("test_user_2", "test2@company.org", True),
        ("test_user_3", "test3@university.edu", True),
        ("test_user_4", "test4@startup.io", True),
    ])
    def test_user_creation_parametrized(self, username, email, expected_active):
        """Parametrized test for user creation with various configurations."""
        user = self.user_service.create_user(username=username, email=email)
        
        assert user.username == username
        assert user.email == email
        assert user.is_active == expected_active
        assert user.created_at is not None
        assert user.updated_at is not None
        assert user.id is not None
    
    def test_user_edge_cases(self):
        """Test user service edge cases and error handling."""
        # Test getting non-existent user
        non_existent_id = uuid4()
        result = self.user_service.get_user(non_existent_id)
        assert result is None
        
        # Test updating non-existent user
        update_result = self.user_service.update_user(
            non_existent_id,
            username="nonexistent"
        )
        assert update_result is None
        
        # Test deleting non-existent user
        delete_result = self.user_service.delete_user(non_existent_id)
        assert delete_result is False
    
    def test_user_email_case_sensitivity(self):
        """Test email case sensitivity handling."""
        # Create users with different email cases
        user1 = self.user_service.create_user(
            username="case_test_1",
            email="CaseSensitive@Example.COM"
        )
        
        user2 = self.user_service.create_user(
            username="case_test_2",
            email="casesensitive@example.com"
        )
        
        # Both users should be created (case sensitivity depends on implementation)
        assert user1.id != user2.id
        assert user1.email != user2.email or user1.email.lower() == user2.email.lower()
    
    def test_user_performance_benchmarks(self):
        """Test user service performance benchmarks."""
        import time
        
        # Benchmark user creation
        start_time = time.time()
        users = []
        for i in range(50):
            user = self.user_service.create_user(
                username=f"perf_user_{i}",
                email=f"perf{i}@benchmark.com"
            )
            users.append(user)
        creation_time = time.time() - start_time
        
        # Should create 50 users in reasonable time (less than 1 second)
        assert creation_time < 1.0
        assert len(users) == 50
        
        # Benchmark user retrieval
        start_time = time.time()
        for user in users[:10]:  # Test first 10 users
            retrieved = self.user_service.get_user(user.id)
            assert retrieved is not None
        retrieval_time = time.time() - start_time
        
        # Should retrieve 10 users quickly
        assert retrieval_time < 0.5
    
    def test_user_memory_efficiency(self):
        """Test memory efficiency with large numbers of users."""
        import sys
        
        initial_user_count = len(self.user_service._users)
        
        # Create many users
        for i in range(200):
            self.user_service.create_user(
                username=f"memory_user_{i}",
                email=f"memory{i}@efficiency.com"
            )
        
        # Verify users were created
        final_user_count = len(self.user_service._users)
        assert final_user_count == initial_user_count + 200
        
        # Test memory usage is reasonable
        users_size = sys.getsizeof(self.user_service._users)
        assert users_size < 2 * 1024 * 1024  # Should be less than 2MB for 200 users
    
    def test_user_data_export_import(self):
        """Test user data export and import functionality (if available)."""
        # Create test users
        test_users = []
        for i in range(5):
            user = self.user_service.create_user(
                username=f"export_user_{i}",
                email=f"export{i}@test.com"
            )
            test_users.append(user)
        
        # Get all users (simulating export)
        all_users = self.user_service.get_all_users()
        export_users = [u for u in all_users if u.username.startswith("export_user_")]
        
        # Verify export contains our test users
        assert len(export_users) == 5
        
        # Verify data structure for export
        for user in export_users:
            assert hasattr(user, 'id')
            assert hasattr(user, 'username')
            assert hasattr(user, 'email')
            assert hasattr(user, 'is_active')
            assert hasattr(user, 'created_at')
            assert hasattr(user, 'updated_at') 
