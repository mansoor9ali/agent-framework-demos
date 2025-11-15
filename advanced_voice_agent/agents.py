"""Specialist agent helpers for the advanced voice system."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, AsyncIterator

from agent_framework import ChatAgent

from .memory import PersistentThreadStore, STATE_DIR


@dataclass
class SpecialistAgent:
    """Wrap a chat agent with its own persisted thread."""

    key: str
    agent: ChatAgent
    store: PersistentThreadStore
    thread: Any
    message_number: int = 0

    async def stream(self, text: str) -> AsyncIterator[object]:
        async for chunk in self.agent.run_stream(text, thread=self.thread):
            yield chunk
        self.message_number += 1
        await self.store.persist(self.thread, self.message_number)


async def create_specialist(
    key: str,
    agent: ChatAgent,
    *,
    store_suffix: str,
) -> SpecialistAgent:
    store = PersistentThreadStore(STATE_DIR / f"{store_suffix}_thread.json")
    thread, message_number = await store.restore(agent)
    return SpecialistAgent(key=key, agent=agent, store=store, thread=thread, message_number=message_number)


def extract_agent_key(response_text: str, default: str = "general") -> str:
    """Parse triage agent output for target agent key."""

    if not response_text:
        return default
    start = response_text.find("{")
    end = response_text.rfind("}")
    if start == -1 or end == -1:
        return default
    try:
        data = json.loads(response_text[start : end + 1])
        agent_key = str(data.get("agent", "")).strip().lower()
        return agent_key or default
    except Exception:
        return default
