"""
memory/memory_manager.py
Long-term memory using ChromaDB (local vector database).
Stores past conversations and facts as embeddings for semantic search.
"""

import os
import uuid
from datetime import datetime
from core.logger import get_logger

logger = get_logger(__name__)

MEMORY_DIR = os.path.join(os.path.dirname(__file__), "..", "memory", "db")


class MemoryManager:
    def __init__(self):
        try:
            import chromadb
            from chromadb.utils import embedding_functions

            self._client = chromadb.PersistentClient(path=MEMORY_DIR)
            ef = embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name="all-MiniLM-L6-v2"
            )
            self._collection = self._client.get_or_create_collection(
                name="jarvis_memory",
                embedding_function=ef,
            )
            logger.info(f"Memory loaded — {self._collection.count()} entries.")
            self._available = True
        except ImportError:
            logger.warning("chromadb not installed — memory disabled. Run: pip install chromadb sentence-transformers")
            self._available = False

    def add(self, text: str, metadata: dict = None):
        """Store a piece of text in long-term memory."""
        if not self._available:
            return
        try:
            meta = {"timestamp": datetime.utcnow().isoformat()}
            if metadata:
                meta.update(metadata)
            self._collection.add(
                documents=[text],
                metadatas=[meta],
                ids=[str(uuid.uuid4())],
            )
        except Exception as e:
            logger.error(f"Memory add error: {e}")

    def search(self, query: str, top_k: int = 3) -> list:
        """Return the most relevant memories for a query."""
        if not self._available or self._collection.count() == 0:
            return []
        try:
            results = self._collection.query(
                query_texts=[query],
                n_results=min(top_k, self._collection.count()),
            )
            docs = results.get("documents", [[]])[0]
            metas = results.get("metadatas", [[]])[0]
            return [{"text": d, "meta": m} for d, m in zip(docs, metas)]
        except Exception as e:
            logger.error(f"Memory search error: {e}")
            return []

    def clear(self):
        """Wipe all memories (use with caution)."""
        if not self._available:
            return
        self._client.delete_collection("jarvis_memory")
        self._collection = self._client.create_collection("jarvis_memory")
        logger.info("Memory cleared.")
