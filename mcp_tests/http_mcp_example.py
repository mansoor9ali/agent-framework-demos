"""
HTTP MCP Example: Microsoft Learn Documentation Agent

This example demonstrates how to integrate an HTTP-based MCP (Model Context Protocol) server
with an agent to query Microsoft Learn documentation. The agent uses the Microsoft Learn MCP
server to answer questions about Azure, Microsoft products, and related documentation.

Key Concepts:
- MCPStreamableHTTPTool: Connects to HTTP-based MCP servers
- Function Middleware: Logs tool invocations and results
- ChatAgent: Orchestrates the conversation and tool usage
"""

from __future__ import annotations

import asyncio
import logging

# Agent Framework imports for creating agents and MCP integration
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from dotenv import load_dotenv
from rich.logging import RichHandler  # Beautiful logging output

from utils import create_openaichat_client  # Helper to create OpenAI chat client
from middleware import function_logger_middleware  # Shared middleware for logging tool calls

# Load environment variables (e.g., API keys) from .env file
load_dotenv()

# Configure logging with Rich for better console output
# Set to INFO level to show function calls and results
logging.basicConfig(level=logging.INFO, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("learn_mcp_lang")

# Constants
# Microsoft Learn MCP server endpoint - provides access to Microsoft documentation
LEARN_MCP_URL = "https://learn.microsoft.com/api/mcp"

# ============================================================================
# MAIN AGENT LOGIC
# ============================================================================


async def http_mcp_example() -> None:
    """
    Demonstrate MCP integration with Microsoft Learn documentation.

    This function shows how to:
    1. Connect to an HTTP-based MCP server
    2. Create an agent with middleware
    3. Use MCP tools to answer questions about Microsoft documentation

    MCP (Model Context Protocol) allows agents to use external tools and data sources
    in a standardized way. HTTP-based MCP servers expose their capabilities via HTTP endpoints.
    """

    # Create the OpenAI chat client for the agent's LLM capabilities
    client = create_openaichat_client()

    # Use async context managers to ensure proper resource cleanup
    async with (
        # Initialize the MCP server connection
        # MCPStreamableHTTPTool wraps the HTTP MCP endpoint and exposes its tools
        MCPStreamableHTTPTool(name="Microsoft Learn MCP", url=LEARN_MCP_URL) as mcp_server,

        # Create the agent with:
        # - chat_client: The LLM client for generating responses
        # - name: Identifier for the agent
        # - instructions: System prompt guiding the agent's behavior
        # - middleware: List of middleware functions for logging/monitoring
        ChatAgent(
            chat_client=client,
            name="DocsAgent",
            instructions="You help with Microsoft documentation questions.",
            middleware=[
                function_logger_middleware,  # Log all tool invocations
            ]
        ) as agent,
    ):
        # Define the user's question
        query = "How to create an Azure storage account using az cli?"

        # Run the agent with the query, providing access to MCP tools
        # The agent will:
        # 1. Understand the question
        # 2. Decide which MCP tools to call (if any)
        # 3. Call the tools (logged by our middleware)
        # 4. Synthesize a response based on tool results
        result = await agent.run(query, tools=mcp_server)

        # Display the final response
        logger.info(f"\n📝 [RESPONSE] {result}")


if __name__ == "__main__":
    # Entry point: Run the async example
    asyncio.run(http_mcp_example())
