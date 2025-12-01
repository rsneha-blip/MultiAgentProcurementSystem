"""
Agent Communication Framework - True Agentic Messaging

Enables autonomous agents to communicate with each other without
central orchestration.
"""
import asyncio
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime
import json
import uuid
from enum import Enum

class MessageType(Enum):
    """Types of inter-agent messages."""
    REQUEST = "request"
    RESPONSE = "response"  
    NOTIFICATION = "notification"
    ERROR = "error"

@dataclass
class AgentMessage:
    """Message passed between agents."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    from_agent: str = ""
    to_agent: str = ""
    message_type: MessageType = MessageType.REQUEST
    content: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    conversation_id: str = ""
    requires_response: bool = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary for serialization."""
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type.value,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "conversation_id": self.conversation_id,
            "requires_response": self.requires_response
        }

class MessageBus:
    """Central message bus for agent communication."""
    
    def __init__(self):
        self.agents: Dict[str, 'BaseAgentV2'] = {}
        self.message_history: List[AgentMessage] = []
        self.active_conversations: Dict[str, List[AgentMessage]] = {}
    
    def register_agent(self, agent: 'BaseAgentV2'):
        """Register an agent with the message bus."""
        self.agents[agent.agent_id] = agent
        agent.message_bus = self
    
    async def send_message(self, message: AgentMessage):
        """Route message to target agent."""
        print(f"📨 MESSAGE: {message.from_agent} → {message.to_agent} | {message.message_type.value}")
        print(f"   Content: {message.content.get('summary', str(message.content)[:100])}")
        
        # Store message history
        self.message_history.append(message)
        
        # Track conversation
        conv_id = message.conversation_id
        if conv_id not in self.active_conversations:
            self.active_conversations[conv_id] = []
        self.active_conversations[conv_id].append(message)
        
        # Route to target agent
        target_agent = self.agents.get(message.to_agent)
        if target_agent:
            await target_agent.receive_message(message)
        else:
            print(f"❌ Agent {message.to_agent} not found")
    
    def get_conversation_history(self, conversation_id: str) -> List[AgentMessage]:
        """Get all messages in a conversation."""
        return self.active_conversations.get(conversation_id, [])

# Global message bus instance
_message_bus = None

def get_message_bus() -> MessageBus:
    """Get global message bus instance."""
    global _message_bus
    if _message_bus is None:
        _message_bus = MessageBus()
    return _message_bus


class BaseAgentV2:
    """Base class for autonomous agents with communication capabilities."""
    
    def __init__(self, agent_id: str, agent_type: str):
        self.agent_id = agent_id
        self.agent_type = agent_type
        self.message_bus: Optional[MessageBus] = None
        self.capabilities = []
        self.current_conversations = {}
        
    async def send_message(self, to_agent: str, content: Dict[str, Any], 
                          message_type: MessageType = MessageType.REQUEST,
                          conversation_id: str = None) -> str:
        """Send message to another agent."""
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            
        message = AgentMessage(
            from_agent=self.agent_id,
            to_agent=to_agent,
            message_type=message_type,
            content=content,
            conversation_id=conversation_id
        )
        
        if self.message_bus:
            await self.message_bus.send_message(message)
        
        return message.id
    
    async def receive_message(self, message: AgentMessage):
        """Receive and process message from another agent."""
        print(f"🤖 {self.agent_id} received message: {message.message_type.value}")
        
        try:
            # Route to appropriate handler
            if message.message_type == MessageType.REQUEST:
                await self.handle_request(message)
            elif message.message_type == MessageType.RESPONSE:
                await self.handle_response(message)
            elif message.message_type == MessageType.NOTIFICATION:
                await self.handle_notification(message)
            elif message.message_type == MessageType.ERROR:
                await self.handle_error(message)
                
        except Exception as e:
            # Send error response
            await self.send_error_response(message, str(e))
    
    async def handle_request(self, message: AgentMessage):
        """Handle incoming request - override in subclasses."""
        raise NotImplementedError(f"Agent {self.agent_id} must implement handle_request")
    
    async def handle_response(self, message: AgentMessage):
        """Handle incoming response - override in subclasses."""
        print(f"📨 {self.agent_id} received response: {message.content}")
    
    async def handle_notification(self, message: AgentMessage):
        """Handle incoming notification - override in subclasses."""
        print(f"🔔 {self.agent_id} received notification: {message.content}")
    
    async def handle_error(self, message: AgentMessage):
        """Handle incoming error - override in subclasses."""
        print(f"❌ {self.agent_id} received error: {message.content}")
    
    async def send_error_response(self, original_message: AgentMessage, error: str):
        """Send error response to original sender."""
        await self.send_message(
            to_agent=original_message.from_agent,
            content={"error": error, "original_message_id": original_message.id},
            message_type=MessageType.ERROR,
            conversation_id=original_message.conversation_id
        )
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status."""
        return {
            "agent_id": self.agent_id,
            "agent_type": self.agent_type,
            "capabilities": self.capabilities,
            "active_conversations": len(self.current_conversations),
            "status": "active"
        }