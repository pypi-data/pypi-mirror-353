"""
CustomerSession - Durable Object for persistent customer state

Maintains conversation history, preferences, and session state across interactions.
Demonstrates durable object patterns with serialized access and state persistence.
"""

import asyncio
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from agnt5.durable import durable, DurableObject


@dataclass
class Message:
    """Message structure for conversation history."""
    timestamp: float
    role: str  # user, assistant, system
    content: str
    agent: Optional[str] = None
    metadata: Dict[str, Any] = None


@dataclass
class CustomerPreferences:
    """Customer preferences and settings."""
    preferred_agent: Optional[str] = None
    communication_style: str = "professional"  # casual, professional, technical
    language: str = "en"
    timezone: str = "UTC"
    notification_preferences: Dict[str, bool] = None
    
    def __post_init__(self):
        if self.notification_preferences is None:
            self.notification_preferences = {
                "email": True,
                "sms": False,
                "push": True
            }


@dataclass
class SessionMetrics:
    """Session-level metrics and analytics."""
    total_interactions: int = 0
    total_duration: float = 0.0
    satisfaction_scores: List[int] = None
    escalations: int = 0
    resolutions: int = 0
    last_activity: Optional[float] = None
    
    def __post_init__(self):
        if self.satisfaction_scores is None:
            self.satisfaction_scores = []


@durable.object
class CustomerSession(DurableObject):
    """
    Durable customer session object with persistent state.
    
    Maintains conversation history, preferences, and session metrics
    with automatic serialization and cross-restart persistence.
    """
    
    def __init__(self, customer_id: str):
        super().__init__()
        self.customer_id = customer_id
        self.session_id = f"sess_{customer_id}_{int(time.time())}"
        self.created_at = time.time()
        self.last_accessed = time.time()
        
        # Core session data
        self.conversation_history: List[Message] = []
        self.preferences = CustomerPreferences()
        self.metrics = SessionMetrics()
        
        # Current session state
        self.current_agent: Optional[str] = None
        self.active_tickets: List[str] = []
        self.pending_actions: List[Dict[str, Any]] = []
        self.context_variables: Dict[str, Any] = {}
        
        # Session flags
        self.is_active = True
        self.requires_human_intervention = False
        self.escalation_level = 0  # 0=normal, 1=supervisor, 2=manager
        
        print(f"🔄 Created customer session {self.session_id}")
    
    async def add_message(self, role: str, content: str, agent: str = None, metadata: Dict[str, Any] = None) -> None:
        """Add a message to the conversation history."""
        message = Message(
            timestamp=time.time(),
            role=role,
            content=content,
            agent=agent,
            metadata=metadata or {}
        )
        
        self.conversation_history.append(message)
        self.last_accessed = time.time()
        self.metrics.total_interactions += 1
        self.metrics.last_activity = time.time()
        
        # Update current agent if this is an assistant message
        if role == "assistant" and agent:
            self.current_agent = agent
        
        # Trim history if it gets too long (keep last 100 messages)
        if len(self.conversation_history) > 100:
            self.conversation_history = self.conversation_history[-100:]
        
        await self.save()
        print(f"💬 Added {role} message to session {self.session_id}")
    
    async def update_preferences(self, preferences: Dict[str, Any]) -> None:
        """Update customer preferences."""
        for key, value in preferences.items():
            if hasattr(self.preferences, key):
                setattr(self.preferences, key, value)
        
        self.last_accessed = time.time()
        await self.save()
        print(f"⚙️ Updated preferences for session {self.session_id}")
    
    async def set_context_variable(self, key: str, value: Any) -> None:
        """Set a context variable for the session."""
        self.context_variables[key] = value
        self.last_accessed = time.time()
        await self.save()
    
    async def get_context_variable(self, key: str, default: Any = None) -> Any:
        """Get a context variable from the session."""
        self.last_accessed = time.time()
        return self.context_variables.get(key, default)
    
    async def add_ticket(self, ticket_id: str) -> None:
        """Add a support ticket to the session."""
        if ticket_id not in self.active_tickets:
            self.active_tickets.append(ticket_id)
            self.last_accessed = time.time()
            await self.save()
            print(f"🎫 Added ticket {ticket_id} to session {self.session_id}")
    
    async def resolve_ticket(self, ticket_id: str) -> bool:
        """Mark a ticket as resolved and remove from active list."""
        if ticket_id in self.active_tickets:
            self.active_tickets.remove(ticket_id)
            self.metrics.resolutions += 1
            self.last_accessed = time.time()
            await self.save()
            print(f"✅ Resolved ticket {ticket_id} in session {self.session_id}")
            return True
        return False
    
    async def escalate_session(self, reason: str, target_level: int = None) -> None:
        """Escalate the session to a higher support level."""
        if target_level is None:
            self.escalation_level += 1
        else:
            self.escalation_level = target_level
        
        self.metrics.escalations += 1
        self.requires_human_intervention = True
        
        # Add escalation to pending actions
        self.pending_actions.append({
            "type": "escalation",
            "reason": reason,
            "level": self.escalation_level,
            "timestamp": time.time()
        })
        
        self.last_accessed = time.time()
        await self.save()
        print(f"⚡ Escalated session {self.session_id} to level {self.escalation_level}")
    
    async def add_satisfaction_score(self, score: int) -> None:
        """Add a customer satisfaction score (1-5)."""
        if 1 <= score <= 5:
            self.metrics.satisfaction_scores.append(score)
            self.last_accessed = time.time()
            await self.save()
            print(f"⭐ Added satisfaction score {score} to session {self.session_id}")
    
    async def get_recent_messages(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent messages from conversation history."""
        self.last_accessed = time.time()
        recent = self.conversation_history[-count:] if count > 0 else self.conversation_history
        return [asdict(msg) for msg in recent]
    
    async def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation and session state."""
        self.last_accessed = time.time()
        
        # Calculate session duration
        duration = time.time() - self.created_at
        self.metrics.total_duration = duration
        
        # Calculate average satisfaction
        avg_satisfaction = None
        if self.metrics.satisfaction_scores:
            avg_satisfaction = sum(self.metrics.satisfaction_scores) / len(self.metrics.satisfaction_scores)
        
        return {
            "session_id": self.session_id,
            "customer_id": self.customer_id,
            "created_at": self.created_at,
            "duration": duration,
            "message_count": len(self.conversation_history),
            "current_agent": self.current_agent,
            "active_tickets": len(self.active_tickets),
            "escalation_level": self.escalation_level,
            "requires_human_intervention": self.requires_human_intervention,
            "total_interactions": self.metrics.total_interactions,
            "resolutions": self.metrics.resolutions,
            "escalations": self.metrics.escalations,
            "average_satisfaction": avg_satisfaction,
            "is_active": self.is_active
        }
    
    async def handoff_to_agent(self, from_agent: str, to_agent: str, reason: str) -> None:
        """Handle agent handoff with context preservation."""
        handoff_message = f"Session handed off from {from_agent} to {to_agent}. Reason: {reason}"
        
        await self.add_message(
            role="system",
            content=handoff_message,
            metadata={
                "type": "handoff",
                "from_agent": from_agent,
                "to_agent": to_agent,
                "reason": reason
            }
        )
        
        self.current_agent = to_agent
        self.pending_actions.append({
            "type": "handoff",
            "from_agent": from_agent,
            "to_agent": to_agent,
            "reason": reason,
            "timestamp": time.time()
        })
        
        await self.save()
        print(f"🔄 Handed off session {self.session_id} from {from_agent} to {to_agent}")
    
    async def close_session(self, reason: str = "completed") -> Dict[str, Any]:
        """Close the session and return final summary."""
        self.is_active = False
        final_duration = time.time() - self.created_at
        self.metrics.total_duration = final_duration
        
        await self.add_message(
            role="system",
            content=f"Session closed. Reason: {reason}",
            metadata={"type": "session_close", "reason": reason}
        )
        
        summary = await self.get_conversation_summary()
        await self.save()
        
        print(f"🔚 Closed session {self.session_id} after {final_duration:.1f}s")
        return summary
    
    async def get_state_size(self) -> Dict[str, int]:
        """Get the size of different state components for monitoring."""
        import sys
        
        return {
            "conversation_history_items": len(self.conversation_history),
            "active_tickets": len(self.active_tickets),
            "pending_actions": len(self.pending_actions),
            "context_variables": len(self.context_variables),
            "satisfaction_scores": len(self.metrics.satisfaction_scores),
            "estimated_memory_bytes": sys.getsizeof(self.__dict__)
        }


# Example usage and testing
async def main():
    """Test the CustomerSession durable object."""
    
    print("🧪 Testing CustomerSession Durable Object")
    print("=" * 50)
    
    # Create a new customer session
    session = CustomerSession("cust_001")
    
    # Simulate a conversation
    await session.add_message("user", "Hi, I need help with my order")
    await session.add_message("assistant", "I'd be happy to help! Can you provide your order number?", "customer_service")
    await session.add_message("user", "It's ORD_12345")
    await session.add_message("assistant", "Let me look that up for you...", "customer_service")
    
    # Add a support ticket
    await session.add_ticket("TICK_001")
    
    # Update preferences
    await session.update_preferences({
        "preferred_agent": "customer_service",
        "communication_style": "casual"
    })
    
    # Set some context variables
    await session.set_context_variable("order_id", "ORD_12345")
    await session.set_context_variable("issue_type", "shipping")
    
    # Escalate the session
    await session.escalate_session("Complex shipping issue requires manager approval")
    
    # Add satisfaction score
    await session.add_satisfaction_score(4)
    
    # Handoff to technical support
    await session.handoff_to_agent("customer_service", "technical_support", "Needs technical investigation")
    
    # Get conversation summary
    summary = await session.get_conversation_summary()
    print("\n📊 Session Summary:")
    for key, value in summary.items():
        print(f"   {key}: {value}")
    
    # Get recent messages
    recent = await session.get_recent_messages(3)
    print(f"\n💬 Recent Messages ({len(recent)}):")
    for msg in recent:
        print(f"   [{msg['role']}] {msg['content'][:50]}...")
    
    # Get state size info
    state_size = await session.get_state_size()
    print(f"\n📈 State Size:")
    for key, value in state_size.items():
        print(f"   {key}: {value}")
    
    # Test persistence simulation
    print(f"\n🔄 Simulating persistence...")
    await session.save()
    
    # Close the session
    final_summary = await session.close_session("Customer issue resolved")
    print(f"\n✅ Final Summary:")
    for key, value in final_summary.items():
        print(f"   {key}: {value}")


if __name__ == "__main__":
    asyncio.run(main())