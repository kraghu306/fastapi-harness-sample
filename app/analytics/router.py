
"""
Analytics router for the analytics module.
"""
from datetime import datetime
from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Query
from .models import (
    AnalyticsDataResponse, AnalyticsResponse, MetricType, TimeRange,
    AnalyticsData, AnalyticsService
)

router = APIRouter(prefix="/analytics", tags=["analytics"])
analytics_service = AnalyticsService()

@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    start_date: Optional[datetime] = Query(None, description="Start date for analytics"),
    end_date: Optional[datetime] = Query(None, description="End date for analytics")
) -> AnalyticsResponse:
    """Get analytics data."""
    # Validate dates
    if start_date and end_date and start_date > end_date:
        raise HTTPException(status_code=422, detail="Start date must be before end date")

    if end_date and end_date > datetime.now():
        raise HTTPException(status_code=422, detail="End date cannot be in the future")

    # Mock data for now - in a real implementation, this would come from a service
    data = AnalyticsDataResponse(
        total_revenue=10000.0,
        total_users=1000,
        revenue_by_plan={
            "basic": 3000.0,
            "premium": 5000.0,
            "enterprise": 2000.0
        },
        user_growth={
            "2024-01": 100,
            "2024-02": 150,
            "2024-03": 200
        }
    )
    return AnalyticsResponse(data=data)

@router.get("/metrics", response_model=List[AnalyticsData])
async def get_all_analytics() -> List[AnalyticsData]:
    """Get all analytics data."""
    return analytics_service.get_all_analytics()

@router.get("/metrics/{metric_type}", response_model=AnalyticsData)
async def get_analytics_by_metric(
    metric_type: MetricType,
    time_range: TimeRange = Query(..., description="Time range for analytics")
) -> AnalyticsData:
    """Get analytics data for a specific metric and time range."""
    analytics = analytics_service.get_analytics(metric_type, time_range)
    if not analytics:
        raise HTTPException(status_code=404, detail="Analytics data not found")
    return analytics

@router.post("/metrics/{metric_type}/generate", response_model=AnalyticsData)
async def generate_analytics(
    metric_type: MetricType,
    time_range: TimeRange = Query(..., description="Time range for analytics")
) -> AnalyticsData:
    """Generate new analytics data."""
    return analytics_service.generate_analytics(metric_type, time_range)

@router.get("/metrics/{metric_type}/summary", response_model=Dict[TimeRange, Dict])
async def get_metric_summary(metric_type: MetricType) -> Dict[TimeRange, Dict]:
    """Get summary statistics for a metric across all time ranges."""
    summary = analytics_service.get_metric_summary(metric_type)
    # Convert MetricSummary objects to dictionaries
    return {
        time_range: {
            "total": float(summary[time_range].total),
            "average": float(summary[time_range].average),
            "min_value": float(summary[time_range].min_value),
            "max_value": float(summary[time_range].max_value),
            "count": summary[time_range].count
        }
        for time_range in summary
    }

@router.get("/correlation", response_model=float)
async def get_correlation(
    metric_type1: MetricType = Query(..., description="First metric type"),
    metric_type2: MetricType = Query(..., description="Second metric type")
) -> float:
    """Calculate correlation between two metrics."""
    return analytics_service.get_correlation(metric_type1, metric_type2)

@router.get("/trends/{metric_type}", response_model=Dict[str, float])
async def get_trend_analysis(metric_type: MetricType) -> Dict[str, float]:
    """Get trend analysis for a metric."""
    return analytics_service.get_trend_analysis(metric_type) 
