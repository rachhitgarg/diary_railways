from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
import os
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Student Diary",
    description="AI-powered diary for students",
    version="1.0.0"
)

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

@app.get("/")
async def root():
    """Serve the main web interface"""
    try:
        with open("static/index.html", "r") as f:
            content = f.read()
        return HTMLResponse(content=content)
    except Exception as e:
        logger.error(f"Error loading index.html: {e}")
        return HTMLResponse("""
        <html>
            <head><title>AI Student Diary</title></head>
            <body>
                <h1>🎓 AI Student Diary</h1>
                <p>Application is starting up...</p>
                <p>Static files loading issue - but the app is working!</p>
            </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    logger.info("Health check requested")
    return {
        "status": "healthy",
        "service": "AI Student Diary",
        "version": "1.0.0",
        "environment": os.environ.get("ENVIRONMENT", "development")
    }

@app.post("/api/v1/diary/entries")
async def create_entry(entry_data: dict):
    """Simplified diary entry endpoint"""
    logger.info(f"Diary entry received: {entry_data.get('content', 'No content')[:50]}...")

    # Simulate processing
    return {
        "status": "success",
        "message": "Entry received! AI processing will be implemented next.",
        "entry_id": "temp_123",
        "analysis": {
            "sentiment": "neutral",
            "mood_detected": entry_data.get("mood_score", 0.5),
            "message": "Basic processing complete - full AI analysis coming soon!"
        }
    }

@app.get("/api/v1/diary/reflection/daily")
async def get_daily_reflection():
    """Simple daily reflection"""
    return {
        "reflection": "🌅 Good morning! Your AI diary is up and running. Start writing to see amazing insights soon!",
        "generated_at": "2025-08-29T00:00:00Z"
    }

@app.get("/api/v1/analytics/overview")
async def get_analytics():
    """Basic analytics"""
    return {
        "total_entries": 0,
        "mood_average": None,
        "streak_days": 0,
        "message": "Start writing entries to see your analytics!"
    }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "message": str(exc)}
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
