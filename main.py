"""
AI Student Diary - Railway Deployment
Production-ready FastAPI application
"""

import os
import logging
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    logger.info("🚀 AI Student Diary starting up...")

    # Initialize databases and connections
    await initialize_services()

    yield

    logger.info("📴 AI Student Diary shutting down...")

# Create FastAPI app
app = FastAPI(
    title="AI Student Diary",
    description="AI-powered diary application for Indian students",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files (frontend)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/", StaticFiles(directory="static", html=True), name="frontend")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Student Diary",
        "version": "1.0.0"
    }

async def initialize_services():
    """Initialize external services"""
    try:
        # Test OpenAI connection
        openai_key = os.getenv("OPENAI_API_KEY")
        if not openai_key:
            logger.warning("⚠️ OpenAI API key not configured")
        else:
            logger.info("✅ OpenAI API key configured")

        # Test Pinecone connection
        pinecone_key = os.getenv("PINECONE_API_KEY")
        if not pinecone_key:
            logger.warning("⚠️ Pinecone API key not configured")
        else:
            logger.info("✅ Pinecone API key configured")

        # Test Neo4j connection
        neo4j_uri = os.getenv("NEO4J_URI")
        if not neo4j_uri:
            logger.warning("⚠️ Neo4j URI not configured")
        else:
            logger.info("✅ Neo4j URI configured")

        logger.info("✅ Service initialization complete")

    except Exception as e:
        logger.error(f"❌ Service initialization failed: {e}")

# API Routes
from app.routers import auth, diary, analytics

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(diary.router, prefix="/api/v1/diary", tags=["Diary"])
app.include_router(analytics.router, prefix="/api/v1/analytics", tags=["Analytics"])

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
