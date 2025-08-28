"""Pinecone vector database service"""

import os
import logging
from typing import List, Dict, Any
import uuid

logger = logging.getLogger(__name__)

class PineconeService:
    def __init__(self):
        self.api_key = os.getenv("PINECONE_API_KEY")
        self.environment = os.getenv("PINECONE_ENVIRONMENT", "us-east-1-aws")
        self.index_name = os.getenv("PINECONE_INDEX_NAME", "student-diary-vectors")

        if not self.api_key:
            logger.warning("Pinecone API key not found")
            self.index = None
        else:
            try:
                import pinecone
                pinecone.init(api_key=self.api_key, environment=self.environment)
                self.index = pinecone.Index(self.index_name)
                logger.info("✅ Pinecone initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize Pinecone: {e}")
                self.index = None

    async def store_entry_embedding(self, entry_id: str, embedding: List[float], metadata: Dict[str, Any]):
        """Store diary entry embedding in Pinecone"""
        if not self.index:
            logger.warning("Pinecone not available, skipping embedding storage")
            return

        try:
            self.index.upsert([
                (entry_id, embedding, metadata)
            ])
            logger.info(f"✅ Stored embedding for entry {entry_id}")
        except Exception as e:
            logger.error(f"Pinecone storage error: {e}")

    async def find_similar_entries(self, query_embedding: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """Find similar diary entries based on embedding"""
        if not self.index:
            logger.warning("Pinecone not available, returning empty results")
            return []

        try:
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                include_metadata=True
            )

            similar_entries = []
            for match in results.matches:
                similar_entries.append({
                    "entry_id": match.id,
                    "similarity_score": match.score,
                    "metadata": match.metadata
                })

            return similar_entries

        except Exception as e:
            logger.error(f"Pinecone query error: {e}")
            return []

    async def get_positive_memories(self, user_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get positive memories for reflection generation"""
        if not self.index:
            logger.warning("Pinecone not available, returning fallback memories")
            return self._fallback_memories()

        try:
            # Query for positive entries from this user
            results = self.index.query(
                filter={"user_id": user_id, "sentiment": "positive"},
                top_k=limit,
                include_metadata=True
            )

            memories = []
            for match in results.matches:
                memories.append({
                    "content": match.metadata.get("content_preview", ""),
                    "date": match.metadata.get("date", ""),
                    "mood_score": match.metadata.get("mood_score", 0.5)
                })

            return memories

        except Exception as e:
            logger.error(f"Memory retrieval error: {e}")
            return self._fallback_memories()

    def _fallback_memories(self) -> List[Dict[str, Any]]:
        """Fallback memories when Pinecone is not available"""
        return [
            {
                "content": "Today was a good day at school. I understood the math lesson perfectly!",
                "date": "2025-08-25",
                "mood_score": 0.8
            }
        ]

# Singleton instance  
pinecone_service = PineconeService()
