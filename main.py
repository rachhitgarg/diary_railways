from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from typing import Optional, List
import os
import logging
import asyncio
import json
from datetime import datetime, timedelta
import openai
import hashlib
import uuid

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Student Diary",
    description="AI-powered diary for students with intelligent analysis",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer(auto_error=False)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    logger.info("OpenAI API key configured")
else:
    logger.warning("OpenAI API key not found")

# Mount static files
try:
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Static files mounted successfully")
except Exception as e:
    logger.warning(f"Could not mount static files: {e}")

# Data models
class DiaryEntry(BaseModel):
    content: str
    mood_score: int = 3
    student_id: Optional[str] = "anonymous"

class AnalysisResponse(BaseModel):
    status: str
    entry_id: str
    analysis: dict
    reflection: Optional[str] = None

# In-memory storage (for demo purposes)
entries_db = []
reflections_db = []

# Helper functions
async def analyze_text_with_openai(text: str) -> dict:
    """Analyze text using OpenAI API"""
    try:
        if not OPENAI_API_KEY:
            return {
                "sentiment": "neutral",
                "mood_detected": 0.5,
                "emotions": ["contemplative"],
                "topics": ["general"],
                "analysis_method": "fallback"
            }

        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are an AI assistant that analyzes student diary entries. 
                    Analyze the text and return JSON with: sentiment (positive/negative/neutral), 
                    emotions (list), topics (list), key_insights (list), suggestions (list).
                    Be supportive and encouraging."""
                },
                {
                    "role": "user", 
                    "content": f"Analyze this diary entry: {text}"
                }
            ],
            max_tokens=500,
            temperature=0.3
        )

        content = response.choices[0].message.content
        try:
            return json.loads(content)
        except:
            return {
                "sentiment": "neutral",
                "analysis": content,
                "emotions": ["thoughtful"],
                "topics": ["personal reflection"]
            }

    except Exception as e:
        logger.error(f"OpenAI analysis error: {e}")
        return {
            "sentiment": "neutral",
            "error": str(e),
            "analysis_method": "error_fallback",
            "emotions": ["uncertain"],
            "topics": ["general"]
        }

async def generate_reflection(entry_data: dict) -> str:
    """Generate a personalized reflection"""
    try:
        if not OPENAI_API_KEY:
            return """🌟 Thank you for sharing your thoughts today! 

Writing in your diary is a wonderful way to process your experiences and emotions. 
Every entry helps you grow and understand yourself better.

💭 Reflection Questions:
• What was one positive moment from today?
• What would you like to focus on tomorrow?
• How are you feeling right now?

Keep writing - you're doing great! 📝"""

        response = await asyncio.to_thread(
            openai.ChatCompletion.create,
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": """You are a supportive AI companion for students. Generate a warm, 
                    encouraging reflection based on their diary entry. Use emojis, ask thoughtful questions, 
                    and provide gentle insights. Keep it positive and supportive."""
                },
                {
                    "role": "user",
                    "content": f"Generate a reflection for this diary entry: {entry_data.get('content', '')}"
                }
            ],
            max_tokens=300,
            temperature=0.7
        )

        return response.choices[0].message.content

    except Exception as e:
        logger.error(f"Reflection generation error: {e}")
        return """🌟 Thank you for sharing your thoughts! 

Your diary is a safe space to explore your feelings and experiences. 
Keep writing and reflecting - it's a powerful tool for personal growth! 📝✨"""

# Routes
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
        <!DOCTYPE html>
        <html>
        <head>
            <title>AI Student Diary</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                .container { background: #f5f5f5; padding: 20px; border-radius: 10px; }
                textarea { width: 100%; height: 150px; padding: 10px; border-radius: 5px; border: 1px solid #ddd; }
                button { background: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 5px; cursor: pointer; }
                button:hover { background: #45a049; }
                .slider-container { margin: 20px 0; }
                .mood-slider { width: 100%; }
                .reflection { background: white; padding: 15px; border-radius: 5px; margin-top: 20px; }
            </style>
        </head>
        <body>
            <div class="container">
                <h1>🎓 AI Student Diary</h1>
                <p>Your intelligent companion for academic and personal growth</p>

                <h2>📝 Write Your Diary Entry</h2>
                <textarea id="diaryText" placeholder="How was your day? Share your thoughts, feelings, academic experiences..."></textarea>

                <div class="slider-container">
                    <label>How are you feeling? (1 = Very sad, 5 = Very happy)</label><br>
                    <input type="range" id="moodSlider" class="mood-slider" min="1" max="5" value="3">
                    <span id="moodValue">Neutral (3)</span>
                </div>

                <button onclick="saveEntry()">💾 Save Entry & Get AI Insights</button>

                <div id="response" class="reflection" style="display: none;">
                    <h3>🌟 AI Analysis & Reflection</h3>
                    <div id="analysisResult"></div>
                </div>

                <div class="reflection">
                    <h3>🌅 Today's Reflection</h3>
                    <div id="dailyReflection">Your daily AI reflection will appear here...</div>
                    <button onclick="getNewReflection()">🔄 Get New Reflection</button>
                </div>

                <div class="reflection">
                    <h3>📊 Your Progress</h3>
                    <p id="totalEntries">Total Entries: <span id="entryCount">0</span></p>
                </div>
            </div>

            <script>
                const moodSlider = document.getElementById('moodSlider');
                const moodValue = document.getElementById('moodValue');

                moodSlider.oninput = function() {
                    const moods = ['Very Sad (1)', 'Sad (2)', 'Neutral (3)', 'Happy (4)', 'Very Happy (5)'];
                    moodValue.textContent = moods[this.value - 1];
                };

                async function saveEntry() {
                    const content = document.getElementById('diaryText').value;
                    const mood = document.getElementById('moodSlider').value;

                    if (!content.trim()) {
                        alert('Please write something in your diary first!');
                        return;
                    }

                    try {
                        const response = await fetch('/api/v1/diary/entries', {
                            method: 'POST',
                            headers: { 'Content-Type': 'application/json' },
                            body: JSON.stringify({
                                content: content,
                                mood_score: parseInt(mood)
                            })
                        });

                        if (response.ok) {
                            const result = await response.json();
                            displayAnalysis(result);
                            document.getElementById('diaryText').value = '';
                            updateEntryCount();
                        } else {
                            throw new Error('Failed to save entry');
                        }
                    } catch (error) {
                        console.error('Error:', error);
                        alert('Error saving entry. Please try again.');
                    }
                }

                function displayAnalysis(result) {
                    const responseDiv = document.getElementById('response');
                    const analysisDiv = document.getElementById('analysisResult');

                    let html = `
                        <h4>✅ Entry Saved Successfully!</h4>
                        <p><strong>Sentiment:</strong> ${result.analysis.sentiment || 'neutral'}</p>
                    `;

                    if (result.analysis.emotions) {
                        html += `<p><strong>Emotions detected:</strong> ${result.analysis.emotions.join(', ')}</p>`;
                    }

                    if (result.analysis.topics) {
                        html += `<p><strong>Topics:</strong> ${result.analysis.topics.join(', ')}</p>`;
                    }

                    if (result.reflection) {
                        html += `<div style="background: #e8f4f8; padding: 10px; border-radius: 5px; margin-top: 10px;">
                            <h4>💭 Your Personal Reflection:</h4>
                            <p>${result.reflection}</p>
                        </div>`;
                    }

                    analysisDiv.innerHTML = html;
                    responseDiv.style.display = 'block';
                }

                async function getNewReflection() {
                    try {
                        const response = await fetch('/api/v1/diary/reflection/daily');
                        if (response.ok) {
                            const result = await response.json();
                            document.getElementById('dailyReflection').innerHTML = result.reflection;
                        }
                    } catch (error) {
                        console.error('Error getting reflection:', error);
                    }
                }

                function updateEntryCount() {
                    const currentCount = parseInt(document.getElementById('entryCount').textContent);
                    document.getElementById('entryCount').textContent = currentCount + 1;
                }

                // Load reflection on page load
                window.onload = function() {
                    getNewReflection();
                };
            </script>
        </body>
        </html>
        """)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AI Student Diary",
        "version": "1.0.0",
        "environment": ENVIRONMENT,
        "openai_configured": bool(OPENAI_API_KEY),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/diary/entries")
async def create_diary_entry(entry: DiaryEntry):
    """Create and analyze a new diary entry"""
    try:
        logger.info(f"Processing diary entry: {entry.content[:50]}...")

        # Generate unique entry ID
        entry_id = str(uuid.uuid4())

        # Analyze the entry with AI
        analysis = await analyze_text_with_openai(entry.content)

        # Generate reflection
        reflection = await generate_reflection({
            "content": entry.content,
            "mood_score": entry.mood_score,
            "analysis": analysis
        })

        # Store entry (in production, this would go to a database)
        entry_data = {
            "id": entry_id,
            "content": entry.content,
            "mood_score": entry.mood_score,
            "student_id": entry.student_id,
            "analysis": analysis,
            "reflection": reflection,
            "timestamp": datetime.now().isoformat(),
            "created_at": datetime.now()
        }

        entries_db.append(entry_data)
        logger.info(f"Entry saved with ID: {entry_id}")

        return AnalysisResponse(
            status="success",
            entry_id=entry_id,
            analysis=analysis,
            reflection=reflection
        )

    except Exception as e:
        logger.error(f"Error processing diary entry: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to process diary entry: {str(e)}"
        )

@app.get("/api/v1/diary/entries")
async def get_diary_entries(limit: int = 10):
    """Get recent diary entries"""
    try:
        # Sort by timestamp, most recent first
        sorted_entries = sorted(entries_db, key=lambda x: x.get("created_at", datetime.min), reverse=True)
        recent_entries = sorted_entries[:limit]

        # Remove sensitive content for summary
        summary_entries = []
        for entry in recent_entries:
            summary_entries.append({
                "id": entry["id"],
                "mood_score": entry["mood_score"],
                "sentiment": entry["analysis"].get("sentiment", "neutral"),
                "timestamp": entry["timestamp"],
                "preview": entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"]
            })

        return {
            "status": "success",
            "entries": summary_entries,
            "total_count": len(entries_db)
        }

    except Exception as e:
        logger.error(f"Error retrieving entries: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve entries")

@app.get("/api/v1/diary/reflection/daily")
async def get_daily_reflection():
    """Get daily AI reflection"""
    try:
        # Check if we have recent entries to base reflection on
        if entries_db:
            recent_entry = max(entries_db, key=lambda x: x.get("created_at", datetime.min))
            reflection = await generate_reflection(recent_entry)
        else:
            reflection = """🌅 Good morning! Welcome to your AI Student Diary.

This is your personal space for growth, reflection, and self-discovery. 
Start by writing about your day, your thoughts, or anything on your mind.

🌟 Daily Inspiration:
Every great journey begins with a single step. Your words today are building the foundation for tomorrow's success!

Ready to start your first entry? 📝✨"""

        return {
            "status": "success",
            "reflection": reflection,
            "generated_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error generating daily reflection: {e}")
        return {
            "status": "success",
            "reflection": "🌅 Good morning! Take a moment today to reflect on your growth and set positive intentions. You're doing great! ✨",
            "generated_at": datetime.now().isoformat()
        }

@app.get("/api/v1/analytics/overview")
async def get_analytics_overview():
    """Get analytics overview"""
    try:
        total_entries = len(entries_db)

        if total_entries == 0:
            return {
                "total_entries": 0,
                "mood_average": None,
                "streak_days": 0,
                "sentiment_distribution": {},
                "message": "Start writing entries to see your analytics!"
            }

        # Calculate mood average
        mood_scores = [entry["mood_score"] for entry in entries_db]
        mood_average = sum(mood_scores) / len(mood_scores)

        # Calculate sentiment distribution
        sentiments = [entry["analysis"].get("sentiment", "neutral") for entry in entries_db]
        sentiment_distribution = {}
        for sentiment in sentiments:
            sentiment_distribution[sentiment] = sentiment_distribution.get(sentiment, 0) + 1

        # Calculate streak (simplified - days with entries)
        entry_dates = [datetime.fromisoformat(entry["timestamp"]).date() for entry in entries_db]
        unique_dates = len(set(entry_dates))

        return {
            "total_entries": total_entries,
            "mood_average": round(mood_average, 1),
            "streak_days": unique_dates,
            "sentiment_distribution": sentiment_distribution,
            "last_entry": entries_db[-1]["timestamp"] if entries_db else None
        }

    except Exception as e:
        logger.error(f"Error generating analytics: {e}")
        return {
            "total_entries": len(entries_db),
            "mood_average": None,
            "streak_days": 0,
            "sentiment_distribution": {},
            "error": str(e)
        }

# Error handlers
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "Something went wrong. Please try again.",
            "type": type(exc).__name__
        }
    )

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AI Student Diary server on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
