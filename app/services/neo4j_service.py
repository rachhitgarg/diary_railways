"""Neo4j graph database service"""

import os
import logging
from typing import Dict, List, Any
import json

logger = logging.getLogger(__name__)

class Neo4jService:
    def __init__(self):
        self.uri = os.getenv("NEO4J_URI")
        self.user = os.getenv("NEO4J_USER")
        self.password = os.getenv("NEO4J_PASSWORD")

        if not all([self.uri, self.user, self.password]):
            logger.warning("Neo4j credentials not complete")
            self.driver = None
        else:
            try:
                from neo4j import AsyncGraphDatabase
                self.driver = AsyncGraphDatabase.driver(
                    self.uri, 
                    auth=(self.user, self.password)
                )
                logger.info("✅ Neo4j driver initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Neo4j: {e}")
                self.driver = None

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def create_student_node(self, user_id: str, user_data: Dict[str, Any]):
        """Create student node in knowledge graph"""
        if not self.driver:
            logger.warning("Neo4j not available, skipping student node creation")
            return

        async with self.driver.session() as session:
            try:
                query = """
                MERGE (s:Student {id: $user_id})
                SET s.name = $name,
                    s.grade = $grade,
                    s.school = $school,
                    s.created_at = datetime(),
                    s.updated_at = datetime()
                RETURN s
                """

                await session.run(query, {
                    "user_id": user_id,
                    "name": user_data.get("name", ""),
                    "grade": user_data.get("grade", 0),
                    "school": user_data.get("school", "")
                })

                logger.info(f"✅ Created student node for {user_id}")

            except Exception as e:
                logger.error(f"Neo4j student creation error: {e}")

    async def create_diary_entry_node(self, entry_id: str, user_id: str, analysis: Dict[str, Any]):
        """Create diary entry node and relationships"""
        if not self.driver:
            logger.warning("Neo4j not available, skipping entry node creation")
            return

        async with self.driver.session() as session:
            try:
                # Create entry node
                entry_query = """
                MATCH (s:Student {id: $user_id})
                CREATE (e:Entry {
                    id: $entry_id,
                    sentiment: $sentiment,
                    mood_score: $mood_score,
                    date: datetime(),
                    crisis_level: $crisis_level
                })
                CREATE (s)-[:WROTE]->(e)
                RETURN e
                """

                await session.run(entry_query, {
                    "entry_id": entry_id,
                    "user_id": user_id,
                    "sentiment": analysis.get("sentiment", "neutral"),
                    "mood_score": analysis.get("mood_score", 0.5),
                    "crisis_level": analysis.get("crisis_level", "none")
                })

                # Create emotion nodes and relationships
                emotions = analysis.get("emotions", [])
                for emotion in emotions:
                    emotion_query = """
                    MATCH (e:Entry {id: $entry_id})
                    MERGE (em:Emotion {name: $emotion})
                    CREATE (e)-[:EXPRESSES]->(em)
                    """

                    await session.run(emotion_query, {
                        "entry_id": entry_id,
                        "emotion": emotion
                    })

                # Create topic nodes and relationships
                topics = analysis.get("topics", [])
                for topic in topics:
                    topic_query = """
                    MATCH (e:Entry {id: $entry_id})
                    MERGE (t:Topic {name: $topic})
                    CREATE (e)-[:DISCUSSES]->(t)
                    """

                    await session.run(topic_query, {
                        "entry_id": entry_id,
                        "topic": topic
                    })

                logger.info(f"✅ Created knowledge graph entries for {entry_id}")

            except Exception as e:
                logger.error(f"Neo4j entry creation error: {e}")

    async def get_student_insights(self, user_id: str) -> Dict[str, Any]:
        """Get AI insights from knowledge graph"""
        if not self.driver:
            logger.warning("Neo4j not available, returning fallback insights")
            return self._fallback_insights()

        async with self.driver.session() as session:
            try:
                # Get mood trends
                mood_query = """
                MATCH (s:Student {id: $user_id})-[:WROTE]->(e:Entry)
                RETURN avg(e.mood_score) as avg_mood,
                       count(e) as total_entries,
                       collect(e.sentiment) as sentiments
                ORDER BY e.date DESC
                LIMIT 30
                """

                result = await session.run(mood_query, {"user_id": user_id})
                record = await result.single()

                if record:
                    return {
                        "average_mood": record["avg_mood"],
                        "total_entries": record["total_entries"],
                        "recent_sentiments": record["sentiments"]
                    }

                return self._fallback_insights()

            except Exception as e:
                logger.error(f"Neo4j insights error: {e}")
                return self._fallback_insights()

    def _fallback_insights(self) -> Dict[str, Any]:
        """Fallback insights when Neo4j is not available"""
        return {
            "average_mood": 0.5,
            "total_entries": 0,
            "recent_sentiments": []
        }

# Singleton instance
neo4j_service = Neo4jService()
