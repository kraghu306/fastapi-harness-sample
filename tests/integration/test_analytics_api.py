
"""
Integration tests for the analytics API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from app.main import app
from app.analytics.models import MetricType, TimeRange

client = TestClient(app)

def test_get_analytics():
    """Test getting analytics data for a specific metric and time range"""
    response = client.get("/analytics/metrics/revenue?time_range=daily")
    
    assert response.status_code == 200
    data = response.json()
    assert data["metric_type"] == "revenue"
    assert data["time_range"] == "daily"
    assert "data_points" in data
    assert "summary" in data
    assert isinstance(data["data_points"], list)
    assert len(data["data_points"]) > 0

def test_get_all_analytics():
    """Test getting all analytics data."""
    response = client.get("/analytics/metrics")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    for analytics in data:
        assert "metric_type" in analytics
        assert "time_range" in analytics
        assert "data_points" in analytics
        assert "summary" in analytics

def test_generate_analytics():
    """Test generating new analytics data."""
    response = client.post("/analytics/metrics/orders/generate?time_range=weekly")
    
    assert response.status_code == 200
    data = response.json()
    assert data["metric_type"] == "orders"
    assert data["time_range"] == "weekly"
    assert "data_points" in data
    assert "summary" in data
    assert isinstance(data["data_points"], list)
    assert len(data["data_points"]) == 7

def test_get_metric_summary():
    """Test getting metric summary across time ranges."""
    response = client.get("/analytics/metrics/users/summary")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) == len(TimeRange)
    for time_range, summary in data.items():
        assert time_range in [tr.value for tr in TimeRange]
        assert "total" in summary
        assert "average" in summary
        assert "min_value" in summary
        assert "max_value" in summary
        assert "count" in summary

def test_get_correlation():
    """Test calculating correlation between metrics."""
    response = client.get("/analytics/correlation?metric_type1=revenue&metric_type2=orders")
    
    assert response.status_code == 200
    correlation = response.json()
    assert isinstance(correlation, float)
    assert -1 <= correlation <= 1

def test_get_trend_analysis():
    """Test getting trend analysis."""
    response = client.get("/analytics/trends/payments")
    
    assert response.status_code == 200
    data = response.json()
    assert "trend" in data
    assert "seasonality" in data
    assert "volatility" in data
    assert -0.5 <= data["trend"] <= 0.5
    assert 0 <= data["seasonality"] <= 0.3
    assert 0 <= data["volatility"] <= 0.2

@pytest.mark.parametrize("metric_type", [mt.value for mt in MetricType])
def test_metric_types(metric_type):
    """Test analytics for all metric types."""
    response = client.get(f"/analytics/metrics/{metric_type}?time_range=daily")
    assert response.status_code == 200
    data = response.json()
    assert data["metric_type"] == metric_type

@pytest.mark.parametrize("time_range", [tr.value for tr in TimeRange])
def test_time_ranges(time_range):
    """Test analytics for all time ranges."""
    response = client.get(f"/analytics/metrics/revenue?time_range={time_range}")
    assert response.status_code == 200
    data = response.json()
    assert data["time_range"] == time_range

def test_invalid_metric_type():
    """Test handling of invalid metric type."""
    response = client.get("/analytics/metrics/invalid?time_range=daily")
    assert response.status_code == 422

def test_invalid_time_range():
    """Test handling of invalid time range."""
    response = client.get("/analytics/metrics/revenue?time_range=invalid")
    assert response.status_code == 422

def test_missing_time_range():
    """Test handling of missing time range parameter."""
    response = client.get("/analytics/metrics/revenue")
    assert response.status_code == 422

def test_invalid_correlation_parameters():
    """Test handling of invalid correlation parameters."""
    response = client.get("/analytics/correlation?metric_type1=invalid&metric_type2=orders")
    assert response.status_code == 422

def test_invalid_trend_analysis():
    """Test handling of invalid trend analysis."""
    response = client.get("/analytics/trends/invalid")
    assert response.status_code == 422 
