"""
Analytics models and mock data for the analytics module.
"""
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID, uuid4
import random
from pydantic import BaseModel, Field

class TimeRange(str, Enum):
    """Time range enumeration for analytics."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    YEARLY = "yearly"

class MetricType(str, Enum):
    """Metric type enumeration."""
    REVENUE = "revenue"
    ORDERS = "orders"
    USERS = "users"
    PAYMENTS = "payments"
    REFUNDS = "refunds"

@dataclass
class TimeSeriesDataPoint:
    """Time series data point model."""
    timestamp: datetime
    value: Decimal
    label: str

@dataclass
class MetricSummary:
    """Metric summary model."""
    total: Decimal
    average: Decimal
    min_value: Decimal
    max_value: Decimal
    count: int

@dataclass
class AnalyticsData:
    """Analytics data model."""
    id: UUID
    metric_type: MetricType
    time_range: TimeRange
    data_points: List[TimeSeriesDataPoint]
    summary: MetricSummary
    created_at: datetime
    updated_at: datetime

class AnalyticsService:
    """Service class for analytics operations with mock data."""
    
    def __init__(self):
        self._analytics: Dict[UUID, AnalyticsData] = {}
        self._initialize_mock_data()
    
    def _generate_mock_time_series(self, days: int, base_value: Decimal, variance: float) -> List[TimeSeriesDataPoint]:
        """Generate mock time series data."""
        from datetime import datetime, timedelta
        
        data_points = []
        current_date = datetime.now() - timedelta(days=days)
        
        for i in range(days):
            random_factor = Decimal(str(1 + random.uniform(-variance, variance)))
            value = base_value * random_factor
            data_points.append(TimeSeriesDataPoint(
                timestamp=current_date + timedelta(days=i),
                value=value,
                label=current_date.strftime("%Y-%m-%d")
            ))
        
        return data_points
    
    def generate_mock_time_series(self, days: int) -> List[TimeSeriesDataPoint]:
        """Generate mock time series data for testing."""
        if days <= 0:
            days = 1  # Ensure at least one data point
        
        return self._generate_mock_time_series(days, Decimal("100.00"), 0.2)
    
    def _calculate_summary(self, data_points: List[TimeSeriesDataPoint]) -> MetricSummary:
        """Calculate summary statistics for data points."""
        values = [point.value for point in data_points]
        return MetricSummary(
            total=sum(values),
            average=sum(values) / len(values) if values else Decimal("0"),
            min_value=min(values) if values else Decimal("0"),
            max_value=max(values) if values else Decimal("0"),
            count=len(values)
        )
    
    def _initialize_mock_data(self) -> None:
        """Initialize mock analytics data."""
        for metric_type in MetricType:
            for time_range in TimeRange:
                days = {
                    TimeRange.DAILY: 1,
                    TimeRange.WEEKLY: 7,
                    TimeRange.MONTHLY: 30,
                    TimeRange.YEARLY: 365
                }[time_range]
                
                base_value = {
                    MetricType.REVENUE: Decimal("1000.00"),
                    MetricType.ORDERS: Decimal("100.00"),
                    MetricType.USERS: Decimal("50.00"),
                    MetricType.PAYMENTS: Decimal("80.00"),
                    MetricType.REFUNDS: Decimal("10.00")
                }[metric_type]
                
                data_points = self._generate_mock_time_series(days, base_value, 0.2)
                summary = self._calculate_summary(data_points)
                
                analytics = AnalyticsData(
                    id=uuid4(),
                    metric_type=metric_type,
                    time_range=time_range,
                    data_points=data_points,
                    summary=summary,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                self._analytics[analytics.id] = analytics
    
    def get_analytics(self, metric_type: MetricType, time_range: TimeRange, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Optional[AnalyticsData]:
        """Get analytics data for a specific metric and time range."""
        for analytics in self._analytics.values():
            if analytics.metric_type == metric_type and analytics.time_range == time_range:
                return analytics
        return None
    
    def get_all_analytics(self) -> List[AnalyticsData]:
        """Get all analytics data."""
        return list(self._analytics.values())
    
    def generate_analytics(self, metric_type: MetricType, time_range: TimeRange) -> AnalyticsData:
        """Generate new analytics data."""
        days = {
            TimeRange.DAILY: 1,
            TimeRange.WEEKLY: 7,
            TimeRange.MONTHLY: 30,
            TimeRange.YEARLY: 365
        }[time_range]
        
        base_value = {
            MetricType.REVENUE: Decimal("1000.00"),
            MetricType.ORDERS: Decimal("100.00"),
            MetricType.USERS: Decimal("50.00"),
            MetricType.PAYMENTS: Decimal("80.00"),
            MetricType.REFUNDS: Decimal("10.00")
        }[metric_type]
        
        data_points = self._generate_mock_time_series(days, base_value, 0.2)
        summary = self._calculate_summary(data_points)
        
        analytics = AnalyticsData(
            id=uuid4(),
            metric_type=metric_type,
            time_range=time_range,
            data_points=data_points,
            summary=summary,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        self._analytics[analytics.id] = analytics
        return analytics
    
    def get_metric_summary(self, metric_type: MetricType, time_range: Optional[TimeRange] = None) -> Dict[TimeRange, MetricSummary]:
        """Get summary statistics for a metric across all time ranges."""
        summaries = {}
        for time_range in TimeRange:
            analytics = self.get_analytics(metric_type, time_range)
            if analytics:
                summaries[time_range] = analytics.summary
        return summaries
    
    def get_correlation(self, metric_type1: MetricType, metric_type2: MetricType) -> float:
        """Calculate correlation between two metrics."""
        # Mock implementation - in reality, this would calculate actual correlation
        return random.uniform(-1, 1)
    
    def get_trend_analysis(self, metric_type: MetricType, time_range: Optional[TimeRange] = None, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, float]:
        """Get trend analysis for a metric."""
        # Mock implementation - in reality, this would calculate actual trends
        return {
            "trend": random.uniform(-0.5, 0.5),
            "seasonality": random.uniform(0, 0.3),
            "volatility": random.uniform(0, 0.2)
        }

class AnalyticsDataResponse(BaseModel):
    total_revenue: float = Field(..., description="Total revenue")
    total_users: int = Field(..., description="Total number of users")
    revenue_by_plan: Dict[str, float] = Field(..., description="Revenue breakdown by plan")
    user_growth: Dict[str, int] = Field(..., description="User growth over time")

class AnalyticsResponse(BaseModel):
    data: AnalyticsDataResponse 