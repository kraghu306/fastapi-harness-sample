
import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from app.main import app
from app.analytics.models import AnalyticsResponse, AnalyticsData

client = TestClient(app)

def test_get_analytics():
    response = client.get("/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], dict)
    assert "total_revenue" in data["data"]
    assert "total_users" in data["data"]
    assert "revenue_by_plan" in data["data"]
    assert "user_growth" in data["data"]

def test_get_analytics_with_date_range():
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    response = client.get(
        f"/analytics?start_date={start_date.isoformat()}&end_date={end_date.isoformat()}"
    )
    assert response.status_code == 200
    data = response.json()
    assert "data" in data
    assert isinstance(data["data"], dict)

def test_get_analytics_with_invalid_date_range():
    response = client.get("/analytics?start_date=invalid")
    assert response.status_code == 422

def test_get_analytics_with_future_date():
    future_date = datetime.now() + timedelta(days=1)
    response = client.get(f"/analytics?end_date={future_date.isoformat()}")
    assert response.status_code == 422 
