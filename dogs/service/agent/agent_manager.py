from typing import Dict, Optional, Any, List
import asyncio
from datetime import datetime
from dataclasses import dataclass
from discord import Client

@dataclass
class AgentState:
    context_interaction_count: int
    last_message_time: datetime
    last_human_message_time: datetime
    last_message_sent_time: datetime
    post_attempt: Optional[Dict[str, Any]]
    mutex: asyncio.Lock

class AgentManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AgentManager, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.agents: Dict[str, Dict[str, Any]] = {}
            self._initialized = True

    def register_agent(self, id: str, client: Client, replier: Any) -> None:
        """Register a new agent with the manager."""
        self.agents[id] = {
            'client': client,
            'replier': replier,
            'state': AgentState(
                context_interaction_count=0,
                last_message_time=datetime.min,
                last_human_message_time=datetime.min,
                last_message_sent_time=datetime.min,
                post_attempt=None,
                mutex=asyncio.Lock()
            )
        }

    def get_agent(self, id: str) -> Optional[Dict[str, Any]]:
        """Get an agent by ID."""
        return self.agents.get(id)

    def get_all_agents(self) -> List[Dict[str, Any]]:
        """Get all registered agents."""
        return list(self.agents.values())

    async def update_agent_state(self, id: str, updates: Dict[str, Any]) -> None:
        """Update an agent's state with the provided updates."""
        agent = self.agents.get(id)
        if not agent:
            return

        print(f"Updating state for agent {id}")
        async with agent['state'].mutex:
            for key, value in updates.items():
                setattr(agent['state'], key, value)
        print(f"Updated state for agent {id}")

    async def get_agent_state(self, id: str) -> Optional[AgentState]:
        """Get an agent's current state."""
        agent = self.agents.get(id)
        if not agent:
            return None

        async with agent['state'].mutex:
            return agent['state']