"""
Local STDIO MCP Example: Expenses Logging Agent

This example demonstrates how to integrate a local STDIO-based MCP (Model Context Protocol) server
with an agent to log expenses. The agent connects to a local MCP server running via STDIO that
manages expense data and uses its tools to create and track expense records.

Key Concepts:
- MCPStdioTool: Connects to STDIO-based MCP servers (local processes)
- ChatAgent: Orchestrates the conversation and tool usage
- Environment-based configuration: Supports both development and production modes
- Date-aware instructions: Provides current date context to the agent
- Shared Middleware: Uses function_logger_middleware for logging tool invocations
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from rich.logging import RichHandler

# Agent Framework imports for creating agents and MCP integration
from agent_framework import ChatAgent, MCPStdioTool

# Local imports
from middleware import function_logger_middleware
from utils import create_openaichat_client

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.WARNING,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)
logger = logging.getLogger("agentframework_mcp_stdio")
logger.setLevel(logging.INFO)

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
RUNNING_IN_PRODUCTION = os.getenv("RUNNING_IN_PRODUCTION", "false").lower() == "true"

if not RUNNING_IN_PRODUCTION:
    load_dotenv(override=True)

# MCP server configuration
SCRIPT_DIR = Path(__file__).parent.parent
MCP_SERVER_PATH = SCRIPT_DIR / "mcp_servers" / "basic_mcp_stdio.py"
PYTHON_EXECUTABLE = sys.executable

# ============================================================================
# MAIN AGENT LOGIC
# ============================================================================

async def stdio_mcp_example() -> None:
    """
    Demonstrate local STDIO MCP integration with an expense tracking system.

    This function shows how to:
    1. Launch a local STDIO-based MCP server process
    2. Create an expense logging agent with date awareness
    3. Process natural language expense entries
    4. Optionally keep the worker alive in production mode

    The agent can understand natural language descriptions of expenses and
    use the MCP server's tools to log them properly with dates, amounts, and categories.
    """
    client = create_openaichat_client()
    logger.info(f"🚀 Starting MCP server: {MCP_SERVER_PATH}")

    async with (
        MCPStdioTool(
            name="Expenses Tracker",
            command=PYTHON_EXECUTABLE,
            args=[str(MCP_SERVER_PATH)],
        ) as mcp_server,
        ChatAgent(
            chat_client=client,
            name="Expenses Agent",
            instructions=f"You help users to log expenses. Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
            middleware=[function_logger_middleware],
        ) as agent,
    ):
        logger.info("✅ MCP server connected successfully")

        # Define the user's expense entry in natural language
        user_query = "yesterday I paid my grocery bill of $93 using my visa."

        # Run the agent with the query, providing access to MCP tools
        result = await agent.run(user_query, tools=mcp_server)

        # Display the final response
        logger.info(f"\n📝 [RESPONSE] {result}")

        # Keep the worker alive in production mode
        while RUNNING_IN_PRODUCTION:
            await asyncio.sleep(60)
            logger.info("Worker still running...")

if __name__ == "__main__":
    asyncio.run(stdio_mcp_example())
