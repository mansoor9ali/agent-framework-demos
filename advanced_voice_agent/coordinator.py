"""Multi-agent coordinator for advanced voice system."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import AsyncIterator

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
from openai import OpenAI

from .memory import LongTermMemory, PersistentThreadStore
from .tools import ToolRegistry


@dataclass
class CoordinatorConfig:
    instructions: str = (
        "You are the primary conversational agent. "
        "Use tools, MCP capabilities, and long-term memory to provide concise, helpful answers."
    )
    memory_model_id: str | None = None


class MultiAgentCoordinator:
    def __init__(
        self,
        config: CoordinatorConfig,
        tool_registry: ToolRegistry,
    ) -> None:
        load_dotenv(override=True)
        self.config = config
        self.tool_registry = tool_registry
        self.chat_client = OpenAIChatClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model_id=os.getenv("OPENAI_MODEL_ID"),
        )
        memory_model = self.config.memory_model_id or os.getenv("OPENAI_MODEL_ID")
        self.memory_provider = LongTermMemory(
            ai_client=OpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL"),
            ),
            model_id=memory_model,
        )
        self.thread_store = PersistentThreadStore()
        self.agent: ChatAgent | None = None
        self.thread = None
        self.message_no = 0

    async def start(self) -> None:
        await self.tool_registry.start()
        self.agent = self.chat_client.create_agent(
            name="AdvancedVoiceSupervisor",
            instructions=self.config.instructions,
            tools=self.tool_registry.tools or None,
            context_providers=[self.memory_provider],
        )
        self.thread, self.message_no = await self.thread_store.restore(self.agent)

    async def shutdown(self) -> None:
        if self.thread:
            await self.thread_store.persist(self.thread, self.message_no)
        await self.tool_registry.shutdown()

    async def handle(self, text: str) -> AsyncIterator[object]:
        if not self.agent:
            raise RuntimeError("Coordinator not started")
        async for chunk in self.agent.run_stream(text, thread=self.thread):
            yield chunk
        self.message_no += 1
        await self.thread_store.persist(self.thread, self.message_no)
