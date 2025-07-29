"""
Memory systems for the AGNT5 SDK.

Provides various memory implementations for agents including short-term,
long-term, and semantic memory with vector search capabilities.
"""

from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator
from abc import ABC, abstractmethod
import asyncio
import json
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import logging
from collections import OrderedDict

from .types import MemoryEntry, MemoryQuery, Message, MessageRole
from .durable import durable, DurableObject


logger = logging.getLogger(__name__)


class MemoryStore(ABC):
    """
    Abstract base class for memory stores.
    
    Implementations can provide different backends like in-memory,
    database, or vector stores.
    """
    
    @abstractmethod
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an entry to memory."""
        pass
    
    @abstractmethod
    async def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory entry."""
        pass
    
    @abstractmethod
    async def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memory with a query."""
        pass
    
    @abstractmethod
    async def update(self, entry_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a memory entry."""
        pass
    
    @abstractmethod
    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        pass
    
    @abstractmethod
    async def clear(self) -> None:
        """Clear all memory entries."""
        pass
    
    @abstractmethod
    async def size(self) -> int:
        """Get the number of entries in memory."""
        pass


class InMemoryStore(MemoryStore):
    """
    Simple in-memory storage implementation.
    
    Good for development and testing, not suitable for production
    with large amounts of data.
    """
    
    def __init__(self, max_size: Optional[int] = None):
        """Initialize in-memory store."""
        self.max_size = max_size
        self._entries: OrderedDict[str, MemoryEntry] = OrderedDict()
        self._embeddings: Dict[str, List[float]] = {}
    
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an entry to memory."""
        entry = MemoryEntry(
            content=content,
            metadata=metadata or {},
        )
        
        # Enforce max size
        if self.max_size and len(self._entries) >= self.max_size:
            # Remove oldest entry (FIFO)
            oldest_id = next(iter(self._entries))
            await self.delete(oldest_id)
        
        self._entries[entry.id] = entry
        return entry.id
    
    async def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory entry."""
        entry = self._entries.get(entry_id)
        if entry:
            entry.access()
        return entry
    
    async def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memory with a query."""
        results = []
        
        for entry in self._entries.values():
            # Simple text search
            if query.query and isinstance(entry.content, str):
                if query.query.lower() in entry.content.lower():
                    results.append(entry)
            
            # Filter by metadata
            if query.filters:
                match = all(
                    entry.metadata.get(k) == v
                    for k, v in query.filters.items()
                )
                if match and entry not in results:
                    results.append(entry)
        
        # Apply limit
        results = results[:query.limit]
        
        # Mark as accessed
        for entry in results:
            entry.access()
        
        return results
    
    async def update(self, entry_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a memory entry."""
        entry = self._entries.get(entry_id)
        if not entry:
            return False
        
        entry.content = content
        if metadata:
            entry.metadata.update(metadata)
        entry.accessed_at = datetime.utcnow()
        
        return True
    
    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        if entry_id in self._entries:
            del self._entries[entry_id]
            if entry_id in self._embeddings:
                del self._embeddings[entry_id]
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all memory entries."""
        self._entries.clear()
        self._embeddings.clear()
    
    async def size(self) -> int:
        """Get the number of entries in memory."""
        return len(self._entries)


class VectorMemoryStore(InMemoryStore):
    """
    Memory store with vector search capabilities.
    
    Requires an embedding function to convert content to vectors.
    """
    
    def __init__(
        self,
        embedding_fn: Callable[[str], List[float]],
        max_size: Optional[int] = None,
        similarity_metric: str = "cosine",
    ):
        """Initialize vector memory store."""
        super().__init__(max_size)
        self.embedding_fn = embedding_fn
        self.similarity_metric = similarity_metric
    
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an entry with embedding."""
        entry_id = await super().add(content, metadata)
        
        # Generate embedding if content is text
        if isinstance(content, str):
            embedding = await self._get_embedding(content)
            self._embeddings[entry_id] = embedding
            self._entries[entry_id].embedding = embedding
        
        return entry_id
    
    async def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search with vector similarity."""
        if query.embedding:
            # Vector search
            return await self._vector_search(query)
        elif query.query:
            # Convert query to embedding
            query_embedding = await self._get_embedding(query.query)
            query.embedding = query_embedding
            return await self._vector_search(query)
        else:
            # Fallback to regular search
            return await super().search(query)
    
    async def _get_embedding(self, text: str) -> List[float]:
        """Get embedding for text."""
        if asyncio.iscoroutinefunction(self.embedding_fn):
            return await self.embedding_fn(text)
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.embedding_fn, text)
    
    async def _vector_search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Perform vector similarity search."""
        if not query.embedding:
            return []
        
        # Calculate similarities
        similarities = []
        
        for entry_id, embedding in self._embeddings.items():
            similarity = self._calculate_similarity(query.embedding, embedding)
            if similarity >= query.similarity_threshold:
                similarities.append((entry_id, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get entries
        results = []
        for entry_id, similarity in similarities[:query.limit]:
            entry = self._entries.get(entry_id)
            if entry:
                # Add similarity score to metadata
                entry.metadata["similarity_score"] = similarity
                entry.access()
                results.append(entry)
        
        return results
    
    def _calculate_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate similarity between two vectors."""
        if self.similarity_metric == "cosine":
            # Cosine similarity implementation without numpy
            if len(vec1) != len(vec2):
                return 0.0
                
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            norm1 = sum(a * a for a in vec1) ** 0.5
            norm2 = sum(b * b for b in vec2) ** 0.5
            
            if norm1 == 0 or norm2 == 0:
                return 0.0
            
            return float(dot_product / (norm1 * norm2))
        else:
            # Default to cosine
            return self._calculate_similarity(vec1, vec2)


class Memory:
    """
    High-level memory interface for agents.
    
    Combines different memory types and provides a unified interface.
    
    Example:
        ```python
        from agnt5 import Memory
        
        # Create memory with custom store
        memory = Memory(
            store=VectorMemoryStore(embedding_fn=my_embed_fn),
            retention_days=30,
        )
        
        # Add memories
        await memory.add("User's name is Alice")
        await memory.add({"event": "user_login", "user": "alice"})
        
        # Search memories
        results = await memory.search("What is the user's name?")
        
        # Get recent memories
        recent = await memory.get_recent(limit=10)
        ```
    """
    
    def __init__(
        self,
        store: Optional[MemoryStore] = None,
        retention_days: Optional[int] = None,
        auto_summarize: bool = False,
        summarize_threshold: int = 100,
    ):
        """Initialize memory."""
        self.store = store or InMemoryStore()
        self.retention_days = retention_days
        self.auto_summarize = auto_summarize
        self.summarize_threshold = summarize_threshold
        
        # Message history for agents
        self._message_history: List[Message] = []
    
    async def add(self, content: Union[Any, Message]) -> str:
        """Add content to memory."""
        # Handle messages specially
        if isinstance(content, Message):
            self._message_history.append(content)
            
            # Store message content
            metadata = {
                "type": "message",
                "role": content.role.value,
                "timestamp": content.timestamp.isoformat(),
            }
            if content.name:
                metadata["name"] = content.name
            
            return await self.store.add(content.content, metadata)
        
        # Regular content
        return await self.store.add(content)
    
    async def search(
        self,
        query: Union[str, MemoryQuery],
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """Search memory."""
        if isinstance(query, str):
            query = MemoryQuery(query=query, limit=limit)
        else:
            query.limit = limit
        
        return await self.store.search(query)
    
    async def get_recent(
        self,
        limit: int = 10,
        content_type: Optional[str] = None,
    ) -> List[MemoryEntry]:
        """Get recent memories."""
        query = MemoryQuery(limit=limit)
        
        if content_type:
            query.filters["type"] = content_type
        
        # Get all entries and sort by access time
        all_entries = []
        size = await self.store.size()
        
        # This is inefficient for large stores, but works for the interface
        results = await self.store.search(MemoryQuery(limit=size))
        
        # Sort by accessed_at
        results.sort(key=lambda e: e.accessed_at, reverse=True)
        
        return results[:limit]
    
    async def get_messages(
        self,
        limit: Optional[int] = None,
        role: Optional[MessageRole] = None,
    ) -> List[Message]:
        """Get message history."""
        messages = self._message_history
        
        if role:
            messages = [m for m in messages if m.role == role]
        
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    async def forget_old(self) -> int:
        """Remove old memories based on retention policy."""
        if not self.retention_days:
            return 0
        
        cutoff = datetime.utcnow() - timedelta(days=self.retention_days)
        deleted = 0
        
        # Get all entries (inefficient, but works for the interface)
        size = await self.store.size()
        all_entries = await self.store.search(MemoryQuery(limit=size))
        
        for entry in all_entries:
            if entry.accessed_at < cutoff:
                if await self.store.delete(entry.id):
                    deleted += 1
        
        return deleted
    
    async def summarize(self) -> Optional[str]:
        """
        Summarize memory contents.
        
        This is a placeholder - actual implementation would use
        an LLM to generate summaries.
        """
        size = await self.store.size()
        
        if size < self.summarize_threshold:
            return None
        
        # TODO: Implement actual summarization
        return f"Memory contains {size} entries"
    
    async def clear(self) -> None:
        """Clear all memories."""
        await self.store.clear()
        self._message_history.clear()
    
    async def export(self) -> Dict[str, Any]:
        """Export memory contents."""
        size = await self.store.size()
        all_entries = await self.store.search(MemoryQuery(limit=size))
        
        return {
            "entries": [
                {
                    "id": entry.id,
                    "content": entry.content,
                    "metadata": entry.metadata,
                    "created_at": entry.created_at.isoformat(),
                    "accessed_at": entry.accessed_at.isoformat(),
                    "access_count": entry.access_count,
                }
                for entry in all_entries
            ],
            "messages": [
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "name": msg.name,
                    "timestamp": msg.timestamp.isoformat(),
                }
                for msg in self._message_history
            ],
        }
    
    async def import_data(self, data: Dict[str, Any]) -> None:
        """Import memory contents."""
        # Clear existing data
        await self.clear()
        
        # Import entries
        for entry_data in data.get("entries", []):
            await self.store.add(
                entry_data["content"],
                entry_data.get("metadata", {}),
            )
        
        # Import messages
        for msg_data in data.get("messages", []):
            msg = Message(
                role=MessageRole(msg_data["role"]),
                content=msg_data["content"],
                name=msg_data.get("name"),
            )
            self._message_history.append(msg)


@durable.object  
class DurableMemoryStore(DurableObject):
    """
    Durable memory store that persists memories across restarts.
    
    This provides a durable, persistent memory system that:
    - Automatically persists all memory entries
    - Survives process restarts and failures
    - Provides efficient search and retrieval
    - Integrates seamlessly with agents and workflows
    """
    
    def __init__(self, memory_id: str):
        """Initialize a durable memory store."""
        super().__init__(memory_id)
        self.memory_id = memory_id
        self.entries: Dict[str, MemoryEntry] = {}
        self.entry_counter = 0
    
    async def add(self, content: Any, metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add an entry to durable memory."""
        entry_id = f"mem_{self.memory_id}_{self.entry_counter}"
        self.entry_counter += 1
        
        entry = MemoryEntry(
            id=entry_id,
            content=content,
            metadata=metadata or {},
        )
        
        self.entries[entry_id] = entry
        await self.save()  # Persist to durable storage
        
        logger.debug(f"Added memory entry {entry_id} to durable store {self.memory_id}")
        return entry_id
    
    async def get(self, entry_id: str) -> Optional[MemoryEntry]:
        """Get a specific memory entry from durable storage."""
        return self.entries.get(entry_id)
    
    async def search(self, query: MemoryQuery) -> List[MemoryEntry]:
        """Search memory with a query."""
        results = []
        
        for entry in self.entries.values():
            # Simple text-based search
            if query.query:
                content_str = str(entry.content).lower()
                if query.query.lower() in content_str:
                    results.append(entry)
                    continue
            
            # Metadata filtering
            if query.filters:
                matches_metadata = all(
                    entry.metadata.get(key) == value
                    for key, value in query.filters.items()
                )
                if matches_metadata:
                    results.append(entry)
                    continue
        
        # Sort by relevance/timestamp
        results.sort(key=lambda x: x.accessed_at, reverse=True)
        
        # Apply limit
        if query.limit:
            results = results[:query.limit]
        
        return results
    
    async def update(self, entry_id: str, content: Any, metadata: Optional[Dict[str, Any]] = None) -> bool:
        """Update a memory entry in durable storage."""
        if entry_id not in self.entries:
            return False
        
        entry = self.entries[entry_id]
        entry.content = content
        if metadata:
            entry.metadata.update(metadata)
        entry.access()  # Update access time
        
        await self.save()  # Persist changes
        logger.debug(f"Updated memory entry {entry_id} in durable store {self.memory_id}")
        return True
    
    async def delete(self, entry_id: str) -> bool:
        """Delete a memory entry from durable storage."""
        if entry_id in self.entries:
            del self.entries[entry_id]
            await self.save()  # Persist changes
            logger.debug(f"Deleted memory entry {entry_id} from durable store {self.memory_id}")
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all memory entries."""
        self.entries.clear()
        self.entry_counter = 0
        await self.save()
        logger.debug(f"Cleared all entries from durable store {self.memory_id}")
    
    async def size(self) -> int:
        """Get the number of entries in memory."""
        return len(self.entries)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory store statistics."""
        total_entries = len(self.entries)
        memory_types = {}
        
        for entry in self.entries.values():
            memory_type = entry.metadata.get("type", "unknown")
            memory_types[memory_type] = memory_types.get(memory_type, 0) + 1
        
        oldest_entry = min(self.entries.values(), key=lambda x: x.created_at) if self.entries else None
        newest_entry = max(self.entries.values(), key=lambda x: x.created_at) if self.entries else None
        
        return {
            "memory_id": self.memory_id,
            "total_entries": total_entries,
            "memory_types": memory_types,
            "oldest_entry": oldest_entry.created_at.isoformat() if oldest_entry else None,
            "newest_entry": newest_entry.created_at.isoformat() if newest_entry else None,
            "version": self._version,
            "last_saved": self._last_saved.isoformat(),
        }
    
    async def _get_state(self) -> Dict[str, Any]:
        """Get memory store state for durable persistence."""
        base_state = await super()._get_state()
        
        # Serialize entries
        serialized_entries = {}
        for entry_id, entry in self.entries.items():
            serialized_entries[entry_id] = {
                "id": entry.id,
                "content": entry.content,
                "metadata": entry.metadata,
                "created_at": entry.created_at.isoformat(),
                "accessed_at": entry.accessed_at.isoformat(),
                "access_count": entry.access_count,
            }
        
        memory_state = {
            "memory_id": self.memory_id,
            "entries": serialized_entries,
            "entry_counter": self.entry_counter,
        }
        
        return {**base_state, **memory_state}
    
    async def _restore_state(self, state: Dict[str, Any]) -> None:
        """Restore memory store state from durable persistence."""
        await super()._restore_state(state)
        
        self.memory_id = state.get("memory_id", self.object_id)
        self.entry_counter = state.get("entry_counter", 0)
        
        # Restore entries
        self.entries = {}
        for entry_id, entry_data in state.get("entries", {}).items():
            entry = MemoryEntry(
                id=entry_data["id"],
                content=entry_data["content"],
                metadata=entry_data["metadata"],
            )
            # Restore timestamps and access count
            entry.created_at = datetime.fromisoformat(entry_data["created_at"])
            entry.accessed_at = datetime.fromisoformat(entry_data["accessed_at"])
            entry.access_count = entry_data["access_count"]
            
            self.entries[entry_id] = entry
        
        logger.info(f"Restored durable memory store {self.memory_id} with {len(self.entries)} entries")


class DurableMemory(Memory):
    """
    Enhanced durable memory interface that uses durable storage by default.
    
    This provides a seamless upgrade path for agents to use durable memory
    while maintaining backward compatibility with the Memory interface.
    """
    
    def __init__(
        self,
        memory_id: Optional[str] = None,
        retention_days: Optional[int] = None,
        auto_summarize: bool = False,
        summarize_threshold: int = 100,
    ):
        """Initialize durable memory."""
        import uuid
        self._memory_id = memory_id or str(uuid.uuid4())
        self._durable_store = None
        
        # Don't call super().__init__ yet - we'll set up the store first
        self.retention_days = retention_days
        self.auto_summarize = auto_summarize
        self.summarize_threshold = summarize_threshold
        self._message_history: List[Message] = []
    
    async def _ensure_durable_store(self) -> DurableMemoryStore:
        """Ensure durable store is initialized."""
        if self._durable_store is None:
            self._durable_store = await DurableMemoryStore.get_or_create(self._memory_id)
        return self._durable_store
    
    async def add(self, content: Union[Any, Message]) -> str:
        """Add content to durable memory."""
        store = await self._ensure_durable_store()
        
        # Handle messages specially
        if isinstance(content, Message):
            self._message_history.append(content)
            
            # Store message content with enhanced metadata
            metadata = {
                "type": "message",
                "role": content.role.value,
                "timestamp": content.timestamp.isoformat(),
                "message_id": getattr(content, 'id', None),
            }
            if content.name:
                metadata["name"] = content.name
            if hasattr(content, 'tool_calls') and content.tool_calls:
                metadata["has_tool_calls"] = True
                metadata["tool_count"] = len(content.tool_calls)
            
            return await store.add(content.content, metadata)
        
        # Regular content
        return await store.add(content)
    
    async def search(
        self,
        query: Union[str, MemoryQuery],
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """Search durable memory."""
        store = await self._ensure_durable_store()
        
        if isinstance(query, str):
            query = MemoryQuery(query=query, limit=limit)
        else:
            query.limit = limit
        
        return await store.search(query)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive memory statistics."""
        store = await self._ensure_durable_store()
        return await store.get_stats()
    
    async def clear(self) -> None:
        """Clear all durable memories."""
        store = await self._ensure_durable_store()
        await store.clear()
        self._message_history.clear()
    
    @property
    def memory_id(self) -> str:
        """Get the memory ID."""
        return self._memory_id
    
    @property
    def is_durable(self) -> bool:
        """Always returns True for durable memory."""
        return True
    
    @classmethod
    async def create(cls, memory_id: Optional[str] = None) -> "DurableMemory":
        """Create and initialize a durable memory instance."""
        memory = cls(memory_id=memory_id)
        await memory._ensure_durable_store()  # Initialize immediately
        return memory