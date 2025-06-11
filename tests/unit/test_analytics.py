
"""
Unit tests for the analytics module.
"""
import pytest
from datetime import datetime, timedelta
from decimal import Decimal
from uuid import UUID

from app.analytics.models import (
    AnalyticsData,
    AnalyticsService,
    MetricType,
    TimeRange,
    TimeSeriesDataPoint,
    MetricSummary
)

@pytest.fixture
def analytics_service():
    """Fixture for analytics service."""
    return AnalyticsService()

@pytest.fixture
def sample_data_points():
    """Fixture for sample time series data points."""
    return [
        TimeSeriesDataPoint(
            timestamp=datetime.now() - timedelta(days=i),
            value=Decimal("100.00"),
            label=f"2024-03-{i:02d}"
        )
        for i in range(7)
    ]

def test_generate_mock_time_series(analytics_service):
    """Test generating mock time series data."""
    days = 7
    base_value = Decimal("100.00")
    variance = 0.2
    
    data_points = analytics_service._generate_mock_time_series(days, base_value, variance)
    
    assert len(data_points) == days
    for point in data_points:
        assert isinstance(point, TimeSeriesDataPoint)
        assert isinstance(point.timestamp, datetime)
        assert isinstance(point.value, Decimal)
        assert isinstance(point.label, str)
        assert base_value * Decimal(str(1 - variance)) <= point.value <= base_value * Decimal(str(1 + variance))

def test_calculate_summary(analytics_service, sample_data_points):
    """Test calculating summary statistics."""
    summary = analytics_service._calculate_summary(sample_data_points)
    
    assert isinstance(summary, MetricSummary)
    assert summary.total == Decimal("700.00")
    assert summary.average == Decimal("100.00")
    assert summary.min_value == Decimal("100.00")
    assert summary.max_value == Decimal("100.00")
    assert summary.count == 7

def test_get_analytics(analytics_service):
    """Test getting analytics data."""
    analytics = analytics_service.get_analytics(MetricType.REVENUE, TimeRange.DAILY)
    
    assert isinstance(analytics, AnalyticsData)
    assert analytics.metric_type == MetricType.REVENUE
    assert analytics.time_range == TimeRange.DAILY
    assert len(analytics.data_points) > 0
    assert isinstance(analytics.summary, MetricSummary)

def test_get_all_analytics(analytics_service):
    """Test getting all analytics data."""
    analytics_list = analytics_service.get_all_analytics()
    
    assert len(analytics_list) > 0
    for analytics in analytics_list:
        assert isinstance(analytics, AnalyticsData)
        assert isinstance(analytics.id, UUID)
        assert isinstance(analytics.metric_type, MetricType)
        assert isinstance(analytics.time_range, TimeRange)

def test_generate_analytics(analytics_service):
    """Test generating new analytics data."""
    analytics = analytics_service.generate_analytics(MetricType.ORDERS, TimeRange.WEEKLY)
    
    assert isinstance(analytics, AnalyticsData)
    assert analytics.metric_type == MetricType.ORDERS
    assert analytics.time_range == TimeRange.WEEKLY
    assert len(analytics.data_points) == 7
    assert isinstance(analytics.summary, MetricSummary)

def test_get_metric_summary(analytics_service):
    """Test getting metric summary across time ranges."""
    summaries = analytics_service.get_metric_summary(MetricType.USERS)
    
    assert len(summaries) == len(TimeRange)
    for time_range, summary in summaries.items():
        assert isinstance(time_range, TimeRange)
        assert isinstance(summary, MetricSummary)
        assert summary.count > 0

def test_get_correlation(analytics_service):
    """Test calculating correlation between metrics."""
    correlation = analytics_service.get_correlation(MetricType.REVENUE, MetricType.ORDERS)
    
    assert isinstance(correlation, float)
    assert -1 <= correlation <= 1

def test_get_trend_analysis(analytics_service):
    """Test getting trend analysis."""
    analysis = analytics_service.get_trend_analysis(MetricType.PAYMENTS)
    
    assert isinstance(analysis, dict)
    assert "trend" in analysis
    assert "seasonality" in analysis
    assert "volatility" in analysis
    assert -0.5 <= analysis["trend"] <= 0.5
    assert 0 <= analysis["seasonality"] <= 0.3
    assert 0 <= analysis["volatility"] <= 0.2

@pytest.mark.parametrize("metric_type", list(MetricType))
def test_metric_types(analytics_service, metric_type):
    """Test analytics for all metric types."""
    analytics = analytics_service.get_analytics(metric_type, TimeRange.DAILY)
    assert analytics is not None
    assert analytics.metric_type == metric_type

@pytest.mark.parametrize("time_range", list(TimeRange))
def test_time_ranges(analytics_service, time_range):
    """Test analytics for all time ranges."""
    analytics = analytics_service.get_analytics(MetricType.REVENUE, time_range)
    assert analytics is not None
    assert analytics.time_range == time_range 
