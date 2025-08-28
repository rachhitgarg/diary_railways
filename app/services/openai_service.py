"""OpenAI integration for diary analysis"""

import openai
import os
import logging
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key:
            self.client = openai.OpenAI(api_key=api_key)
        else:
            self.client = None
            logger.warning("OpenAI API key not found")

    async def analyze_diary_entry(self, content: str) -> Dict[str, Any]:
        """Analyze diary entry for sentiment, emotions, and topics"""
        if not self.client:
            return self._fallback_analysis(content)

        try:
            prompt = f"""
            Analyze this student diary entry from an Indian student (5th-12th grade):

            "{content}"

            Provide analysis in JSON format:
            {{
                "sentiment": "positive/negative/neutral",
                "mood_score": 0.0-1.0,
                "emotions": ["joy", "anxiety", "excitement", etc.],
                "topics": ["academics", "friends", "family", etc.],
                "academic_subjects": ["math", "science", etc.],
                "stress_indicators": ["exam pressure", "peer pressure", etc.],
                "cultural_context": ["festival", "family expectations", etc.],
                "support_needed": true/false,
                "crisis_level": "none/low/medium/high"
            }}

            Focus on Indian education system context (JEE, NEET, board exams, family pressure).
            """

            response = await self.client.chat.completions.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an AI counselor specializing in Indian student mental health and academic pressure."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3
            )

            analysis = json.loads(response.choices[0].message.content)
            return analysis

        except Exception as e:
            logger.error(f"OpenAI analysis error: {e}")
            return self._fallback_analysis(content)

    def _fallback_analysis(self, content: str) -> Dict[str, Any]:
        """Fallback analysis when OpenAI is not available"""
        return {
            "sentiment": "positive" if any(word in content.lower() for word in ["good", "happy", "excited"]) else "neutral",
            "mood_score": 0.7 if "good" in content.lower() else 0.5,
            "emotions": ["joy"] if "happy" in content.lower() else ["neutral"],
            "topics": ["academics"] if "study" in content.lower() else ["general"],
            "academic_subjects": [],
            "stress_indicators": ["exam pressure"] if "exam" in content.lower() else [],
            "cultural_context": [],
            "support_needed": False,
            "crisis_level": "none"
        }

    async def generate_reflection(self, past_entries: List[str], current_mood: str) -> str:
        """Generate morning reflection based on past entries"""
        if not self.client:
            return self._fallback_reflection()

        try:
            entries_text = "\n".join(past_entries[-5:])  # Last 5 entries

            prompt = f"""
            Create a supportive morning reflection for an Indian student based on their recent diary entries:

            Recent entries:
            {entries_text}

            Current mood: {current_mood}

            Generate a warm, encouraging reflection (2-3 paragraphs) that:
            1. Acknowledges their feelings and experiences
            2. Highlights positive patterns or growth
            3. Offers gentle guidance for the day ahead
            4. Is culturally sensitive to Indian family/academic context
            5. Uses encouraging language suitable for teenagers

            Format as a friendly morning message.
            """

            response = await self.client.chat.completions.acreate(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a caring AI mentor for Indian students, providing emotional support and guidance."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7
            )

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"Reflection generation error: {e}")
            return self._fallback_reflection()

    def _fallback_reflection(self) -> str:
        """Fallback reflection when OpenAI is not available"""
        return """🌅 Good morning! 

Remember that every new day brings fresh opportunities to learn and grow. You're doing great on your journey, and every small step forward counts.

Take today as a chance to discover something new about yourself. You've got this! 🌟"""

    async def create_embedding(self, text: str) -> List[float]:
        """Create embedding for text using OpenAI"""
        if not self.client:
            return []

        try:
            response = await self.client.embeddings.acreate(
                model="text-embedding-ada-002",
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Embedding creation error: {e}")
            return []

# Singleton instance
openai_service = OpenAIService()
