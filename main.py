from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import os
import logging
import asyncio
import json
from datetime import datetime, timedelta
import openai
import hashlib
import uuid
import random
import re
from collections import defaultdict
import math

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
SECRET_KEY = os.getenv("SECRET_KEY", "fallback-secret-key")

# Initialize OpenAI
if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
    logger.info("OpenAI API key configured")

# Knowledge Graph Storage (In-memory Neo4j-like structure)
class KnowledgeGraph:
    def __init__(self):
        self.nodes = {}  # {node_id: {type, properties}}
        self.relationships = []  # [{from_id, to_id, type, properties}]
        self.initialize_mock_data()

    def add_node(self, node_id: str, node_type: str, properties: dict):
        self.nodes[node_id] = {"type": node_type, "properties": properties}

    def add_relationship(self, from_id: str, to_id: str, rel_type: str, properties: dict = None):
        self.relationships.append({
            "from_id": from_id,
            "to_id": to_id,
            "type": rel_type,
            "properties": properties or {}
        })

    def find_nodes(self, node_type: str = None, **filters):
        results = []
        for node_id, node_data in self.nodes.items():
            if node_type and node_data["type"] != node_type:
                continue
            match = True
            for key, value in filters.items():
                if key not in node_data["properties"] or node_data["properties"][key] != value:
                    match = False
                    break
            if match:
                results.append({"id": node_id, **node_data})
        return results

    def find_relationships(self, from_id: str = None, to_id: str = None, rel_type: str = None):
        results = []
        for rel in self.relationships:
            if from_id and rel["from_id"] != from_id:
                continue
            if to_id and rel["to_id"] != to_id:
                continue
            if rel_type and rel["type"] != rel_type:
                continue
            results.append(rel)
        return results

    def get_connected_nodes(self, node_id: str, rel_type: str = None):
        connected = []
        for rel in self.relationships:
            if rel["from_id"] == node_id:
                if not rel_type or rel["type"] == rel_type:
                    connected.append({
                        "node": self.nodes.get(rel["to_id"]),
                        "relationship": rel,
                        "node_id": rel["to_id"]
                    })
        return connected

    def initialize_mock_data(self):
        """Initialize with rich mock data for demo"""
        # Create main student
        self.add_node("student_1", "Student", {
            "name": "Arjun Sharma",
            "grade": 11,
            "stream": "Science (PCM)",
            "age": 16,
            "personality_traits": ["analytical", "introverted", "creative"],
            "academic_level": "above_average"
        })

        # Create subjects with emotional associations
        subjects = [
            ("math", "Mathematics", {"difficulty": 0.8, "interest": 0.9, "performance": 0.85}),
            ("physics", "Physics", {"difficulty": 0.7, "interest": 0.8, "performance": 0.75}),
            ("chemistry", "Chemistry", {"difficulty": 0.6, "interest": 0.5, "performance": 0.7}),
            ("english", "English", {"difficulty": 0.4, "interest": 0.6, "performance": 0.8}),
            ("biology", "Biology", {"difficulty": 0.5, "interest": 0.3, "performance": 0.6})
        ]

        for subject_id, name, stats in subjects:
            self.add_node(subject_id, "Subject", {"name": name, **stats})
            self.add_relationship("student_1", subject_id, "STUDIES", {
                "emotional_association": stats["interest"] - stats["difficulty"],
                "stress_level": 1 - stats["performance"]
            })

        # Create people in student's life
        people = [
            ("friend_1", "Friend", {"name": "Priya", "closeness": 0.9, "support_level": 0.8}),
            ("friend_2", "Friend", {"name": "Rohit", "closeness": 0.7, "support_level": 0.6}),
            ("teacher_1", "Teacher", {"name": "Mrs. Gupta", "subject": "Mathematics", "effectiveness": 0.9}),
            ("parent_1", "Parent", {"role": "Mother", "support_level": 0.8, "pressure_level": 0.6}),
            ("parent_2", "Parent", {"role": "Father", "support_level": 0.6, "pressure_level": 0.9})
        ]

        for person_id, person_type, props in people:
            self.add_node(person_id, person_type, props)
            if person_type == "Friend":
                self.add_relationship("student_1", person_id, "FRIENDS_WITH", {
                    "strength": props["closeness"],
                    "emotional_impact": props["support_level"]
                })
            elif person_type == "Teacher":
                self.add_relationship("student_1", person_id, "LEARNS_FROM", {
                    "effectiveness": props["effectiveness"]
                })
            elif person_type == "Parent":
                self.add_relationship("student_1", person_id, "FAMILY_RELATION", {
                    "relation_type": props["role"],
                    "support_level": props["support_level"],
                    "pressure_level": props["pressure_level"]
                })

        # Create historical emotions and events
        emotions = [
            ("anxiety", {"intensity": 0.7, "frequency": "high", "triggers": ["exams", "presentations"]}),
            ("excitement", {"intensity": 0.8, "frequency": "medium", "triggers": ["math_problems", "achievements"]}),
            ("stress", {"intensity": 0.6, "frequency": "medium", "triggers": ["deadlines", "family_pressure"]}),
            ("confidence", {"intensity": 0.5, "frequency": "low", "triggers": ["good_grades", "praise"]})
        ]

        for emotion_id, props in emotions:
            self.add_node(emotion_id, "Emotion", props)
            self.add_relationship("student_1", emotion_id, "EXPERIENCES", {
                "frequency": props["frequency"],
                "intensity": props["intensity"]
            })

        # Create past events for pattern recognition
        events = [
            ("exam_math_1", "Exam", {"subject": "Mathematics", "date": "2025-08-15", "outcome": "success", "stress_level": 0.8}),
            ("party_1", "Social", {"type": "birthday_party", "date": "2025-08-20", "outcome": "excluded", "emotional_impact": -0.7}),
            ("presentation_1", "Academic", {"subject": "Physics", "date": "2025-08-22", "outcome": "success", "confidence_boost": 0.6}),
            ("family_dinner", "Family", {"type": "career_discussion", "date": "2025-08-25", "stress_level": 0.9, "pressure_source": "parent_2"})
        ]

        for event_id, event_type, props in events:
            self.add_node(event_id, "Event", {"type": event_type, **props})
            self.add_relationship("student_1", event_id, "EXPERIENCED", {
                "emotional_impact": props.get("emotional_impact", 0),
                "stress_level": props.get("stress_level", 0)
            })

# Global Knowledge Graph instance
kg = KnowledgeGraph()

# Agent Classes
class NLPAgent:
    @staticmethod
    async def analyze_text(text: str) -> dict:
        """Advanced NLP analysis with mood detection"""

        # Mood detection patterns
        mood_patterns = {
            "very_positive": ["amazing", "fantastic", "excellent", "thrilled", "ecstatic", "wonderful"],
            "positive": ["good", "happy", "excited", "pleased", "confident", "optimistic", "proud"],
            "neutral": ["okay", "fine", "normal", "average", "typical"],
            "negative": ["bad", "sad", "worried", "stressed", "frustrated", "disappointed", "anxious"],
            "very_negative": ["terrible", "awful", "devastated", "hopeless", "miserable", "overwhelmed"]
        }

        # Emotion detection
        emotion_patterns = {
            "anxiety": ["anxious", "worried", "nervous", "scared", "panic", "stress"],
            "excitement": ["excited", "thrilled", "enthusiastic", "energetic"],
            "sadness": ["sad", "depressed", "down", "blue", "melancholy"],
            "anger": ["angry", "frustrated", "annoyed", "furious", "mad"],
            "confidence": ["confident", "proud", "accomplished", "successful"],
            "confusion": ["confused", "lost", "uncertain", "unclear", "puzzled"]
        }

        # Topic detection
        topic_patterns = {
            "mathematics": ["math", "algebra", "calculus", "geometry", "equations", "problem", "solve"],
            "physics": ["physics", "mechanics", "waves", "electricity", "motion", "energy"],
            "chemistry": ["chemistry", "reaction", "elements", "compounds", "lab", "experiment"],
            "social": ["friends", "party", "social", "group", "peer", "relationship"],
            "family": ["family", "parents", "mom", "dad", "home", "sister", "brother"],
            "exams": ["exam", "test", "preparation", "study", "grade", "marks", "result"],
            "career": ["career", "future", "job", "profession", "engineering", "doctor"]
        }

        text_lower = text.lower()

        # Detect mood
        mood_score = 3  # neutral default
        detected_mood = "neutral"
        for mood, words in mood_patterns.items():
            if any(word in text_lower for word in words):
                if mood == "very_positive":
                    mood_score = 5
                    detected_mood = "very_positive"
                elif mood == "positive":
                    mood_score = 4
                    detected_mood = "positive"
                elif mood == "negative":
                    mood_score = 2
                    detected_mood = "negative"
                elif mood == "very_negative":
                    mood_score = 1
                    detected_mood = "very_negative"
                break

        # Detect emotions
        detected_emotions = []
        for emotion, words in emotion_patterns.items():
            if any(word in text_lower for word in words):
                detected_emotions.append(emotion)

        if not detected_emotions:
            detected_emotions = ["contemplative"]

        # Detect topics
        detected_topics = []
        for topic, words in topic_patterns.items():
            if any(word in text_lower for word in words):
                detected_topics.append(topic)

        if not detected_topics:
            detected_topics = ["general"]

        # Entity extraction (people, subjects, events)
        entities = []

        # Find mentioned people from KG
        people_nodes = kg.find_nodes("Friend") + kg.find_nodes("Teacher") + kg.find_nodes("Parent")
        for person in people_nodes:
            name = person["properties"]["name"].lower()
            if name in text_lower:
                entities.append({
                    "type": "Person",
                    "name": person["properties"]["name"],
                    "id": person["id"]
                })

        # Find mentioned subjects
        subject_nodes = kg.find_nodes("Subject")
        for subject in subject_nodes:
            name = subject["properties"]["name"].lower()
            if name in text_lower or subject["id"] in text_lower:
                entities.append({
                    "type": "Subject",
                    "name": subject["properties"]["name"],
                    "id": subject["id"]
                })

        # Advanced sentiment analysis with context
        sentiment_score = (mood_score - 3) / 2  # Convert to -1 to 1 scale

        if OPENAI_API_KEY:
            try:
                # Use OpenAI for deeper analysis
                response = await asyncio.to_thread(
                    openai.ChatCompletion.create,
                    model="gpt-3.5-turbo",
                    messages=[
                        {
                            "role": "system",
                            "content": """You are an expert in analyzing student emotions and academic experiences. 
                            Analyze the text and return JSON with: sentiment_score (-1 to 1), key_insights (list), 
                            academic_concerns (list), social_aspects (list), suggestions (list).
                            Focus on understanding the student's emotional state and academic journey."""
                        },
                        {
                            "role": "user",
                            "content": f"Analyze this student diary entry: {text}"
                        }
                    ],
                    max_tokens=400,
                    temperature=0.3
                )

                openai_analysis = response.choices[0].message.content
                try:
                    openai_result = json.loads(openai_analysis)
                    sentiment_score = openai_result.get("sentiment_score", sentiment_score)
                except:
                    pass

            except Exception as e:
                logger.error(f"OpenAI analysis error: {e}")

        return {
            "mood_score": mood_score,
            "detected_mood": detected_mood,
            "sentiment_score": sentiment_score,
            "emotions": detected_emotions,
            "topics": detected_topics,
            "entities": entities,
            "analysis_confidence": 0.85,
            "processing_method": "advanced_nlp"
        }

class KnowledgeGraphAgent:
    @staticmethod
    def update_graph(entry_data: dict, analysis: dict):
        """Update KG with new entry data and relationships"""
        entry_id = entry_data["id"]

        # Create entry node
        kg.add_node(entry_id, "Entry", {
            "date": entry_data["timestamp"],
            "mood_score": analysis["mood_score"],
            "sentiment": analysis["detected_mood"],
            "text_preview": entry_data["content"][:100]
        })

        # Link to student
        kg.add_relationship("student_1", entry_id, "WROTE", {
            "timestamp": entry_data["timestamp"]
        })

        # Create emotion relationships
        for emotion in analysis["emotions"]:
            emotion_id = f"emotion_{emotion}_{entry_id}"
            kg.add_node(emotion_id, "EmotionInstance", {
                "type": emotion,
                "intensity": analysis["mood_score"] / 5.0,
                "date": entry_data["timestamp"]
            })
            kg.add_relationship(entry_id, emotion_id, "TRIGGERS", {
                "intensity": analysis["mood_score"] / 5.0
            })

        # Link to mentioned entities
        for entity in analysis["entities"]:
            if entity["type"] == "Person":
                kg.add_relationship(entry_id, entity["id"], "MENTIONS", {
                    "context": "diary_entry"
                })
            elif entity["type"] == "Subject":
                kg.add_relationship(entry_id, entity["id"], "DISCUSSES", {
                    "sentiment": analysis["sentiment_score"]
                })

        # Create topic relationships
        for topic in analysis["topics"]:
            topic_id = f"topic_{topic}"
            if topic_id not in kg.nodes:
                kg.add_node(topic_id, "Topic", {"label": topic})
            kg.add_relationship(entry_id, topic_id, "RELATED_TO", {
                "relevance": 0.8
            })

    @staticmethod
    def get_student_patterns(student_id: str = "student_1"):
        """Analyze patterns from KG"""

        # Get all entries
        entries = kg.find_nodes("Entry")
        if not entries:
            return {"message": "No entries found for pattern analysis"}

        # Mood trends
        mood_scores = [entry["properties"]["mood_score"] for entry in entries]
        avg_mood = sum(mood_scores) / len(mood_scores)
        mood_trend = "improving" if len(mood_scores) > 1 and mood_scores[-1] > mood_scores[0] else "stable"

        # Most discussed topics
        topic_counts = defaultdict(int)
        for entry in entries:
            topics = kg.get_connected_nodes(entry["id"], "RELATED_TO")
            for topic_rel in topics:
                topic_name = topic_rel["node"]["properties"]["label"]
                topic_counts[topic_name] += 1

        # Emotional patterns
        emotion_frequency = defaultdict(int)
        emotion_instances = kg.find_nodes("EmotionInstance")
        for emotion in emotion_instances:
            emotion_type = emotion["properties"]["type"]
            emotion_frequency[emotion_type] += 1

        # Social connections analysis
        friend_mentions = 0
        friends = kg.get_connected_nodes(student_id, "FRIENDS_WITH")
        for friend in friends:
            mentions = kg.find_relationships(to_id=friend["node_id"], rel_type="MENTIONS")
            friend_mentions += len(mentions)

        return {
            "total_entries": len(entries),
            "average_mood": round(avg_mood, 2),
            "mood_trend": mood_trend,
            "top_topics": dict(list(topic_counts.items())[:3]),
            "dominant_emotions": dict(list(emotion_frequency.items())[:3]),
            "social_engagement": friend_mentions,
            "academic_focus": topic_counts.get("mathematics", 0) + topic_counts.get("physics", 0) + topic_counts.get("chemistry", 0)
        }

class ReflectionAgent:
    @staticmethod
    async def generate_contextual_reflection(entry_data: dict, analysis: dict):
        """Generate reflection based on KG patterns and current analysis"""

        # Get student patterns
        patterns = KnowledgeGraphAgent.get_student_patterns()

        # Get relevant past experiences
        past_entries = kg.find_nodes("Entry")
        similar_mood_entries = [e for e in past_entries if abs(e["properties"]["mood_score"] - analysis["mood_score"]) <= 1]

        # Find coping strategies that worked
        successful_strategies = []
        if analysis["mood_score"] >= 4:  # Current entry is positive
            for entry in past_entries:
                if entry["properties"]["mood_score"] >= 4:
                    # This was a positive entry - extract what worked
                    connected_topics = kg.get_connected_nodes(entry["id"], "RELATED_TO")
                    for topic_rel in connected_topics:
                        topic = topic_rel["node"]["properties"]["label"]
                        if topic not in successful_strategies:
                            successful_strategies.append(topic)

        # Identify potential concerns
        concerns = []
        if analysis["mood_score"] <= 2:
            concerns.append("low_mood")
        if "anxiety" in analysis["emotions"]:
            concerns.append("anxiety_detected")
        if "stress" in analysis["emotions"]:
            concerns.append("stress_management")

        # Generate personalized reflection
        reflection_parts = []

        # Greeting based on mood
        if analysis["mood_score"] >= 4:
            reflection_parts.append("🌟 I can sense the positive energy in your writing today!")
        elif analysis["mood_score"] <= 2:
            reflection_parts.append("💙 Thank you for sharing your feelings. It takes courage to express difficult emotions.")
        else:
            reflection_parts.append("🌸 Thank you for taking time to reflect and write today.")

        # Pattern-based insights
        if patterns["mood_trend"] == "improving":
            reflection_parts.append(f"I've noticed your overall mood has been improving - that's wonderful to see! Your average mood score is {patterns['average_mood']}.")

        # Topic-specific encouragement
        if "mathematics" in analysis["topics"] and "mathematics" in patterns["top_topics"]:
            reflection_parts.append("I see mathematics continues to be an important part of your journey. Your analytical thinking is one of your strengths!")

        # Social aspects
        if "social" in analysis["topics"] and patterns["social_engagement"] > 0:
            reflection_parts.append("Your social connections, especially with friends like Priya and Rohit, are valuable sources of support.")

        # Coping suggestions based on KG
        if concerns:
            if "anxiety_detected" in concerns:
                reflection_parts.append("When feeling anxious, remember that you've successfully handled challenges before. Consider breaking big tasks into smaller, manageable steps.")
            if "stress_management" in concerns:
                reflection_parts.append("For stress relief, activities that have helped you before include focusing on subjects you enjoy, like mathematics, and connecting with supportive friends.")

        # Encouraging questions
        questions = []
        if analysis["mood_score"] >= 4:
            questions.append("What specific aspect of today brought you the most joy?")
            questions.append("How can you build on this positive momentum tomorrow?")
        else:
            questions.append("What's one small thing that might help you feel a bit better right now?")
            questions.append("Who in your support network could you reach out to if needed?")

        if questions:
            reflection_parts.append("\n🤔 Reflection Questions:")
            for q in questions:
                reflection_parts.append(f"• {q}")

        # Affirmation based on student profile
        reflection_parts.append("\n✨ Remember: Your analytical mind and creative thinking are powerful tools. You're building resilience with every entry you write.")

        return "\n\n".join(reflection_parts)

class AnalyticsAgent:
    @staticmethod
    def generate_insights():
        """Generate advanced analytics from KG"""

        patterns = KnowledgeGraphAgent.get_student_patterns()

        # Predictive insights
        predictions = []

        # Academic performance prediction
        math_entries = 0
        positive_math_entries = 0
        entries = kg.find_nodes("Entry")

        for entry in entries:
            topics = kg.get_connected_nodes(entry["id"], "RELATED_TO")
            for topic_rel in topics:
                if topic_rel["node"]["properties"]["label"] == "mathematics":
                    math_entries += 1
                    if entry["properties"]["mood_score"] >= 4:
                        positive_math_entries += 1

        if math_entries > 0:
            math_positivity = positive_math_entries / math_entries
            if math_positivity > 0.7:
                predictions.append("Strong positive association with mathematics detected - likely to excel in upcoming assessments")
            elif math_positivity < 0.3:
                predictions.append("Mathematics showing some challenges - consider additional support or different study approaches")

        # Social well-being prediction
        if patterns["social_engagement"] < 2:
            predictions.append("Low social engagement detected - building stronger peer connections could improve overall well-being")

        # Stress management insights
        stress_entries = [e for e in entries if "stress" in str(e["properties"]).lower()]
        if len(stress_entries) > len(entries) * 0.3:  # More than 30% stress-related
            predictions.append("Elevated stress levels detected - implementing regular stress-management techniques recommended")

        # Growth opportunities
        growth_areas = []
        if patterns["dominant_emotions"].get("confidence", 0) < 2:
            growth_areas.append("Building self-confidence through celebrating small achievements")

        if patterns["top_topics"].get("social", 0) > patterns["top_topics"].get("mathematics", 0):
            growth_areas.append("Balancing social activities with academic focus")

        return {
            "patterns": patterns,
            "predictions": predictions,
            "growth_opportunities": growth_areas,
            "strengths": ["Analytical thinking", "Emotional awareness", "Academic dedication"],
            "recommended_focus": ["Stress management", "Social connections", "Academic confidence"]
        }

# Data models
class DiaryEntry(BaseModel):
    content: str
    student_id: Optional[str] = "student_1"

class AnalysisResponse(BaseModel):
    status: str
    entry_id: str
    analysis: dict
    reflection: str
    kg_insights: dict

# Storage
entries_db = []
nlp_agent = NLPAgent()
kg_agent = KnowledgeGraphAgent()
reflection_agent = ReflectionAgent()
analytics_agent = AnalyticsAgent()

# Routes
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

            .left-panel { }
            .right-panel { }

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

            .insights-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; }
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

            .kg-insights { 
                background: #fff3e0; border: 2px solid #ff9800; border-radius: 10px;
                padding: 20px; margin-top: 15px;
            }

            .predictions { 
                background: #e8f5e8; border: 2px solid #4caf50; border-radius: 10px;
                padding: 20px; margin-top: 15px;
            }

            .predictions h4 { color: #2e7d32; margin-bottom: 15px; }
            .prediction-item { 
                background: white; padding: 10px; margin: 8px 0; border-radius: 6px;
                border-left: 3px solid #4caf50;
            }

            .loading { 
                display: inline-block; width: 20px; height: 20px;
                border: 3px solid #f3f3f3; border-top: 3px solid #667eea;
                border-radius: 50%; animation: spin 1s linear infinite;
            }

            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            @keyframes slideIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }

            .demo-note { 
                background: #fff9c4; border: 2px solid #ffeb3b; border-radius: 8px;
                padding: 15px; margin-bottom: 20px; text-align: center;
            }
            .demo-note strong { color: #f57c00; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🧠 AI Student Diary - Advanced Edition</h1>
                <p>Powered by Knowledge Graph & Intelligent Agents</p>
            </div>

            <div class="demo-note">
                <strong>🚀 DEMO MODE:</strong> This version showcases advanced AI with automatic mood detection, 
                Knowledge Graph relationships, and predictive insights using mock student data.
            </div>

            <div class="main-content">
                <div class="left-panel">
                    <div class="section">
                        <h2>📝 Write Your Diary Entry</h2>
                        <textarea id="diaryText" placeholder="Write naturally about your day, feelings, academic experiences, social interactions, or any thoughts on your mind...

Examples:
- 'Today's math test went really well! I solved the calculus problems faster than expected.'
- 'Feeling anxious about the physics presentation tomorrow. Priya offered to help practice.'
- 'Had a disagreement with Rohit during group work. Sometimes I prefer working alone.'"></textarea>

                        <button class="btn" onclick="saveEntry()" id="saveBtn">
                            🤖 Analyze with AI Agents
                        </button>

                        <div id="analysisResult" style="display: none;">
                            <!-- Analysis results will appear here -->
                        </div>
                    </div>
                </div>

                <div class="right-panel">
                    <div class="section">
                        <h2>🧠 Knowledge Graph Insights</h2>
                        <div id="kgInsights">
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
                    </div>

                    <div class="section">
                        <h2>🔮 AI Predictions</h2>
                        <div id="predictions">
                            <p>Write entries to see personalized predictions...</p>
                        </div>
                    </div>

                    <div class="section">
                        <h2>📊 Pattern Analysis</h2>
                        <div id="patterns">
                            <p>Analyzing your behavioral patterns...</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            async function saveEntry() {
                const content = document.getElementById('diaryText').value;
                const saveBtn = document.getElementById('saveBtn');

                if (!content.trim()) {
                    alert('Please write something in your diary first!');
                    return;
                }

                saveBtn.innerHTML = '<div class="loading"></div> AI Agents Processing...';
                saveBtn.disabled = true;

                try {
                    const response = await fetch('/api/v1/diary/entries', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ content: content })
                    });

                    if (response.ok) {
                        const result = await response.json();
                        displayAnalysis(result);
                        document.getElementById('diaryText').value = '';
                        updateDashboard();
                    } else {
                        throw new Error('Failed to analyze entry');
                    }
                } catch (error) {
                    console.error('Error:', error);
                    alert('Error: ' + error.message);
                } finally {
                    saveBtn.innerHTML = '🤖 Analyze with AI Agents';
                    saveBtn.disabled = false;
                }
            }

            function displayAnalysis(result) {
                const analysisDiv = document.getElementById('analysisResult');
                const analysis = result.analysis;

                // Mood color mapping
                const moodColors = {
                    1: '#f44336', 2: '#ff9800', 3: '#9e9e9e', 4: '#4caf50', 5: '#8bc34a'
                };

                let html = `
                    <div class="analysis-result">
                        <h3>🤖 AI Analysis Complete</h3>

                        <div class="mood-display">
                            <div class="mood-score" style="background: ${moodColors[analysis.mood_score]}">
                                ${analysis.mood_score}
                            </div>
                            <div>
                                <strong>Detected Mood:</strong> ${analysis.detected_mood}<br>
                                <strong>Confidence:</strong> ${(analysis.analysis_confidence * 100).toFixed(1)}%
                            </div>
                        </div>

                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 15px 0;">
                            <div>
                                <strong>🎭 Emotions:</strong><br>
                                ${analysis.emotions.map(e => `<span style="background:#e3f2fd; padding:4px 8px; border-radius:12px; margin:2px; display:inline-block;">${e}</span>`).join('')}
                            </div>
                            <div>
                                <strong>📚 Topics:</strong><br>
                                ${analysis.topics.map(t => `<span style="background:#f3e5f5; padding:4px 8px; border-radius:12px; margin:2px; display:inline-block;">${t}</span>`).join('')}
                            </div>
                        </div>

                        ${analysis.entities.length > 0 ? `
                            <div style="margin: 15px 0;">
                                <strong>👥 Mentioned:</strong><br>
                                ${analysis.entities.map(e => `<span style="background:#e8f5e8; padding:4px 8px; border-radius:12px; margin:2px; display:inline-block;">${e.name} (${e.type})</span>`).join('')}
                            </div>
                        ` : ''}

                        <div class="reflection-box">
                            <h4>💭 Personalized Reflection:</h4>
                            <p>${result.reflection.replace(/\n/g, '<br>')}</p>
                        </div>

                        <div class="kg-insights">
                            <h4>🕸️ Knowledge Graph Insights:</h4>
                            <p><strong>Pattern Recognition:</strong> ${result.kg_insights.mood_trend} mood trend detected</p>
                            <p><strong>Academic Focus:</strong> ${result.kg_insights.academic_focus} academic-related entries</p>
                            <p><strong>Social Engagement:</strong> ${result.kg_insights.social_engagement} social interactions tracked</p>
                        </div>
                    </div>
                `;

                analysisDiv.innerHTML = html;
                analysisDiv.style.display = 'block';
                analysisDiv.scrollIntoView({ behavior: 'smooth' });
            }

            async function updateDashboard() {
                try {
                    const response = await fetch('/api/v1/analytics/insights');
                    if (response.ok) {
                        const insights = await response.json();

                        document.getElementById('totalEntries').textContent = insights.patterns.total_entries;
                        document.getElementById('avgMood').textContent = insights.patterns.average_mood;
                        document.getElementById('socialScore').textContent = insights.patterns.social_engagement;

                        // Update predictions
                        const predictionsDiv = document.getElementById('predictions');
                        if (insights.predictions.length > 0) {
                            predictionsDiv.innerHTML = insights.predictions.map(p => 
                                `<div class="prediction-item">🔮 ${p}</div>`
                            ).join('');
                        }

                        // Update patterns
                        const patternsDiv = document.getElementById('patterns');
                        patternsDiv.innerHTML = `
                            <p><strong>Top Topics:</strong></p>
                            ${Object.entries(insights.patterns.top_topics).map(([topic, count]) => 
                                `<div style="margin: 5px 0;">📌 ${topic}: ${count} mentions</div>`
                            ).join('')}
                        `;
                    }
                } catch (error) {
                    console.error('Error updating dashboard:', error);
                }
            }

            // Initialize dashboard
            window.onload = updateDashboard;
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
        "kg_nodes": len(kg.nodes),
        "kg_relationships": len(kg.relationships),
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/v1/diary/entries")
async def create_advanced_entry(entry: DiaryEntry):
    """Process entry through all AI agents"""
    try:
        logger.info(f"Processing advanced entry: {entry.content[:50]}...")

        entry_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        # Step 1: NLP Agent Analysis
        logger.info("Running NLP Agent...")
        analysis = await nlp_agent.analyze_text(entry.content)

        # Step 2: Update Knowledge Graph
        logger.info("Updating Knowledge Graph...")
        entry_data = {
            "id": entry_id,
            "content": entry.content,
            "student_id": entry.student_id,
            "timestamp": timestamp
        }
        kg_agent.update_graph(entry_data, analysis)

        # Step 3: Generate Contextual Reflection
        logger.info("Generating reflection...")
        reflection = await reflection_agent.generate_contextual_reflection(entry_data, analysis)

        # Step 4: Get KG Insights
        logger.info("Extracting KG insights...")
        kg_insights = kg_agent.get_student_patterns()

        # Store entry
        entries_db.append({
            **entry_data,
            "analysis": analysis,
            "reflection": reflection,
            "kg_insights": kg_insights
        })

        return AnalysisResponse(
            status="success",
            entry_id=entry_id,
            analysis=analysis,
            reflection=reflection,
            kg_insights=kg_insights
        )

    except Exception as e:
        logger.error(f"Error in advanced processing: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/analytics/insights")
async def get_advanced_insights():
    """Get comprehensive analytics from all agents"""
    try:
        insights = analytics_agent.generate_insights()
        return insights
    except Exception as e:
        logger.error(f"Error generating insights: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/kg/graph")
async def get_knowledge_graph():
    """Get Knowledge Graph structure for visualization"""
    try:
        return {
            "nodes": [
                {"id": node_id, **node_data} 
                for node_id, node_data in kg.nodes.items()
            ],
            "relationships": kg.relationships,
            "statistics": {
                "total_nodes": len(kg.nodes),
                "total_relationships": len(kg.relationships),
                "node_types": list(set(node["type"] for node in kg.nodes.values()))
            }
        }
    except Exception as e:
        logger.error(f"Error retrieving KG: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting Advanced AI Student Diary on port {port}")
    logger.info(f"Knowledge Graph initialized with {len(kg.nodes)} nodes and {len(kg.relationships)} relationships")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
