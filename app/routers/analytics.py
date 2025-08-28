from fastapi import APIRouter
from datetime import datetime, timedelta

router = APIRouter()

@router.get("/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    return {
        "total_entries": 0,
        "mood_average": 0.5,
        "streak_days": 0,
        "insights_count": 0,
        "last_entry_date": None,
        "status": "analytics_ready"
    }

@router.get("/mood-trends")
async def get_mood_trends():
    """Get mood trends over time"""
    return {
        "trends": [],
        "period": "7_days",
        "average_mood": 0.5,
        "status": "trends_ready"
    }

@router.get("/insights")
async def get_ai_insights():
    """Get AI-generated insights"""
    return {
        "insights": [
            {
                "type": "pattern",
                "title": "Study Pattern Recognition",
                "description": "AI insights will appear here after collecting diary entries",
                "confidence": 0.0
            }
        ],
        "generated_at": datetime.utcnow(),
        "status": "insights_ready"
    }

@router.get("/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    return {
        "mood_trends": [],
        "recent_entries": [],
        "upcoming_events": [],
        "stress_levels": {
            "current": "low",
            "trend": "stable"
        },
        "recommendations": [
            "Keep up the great work with your diary entries!",
            "Consider adding more details about your daily activities."
        ],
        "achievements": [
            {
                "type": "streak",
                "title": "Getting Started!",
                "description": "Welcome to your AI diary journey"
            }
        ]
    }
