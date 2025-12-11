"""Entry point for advanced voice agent system."""

from __future__ import annotations

from typing import AsyncIterator

from .voice_io import AdvancedVoiceAgentSystem
from .coordinator import CoordinatorConfig, MultiAgentCoordinator
from .tools import ToolRegistry, get_weather, calculate, get_time
from .idle import IdleController



MCP_SPECS = [
    {
        "name": "calculator",
        "command": "uvx.exe",
        "args": ["mcp-server-calculator"],
    }
]


async def build_coordinator() -> MultiAgentCoordinator:
    tools = ToolRegistry(
        python_tools=[get_weather, calculate, get_time],
        mcp_specs=MCP_SPECS,
    )
    coordinator = MultiAgentCoordinator(CoordinatorConfig(), tools)
    await coordinator.start()
    return coordinator


def main() -> None:
    coordinator: MultiAgentCoordinator | None = None

    async def before_loop() -> None:
        nonlocal coordinator
        coordinator = await build_coordinator()

    async def after_loop() -> None:
        if coordinator:
            await coordinator.shutdown()

    async def responder(text: str) -> AsyncIterator[object]:
        if not coordinator:
            raise RuntimeError("Coordinator not initialized")
        async for chunk in coordinator.handle(text):
            yield chunk

    system = AdvancedVoiceAgentSystem(
        responder,
        before_loop=before_loop,
        after_loop=after_loop,
        idle_controller=IdleController(max_idle_attempts=5, idle_timeout=300.0),
    )
    system.run()


if __name__ == "__main__":
    main()
