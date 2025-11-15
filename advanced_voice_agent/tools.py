"""Tool registry combining native functions and MCP tools."""

from __future__ import annotations

from dataclasses import dataclass, field, Field
from typing import Any, Callable, Sequence, Annotated

import requests
from agent_framework import MCPStdioTool


# Tool 1: Weather
def get_weather(
    location: Annotated[str, Field(description="City name")]
) -> str:
    """Get current weather for a location."""
    weather_data = {
        "london": "🌧️ 15°C, Rainy",
        "paris": "☀️ 22°C, Sunny",
        "tokyo": "⛅ 18°C, Partly Cloudy",
        "new york": "🌤️ 20°C, Clear"
    }
    return weather_data.get(location.lower(), f"Weather data not available for {location}")


# Tool 2: Calculator
def calculate(
    expression: Annotated[str, Field(description="Math expression")]
) -> str:
    """Calculate a mathematical expression."""
    try:
        result = eval(expression, {"__builtins__": {}}, {
            "abs": abs, "round": round, "min": min, "max": max, "pow": pow
        })
        return f"Result: {result}"
    except:
        return f"Cannot calculate '{expression}'"


# Tool 3: Time Zone
def get_time(
    timezone: Annotated[str, Field(description="Timezone like 'America/New_York' or 'Europe/London'")]
) -> str:
    """Get current time in a timezone."""
    try:
        response = requests.get(f"http://worldtimeapi.org/api/timezone/{timezone}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            time = data.get('datetime', '').split('T')[1].split('.')[0]
            return f"⏰ Current time in {timezone}: {time}"
        else:
            return f"Could not get time for {timezone}"
    except:
        return f"Error getting time for {timezone}"


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
