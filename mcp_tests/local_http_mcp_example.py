"""
Local HTTP MCP Example: Expenses Logging Agent

This example demonstrates how to integrate a local HTTP-based MCP (Model Context Protocol) server
with an agent to log expenses. The agent connects to a local MCP server that manages expense data
and uses its tools to create and track expense records.

Key Concepts:
- MCPStreamableHTTPTool: Connects to HTTP-based MCP servers (local or remote)
- ChatAgent: Orchestrates the conversation and tool usage
- Environment-based configuration: Supports both development and production modes
- Date-aware instructions: Provides current date context to the agent
"""

import asyncio
import logging
import os
from datetime import datetime

# Agent Framework imports for creating agents and MCP integration
from agent_framework import ChatAgent, MCPStreamableHTTPTool
from utils import create_openaichat_client  # Helper to create OpenAI chat client
from middleware import function_logger_middleware  # Shared middleware for logging tool calls
from dotenv import load_dotenv
from rich.logging import RichHandler  # Beautiful logging output

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
# Configure logging with Rich for better console output
# Base level is WARNING, but we override the logger to INFO for our messages
logging.basicConfig(level=logging.WARNING, format="%(message)s", datefmt="[%X]", handlers=[RichHandler()])
logger = logging.getLogger("agentframework_mcp_http")
logger.setLevel(logging.INFO)  # Show INFO level messages for this logger

# ============================================================================
# ENVIRONMENT CONFIGURATION
# ============================================================================
# Determine if running in production environment
# This affects whether to load .env file and how long to keep the worker alive
RUNNING_IN_PRODUCTION = os.getenv("RUNNING_IN_PRODUCTION", "false").lower() == "true"

# Load environment variables from .env file in development mode
if not RUNNING_IN_PRODUCTION:
    load_dotenv(override=True)

# MCP server URL - defaults to localhost for local development
# In production, this should point to the deployed MCP server
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8000/mcp/")

# API host configuration (for future use)
API_HOST = os.getenv("API_HOST", "github")



# ============================================================================
# MAIN AGENT LOGIC
# ============================================================================

async def http_mcp_example() -> None:
    """
    Demonstrate local MCP integration with an expense tracking system.

    This function shows how to:
    1. Connect to a local HTTP-based MCP server
    2. Create an expense logging agent with date awareness
    3. Process natural language expense entries
    4. Optionally keep the worker alive in production mode

    The agent can understand natural language descriptions of expenses and
    use the MCP server's tools to log them properly with dates, amounts, and categories.
    """

    # Create the OpenAI chat client for the agent's LLM capabilities
    client = create_openaichat_client()

    # Use async context managers to ensure proper resource cleanup
    async with (
        # Initialize the local MCP server connection
        # MCPStreamableHTTPTool wraps the HTTP MCP endpoint and exposes its tools
        MCPStreamableHTTPTool(name="Expenses MCP Server", url=MCP_SERVER_URL) as mcp_server,

        # Create the expense logging agent with:
        # - chat_client: The LLM client for generating responses
        # - name: Identifier for the agent
        # - instructions: System prompt with current date context for accurate expense logging
        # - middleware: List of middleware functions for logging/monitoring
        ChatAgent(
            chat_client=client,
            name="Expenses Agent",
            instructions=f"You help users to log expenses. Today's date is {datetime.now().strftime('%Y-%m-%d')}.",
            middleware=[
                function_logger_middleware,  # Log all tool invocations
            ]
        ) as agent,
    ):
        # Define the user's expense entry in natural language
        user_query = "yesterday I bought a laptop for $1200 using my visa."

        # Run the agent with the query, providing access to MCP tools
        # The agent will:
        # 1. Parse the natural language expense description
        # 2. Extract relevant information (date, amount, category, payment method)
        # 3. Call the appropriate MCP server tools to log the expense
        # 4. Provide confirmation to the user
        result = await agent.run(user_query, tools=mcp_server)

        # Display the final response using logger
        logger.info(f"\n📝 [RESPONSE] {result}")

        # Keep the worker alive in production mode
        # This is useful when running as a continuous service
        while RUNNING_IN_PRODUCTION:
            await asyncio.sleep(60)
            logger.info("Worker still running...")


if __name__ == "__main__":
    # Entry point: Run the async example
    asyncio.run(http_mcp_example())