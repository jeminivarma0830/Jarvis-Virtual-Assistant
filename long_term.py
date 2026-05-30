"""
memory/long_term.py  –  Vector-based long-term memory using ChromaDB
"""
import logging
import chromadb
from chromadb.utils import embedding_functions
from config.settings import MEMORY_DB_PATH, MEMORY_COLLECTION, MAX_MEMORY_RESULTS

logger = logging.getLogger(__name__)


class Memory:
    """Stores and retrieves conversation facts using semantic search."""

    def __init__(self):
        self._client = chromadb.PersistentClient(path=MEMORY_DB_PATH)
        emb_fn = embedding_functions.DefaultEmbeddingFunction()
        self._col = self._client.get_or_create_collection(
            name=MEMORY_COLLECTION,
            embedding_function=emb_fn,
        )
        self._counter = self._col.count()
        logger.info(f"Memory loaded: {self._counter} entries in '{MEMORY_COLLECTION}'")

    def store(self, user_msg: str, assistant_reply: str):
        """Save a user↔JARVIS exchange as a memory entry."""
        doc = f"User: {user_msg}\nJARVIS: {assistant_reply}"
        uid = f"mem_{self._counter}"
        self._col.add(documents=[doc], ids=[uid])
        self._counter += 1

    def recall(self, query: str, n: int = MAX_MEMORY_RESULTS) -> list[str]:
        """Return the most relevant past memories for a query."""
        if self._col.count() == 0:
            return []
        results = self._col.query(query_texts=[query], n_results=min(n, self._col.count()))
        return results["documents"][0] if results["documents"] else []

    def clear(self):
        """Wipe all stored memories."""
        self._client.delete_collection(MEMORY_COLLECTION)
        self._col = self._client.get_or_create_collection(MEMORY_COLLECTION)
        self._counter = 0
        logger.info("All memories cleared.")
