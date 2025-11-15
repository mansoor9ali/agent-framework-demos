"""Tool registry combining native functions and MCP tools."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Sequence

from agent_framework import MCPStdioTool


@dataclass
class ToolRegistry:
    python_tools: Sequence[Callable[..., Any]] = field(default_factory=tuple)
    mcp_specs: Sequence[dict[str, Any]] = field(default_factory=tuple)
    _mcp_tools: list[MCPStdioTool] = field(init=False, default_factory=list)

    async def start(self) -> None:
        for spec in self.mcp_specs:
            tool = MCPStdioTool(**spec)
            await tool.__aenter__()
            self._mcp_tools.append(tool)

    async def shutdown(self) -> None:
        while self._mcp_tools:
            tool = self._mcp_tools.pop()
            await tool.__aexit__(None, None, None)

    @property
    def tools(self) -> list[Any]:
        combo = list(self.python_tools)
        combo.extend(self._mcp_tools)
        return combo
