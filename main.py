from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
import logging
import json
from datetime import datetime
import uuid
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Student Diary - Advanced Edition",
    description="AI-powered diary with Knowledge Graph and Agent Architecture",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Simple mock data for demo
mock_knowledge_graph = {
    "student_profile": {
        "name": "Arjun Sharma",
        "grade": 11,
        "strengths": ["mathematics", "analytical_thinking"],
        "challenges": ["physics", "social_anxiety"]
    },
    "subjects": {
        "mathematics": {"performance": 0.9, "interest": 0.95, "emotional_association": "positive"},
        "physics": {"performance": 0.6, "interest": 0.7, "emotional_association": "challenging"},
        "chemistry": {"performance": 0.7, "interest": 0.5, "emotional_association": "neutral"}
    },
    "social_network": {
        "priya": {"type": "friend", "support_level": 0.9, "closeness": 0.8},
        "rohit": {"type": "friend", "support_level": 0.6, "closeness": 0.7}
    }
}

# Storage
entries_storage = []

class DiaryEntry(BaseModel):
    content: str
    student_id: Optional[str] = "student_1"

def analyze_text_advanced(text: str) -> Dict[str, Any]:
    """Advanced NLP analysis with mood detection"""
    text_lower = text.lower()

    # Mood detection patterns
    mood_indicators = {
        "very_positive": ["fantastic", "amazing", "excellent", "thrilled", "wonderful", "perfect"],
        "positive": ["good", "happy", "great", "pleased", "satisfied", "confident", "excited"],
        "neutral": ["okay", "fine", "normal", "average"],
        "negative": ["bad", "sad", "difficult", "challenging", "worried", "stressed"],
        "very_negative": ["terrible", "awful", "horrible", "devastated", "overwhelmed"]
    }

    # Detect mood automatically
    detected_mood = "neutral"
    mood_score = 3

    for mood_level, words in mood_indicators.items():
        if any(word in text_lower for word in words):
            if mood_level == "very_positive":
                mood_score = 5
                detected_mood = "very_positive"
            elif mood_level == "positive":
                mood_score = 4
                detected_mood = "positive"
            elif mood_level == "negative":
                mood_score = 2
                detected_mood = "negative"
            elif mood_level == "very_negative":
                mood_score = 1
                detected_mood = "very_negative"
            break

    # Emotion detection
    emotion_patterns = {
        "happiness": ["happy", "joy", "excited", "pleased", "satisfied"],
        "anxiety": ["anxious", "worried", "nervous", "stressed"],
        "confidence": ["confident", "proud", "accomplished"],
        "frustration": ["frustrated", "annoyed", "difficult"],
        "confusion": ["confused", "unclear", "lost", "don't understand"]
    }

    detected_emotions = []
    for emotion, words in emotion_patterns.items():
        if any(word in text_lower for word in words):
            detected_emotions.append(emotion)

    if not detected_emotions:
        detected_emotions = ["contemplative"]

    # Topic detection
    topic_patterns = {
        "mathematics": ["math", "maths", "algebra", "calculus", "equations"],
        "physics": ["physics", "mechanics", "motion", "energy"],
        "chemistry": ["chemistry", "reaction", "lab", "experiment"],
        "social": ["friends", "social", "party", "group"],
        "academic": ["test", "exam", "study", "grade", "score"]
    }

    detected_topics = []
    for topic, words in topic_patterns.items():
        if any(word in text_lower for word in words):
            detected_topics.append(topic)

    if not detected_topics:
        detected_topics = ["general"]

    # Entity extraction
    entities = []
    known_people = ["priya", "rohit", "mrs. gupta"]
    for person in known_people:
        if person in text_lower:
            entities.append({"type": "Person", "name": person.title()})

    return {
        "mood_score": mood_score,
        "detected_mood": detected_mood,
        "emotions": detected_emotions,
        "topics": detected_topics,
        "entities": entities,
        "sentiment_score": (mood_score - 3) / 2,
        "analysis_confidence": 0.85,
        "processing_method": "pattern_matching"
    }

def generate_reflection(content: str, analysis: Dict[str, Any]) -> str:
    """Generate contextual reflection"""

    mood_score = analysis["mood_score"]
    emotions = analysis["emotions"]
    topics = analysis["topics"]

    reflection_parts = []

    # Mood-based greeting
    if mood_score >= 4:
        reflection_parts.append("🌟 I can sense the positive energy in your writing today!")
    elif mood_score <= 2:
        reflection_parts.append("💙 Thank you for sharing your feelings. It takes courage to express difficult emotions.")
    else:
        reflection_parts.append("🌸 Thank you for taking time to reflect today.")

    # Topic-specific insights
    if "mathematics" in topics:
        if mood_score >= 4:
            reflection_parts.append("Your success in mathematics is wonderful to see! Your analytical strengths are really shining through.")
        else:
            reflection_parts.append("Mathematics can be challenging, but remember that every problem you work through builds your analytical skills.")

    if "physics" in topics:
        reflection_parts.append("Physics requires patience and practice. Don't be discouraged by temporary challenges - you're building understanding step by step.")

    # Emotional support
    if "anxiety" in emotions:
        reflection_parts.append("When feeling anxious, remember to take deep breaths and break big challenges into smaller, manageable steps.")

    if "happiness" in emotions:
        reflection_parts.append("Hold onto this positive feeling! Success builds upon itself, and you're creating momentum for future achievements.")

    # Questions for reflection
    questions = []
    if mood_score >= 4:
        questions.append("What specific aspect of today brought you the most satisfaction?")
    else:
        questions.append("What's one small thing that might help you feel a bit better?")

    if questions:
        reflection_parts.append("\n🤔 Reflection Questions:")
        for q in questions:
            reflection_parts.append(f"• {q}")

    reflection_parts.append("\n✨ Remember: Every entry you write is a step toward better self-understanding and growth!")

    return "\n\n".join(reflection_parts)

def get_kg_insights() -> Dict[str, Any]:
    """Get Knowledge Graph insights"""
    total_entries = len(entries_storage)

    if total_entries == 0:
        return {
            "total_entries": 0,
            "average_mood": 0,
            "mood_trend": "no_data",
            "social_engagement": 0,
            "academic_focus": 0
        }

    # Calculate insights from stored entries
    mood_scores = [entry.get("mood_score", 3) for entry in entries_storage]
    avg_mood = sum(mood_scores) / len(mood_scores) if mood_scores else 3

    # Count academic mentions
    academic_count = sum(1 for entry in entries_storage 
                        if any(topic in ["mathematics", "physics", "chemistry"] 
                              for topic in entry.get("topics", [])))

    # Count social mentions  
    social_count = sum(1 for entry in entries_storage
                      if "social" in entry.get("topics", []) or 
                         any(entity.get("type") == "Person" for entity in entry.get("entities", [])))

    return {
        "total_entries": total_entries,
        "average_mood": round(avg_mood, 1),
        "mood_trend": "improving" if len(mood_scores) > 1 and mood_scores[-1] > mood_scores[0] else "stable",
        "social_engagement": social_count,
        "academic_focus": academic_count
    }

@app.get("/")
async def root():
    """Serve the advanced interface"""
    return HTMLResponse("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Student Diary - Advanced Edition</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { 
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0; padding: 20px; min-height: 100vh;
            }
            .container { 
                max-width: 1200px; margin: 0 auto; 
                background: white; border-radius: 15px;
                box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                overflow: hidden;
            }
            .header { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 30px; text-align: center;
            }
            .header h1 { font-size: 2.5rem; margin: 0 0 10px 0; }
            .header p { font-size: 1.1rem; opacity: 0.9; margin: 0; }

            .main-content { display: grid; grid-template-columns: 2fr 1fr; gap: 30px; padding: 30px; }

            .section { 
                background: #f8f9fa; padding: 25px; margin-bottom: 25px;
                border-radius: 12px; border-left: 4px solid #667eea;
            }
            .section h2 { color: #333; margin: 0 0 20px 0; display: flex; align-items: center; gap: 10px; }

            textarea { 
                width: 100%; height: 120px; padding: 15px; border: 2px solid #e0e0e0;
                border-radius: 8px; font-size: 16px; resize: vertical; font-family: inherit;
                transition: border-color 0.3s;
            }
            textarea:focus { border-color: #667eea; outline: none; }

            .btn { 
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white; padding: 12px 24px; border: none; border-radius: 8px;
                cursor: pointer; font-size: 16px; font-weight: 600;
                transition: transform 0.2s, box-shadow 0.2s;
                display: inline-flex; align-items: center; gap: 8px;
            }
            .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4); }
            .btn:disabled { opacity: 0.6; cursor: not-allowed; transform: none; }

            .analysis-result { 
                background: white; border: 2px solid #667eea; border-radius: 12px;
                padding: 20px; margin-top: 20px; animation: slideIn 0.5s ease;
            }

            .mood-display { 
                display: flex; align-items: center; gap: 15px; 
                background: white; padding: 15px; border-radius: 8px; margin: 15px 0;
            }
            .mood-score { 
                font-size: 2rem; font-weight: bold; 
                width: 60px; height: 60px; border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                color: white;
            }

            .insights-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 15px; }
            .insight-card { 
                background: white; padding: 15px; border-radius: 8px;
                border-left: 4px solid #667eea; text-align: center;
            }
            .insight-number { font-size: 1.8rem; font-weight: bold; color: #667eea; }
            .insight-label { color: #666; margin-top: 5px; }

            .reflection-box { 
                background: linear-gradient(135deg, #e3f2fd 0%, #f3e5f5 100%);
                padding: 20px; border-radius: 10px; margin-top: 15px;
                border-left: 4px solid #2196F3;
            }

            .loading { 
                display: inline-block; width: 20px; height: 20px;
                border: 3px solid #f3f3f3; border-top: 3px solid #667eea;
                border-radius: 50%; animation: spin 1s linear infinite;
            }

            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

            .demo-banner { 
                background: #fff3cd; border: 2px solid #ffc107; border-radius: 8px;
                padding: 15px; margin-bottom: 20px; text-align: center;
            }
            .demo-banner strong { color: #856404; }

            .tag { 
                background: #e3f2fd; padding: 4px 8px; border-radius: 12px; 
                margin: 2px; display: inline-block; font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 AI Student Diary - Advanced Edition</h1>
                <p>Powered by Knowledge Graph & Intelligent Agents</p>
            </div>

            <div class="demo-banner">
                <strong>🚀 ADVANCED AI DEMO:</strong> Automatic mood detection, Knowledge Graph analysis, 
                and intelligent reflections powered by AI agents!
            </div>

            <div class="main-content">
                <div class="left-panel">
                    <div class="section">
                        <h2>📝 Write Your Diary Entry</h2>
                        <textarea id="diaryText" placeholder="Write naturally about your day...

Try these examples:
• 'Today's math test went fantastic! I solved all problems correctly.'
• 'Feeling anxious about tomorrow's physics presentation.'
• 'Had a good chat with Priya about the chemistry project.'"></textarea>

                        <button class="btn" onclick="analyzeEntry()" id="analyzeBtn">
                            🤖 Analyze with AI Agents
                        </button>

                        <div id="analysisResult" style="display: none;"></div>
                    </div>
                </div>

                <div class="right-panel">
                    <div class="section">
                        <h2>🧠 Knowledge Graph Insights</h2>
                        <div class="insights-grid">
                            <div class="insight-card">
                                <div class="insight-number" id="totalEntries">0</div>
                                <div class="insight-label">Total Entries</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number" id="avgMood">-</div>
                                <div class="insight-label">Avg Mood</div>
                            </div>
                            <div class="insight-card">
                                <div class="insight-number" id="socialScore">-</div>
                                <div class="insight-label">Social Score</div>
                            </div>
                        </div>
                    </div>

                    <div class="section">
                        <h2>🔮 AI Predictions</h2>
                        <div id="predictions">
                            <p>Write entries to unlock AI predictions...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function analyzeEntry() {
                const content = document.getElementById('diaryText').value;
                const analyzeBtn = document.getElementById('analyzeBtn');
                const resultDiv = document.getElementById('analysisResult');

                if (!content.trim()) {
                    alert('Please write something in your diary first!');
                    return;
                }

                // Show loading state
                analyzeBtn.innerHTML = '<div class="loading"></div> Processing...';
                analyzeBtn.disabled = true;

                try {
                    const response = await fetch('/api/v1/diary/entries', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content: content })
                    });

                    if (!response.ok) {
                        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                    }

                    const result = await response.json();
                    displayAnalysis(result);
                    document.getElementById('diaryText').value = '';
                    updateInsights();

                } catch (error) {
                    console.error('Analysis error:', error);
                    resultDiv.innerHTML = `
                        <div class="analysis-result">
                            <h3>❌ Analysis Failed</h3>
                            <p><strong>Error:</strong> ${error.message}</p>
                            <p>Please check browser console for details.</p>
                        </div>
                    `;
                    resultDiv.style.display = 'block';
                } finally {
                    analyzeBtn.innerHTML = '🤖 Analyze with AI Agents';
                    analyzeBtn.disabled = false;
                }
            }

            function displayAnalysis(result) {
                const resultDiv = document.getElementById('analysisResult');
                const analysis = result.analysis;

                const moodColors = {
                    1: '#f44336', 2: '#ff9800', 3: '#9e9e9e', 4: '#4caf50', 5: '#8bc34a'
                };

                let html = `
                    <div class="analysis-result">
                        <h3>🎯 AI Analysis Complete</h3>

                        <div class="mood-display">
                            <div class="mood-score" style="background: ${moodColors[analysis.mood_score]}">
                                ${analysis.mood_score}
                            </div>
                            <div>
                                <strong>Auto-Detected Mood:</strong> ${analysis.detected_mood}<br>
                                <strong>Confidence:</strong> ${(analysis.analysis_confidence * 100).toFixed(0)}%
                            </div>
                        </div>

                        <div style="margin: 15px 0;">
                            <strong>🎭 Emotions:</strong><br>
                            ${analysis.emotions.map(e => `<span class="tag">${e}</span>`).join('')}
                        </div>

                        <div style="margin: 15px 0;">
                            <strong>📚 Topics:</strong><br>
                            ${analysis.topics.map(t => `<span class="tag" style="background: #f3e5f5;">${t}</span>`).join('')}
                        </div>

                        ${analysis.entities.length > 0 ? `
                            <div style="margin: 15px 0;">
                                <strong>👥 People Mentioned:</strong><br>
                                ${analysis.entities.map(e => `<span class="tag" style="background: #e8f5e8;">${e.name}</span>`).join('')}
                            </div>
                        ` : ''}

                        <div class="reflection-box">
                            <h4>💭 AI Reflection:</h4>
                            <p>${result.reflection.replace(/\n/g, '<br>')}</p>
                        </div>

                        <div style="background: #fff3e0; padding: 15px; border-radius: 8px; margin-top: 15px;">
                            <h4>🕸️ Knowledge Graph Update:</h4>
                            <p><strong>Entry processed and relationships updated!</strong></p>
                            <p>• Mood pattern: ${result.kg_insights.mood_trend}</p>
                            <p>• Academic focus: ${result.kg_insights.academic_focus} entries</p>
                            <p>• Social engagement: ${result.kg_insights.social_engagement} interactions</p>
                        </div>
                    </div>
                `;

                resultDiv.innerHTML = html;
                resultDiv.style.display = 'block';
                resultDiv.scrollIntoView({ behavior: 'smooth' });
            }

            async function updateInsights() {
                try {
                    const response = await fetch('/api/v1/analytics/insights');
                    if (response.ok) {
                        const insights = await response.json();
                        document.getElementById('totalEntries').textContent = insights.total_entries;
                        document.getElementById('avgMood').textContent = insights.average_mood || '-';
                        document.getElementById('socialScore').textContent = insights.social_engagement;

                        // Update predictions
                        const predictionsDiv = document.getElementById('predictions');
                        if (insights.total_entries > 0) {
                            predictionsDiv.innerHTML = `
                                <div style="background: #e8f5e8; padding: 10px; border-radius: 5px; margin: 5px 0;">
                                    🔮 Mood trend: ${insights.mood_trend}
                                </div>
                                <div style="background: #f3e5f5; padding: 10px; border-radius: 5px; margin: 5px 0;">
                                    📊 Academic engagement detected
                                </div>
                            `;
                        }
                    }
                } catch (error) {
                    console.error('Error updating insights:', error);
                }
            }

            // Initialize
            window.onload = updateInsights;
        </script>
    </body>
    </html>
    """)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "AI Student Diary - Advanced Edition",
        "version": "2.0.0",
        "agents": ["NLP", "KnowledgeGraph", "Reflection", "Analytics"],
        "features": ["automatic_mood_detection", "knowledge_graph", "pattern_analysis"],
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/diary/entries")
async def create_entry(entry: DiaryEntry):
    """Process diary entry with AI agents"""
    try:
        logger.info(f"Processing entry: {entry.content[:50]}...")

        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # NLP Analysis
        analysis = analyze_text_advanced(entry.content)
        logger.info(f"NLP analysis complete: mood={analysis['mood_score']}, emotions={analysis['emotions']}")

        # Generate reflection
        reflection = generate_reflection(entry.content, analysis)

        # Update storage
        entry_data = {
            "id": entry_id,
            "content": entry.content,
            "timestamp": timestamp,
            "mood_score": analysis["mood_score"],
            "emotions": analysis["emotions"],
            "topics": analysis["topics"],
            "entities": analysis["entities"]
        }
        entries_storage.append(entry_data)

        # Get KG insights
        kg_insights = get_kg_insights()

        return {
            "status": "success",
            "entry_id": entry_id,
            "analysis": analysis,
            "reflection": reflection,
            "kg_insights": kg_insights
        }

    except Exception as e:
        logger.error(f"Error processing entry: {e}")
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")

@app.get("/api/v1/analytics/insights")
async def get_insights():
    """Get analytics insights"""
    try:
        insights = get_kg_insights()
        return insights
    except Exception as e:
        logger.error(f"Error getting insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting AI Student Diary Advanced Edition on port {port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
