"""
Filtered Tools MCP Example: GitHub Copilot MCP with Tool Filtering

This example demonstrates how to filter MCP tools to only allow specific operations.
It shows how to connect to GitHub Copilot MCP server and restrict the agent to only
use read-only operations like searching repositories, code, and issues.

Key Concepts:
- MCPStreamableHTTPTool: Connects to HTTP-based MCP servers
- Tool Filtering: Restrict which tools the agent can access
- Function Middleware: Logs tool invocations and results
- ChatAgent: Orchestrates the conversation and tool usage with filtered tools
"""

import asyncio
import csv
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from dotenv import load_dotenv
from rich.console import Console
from rich.logging import RichHandler

# Agent Framework imports for creating agents and MCP integration
from agent_framework import ChatAgent, MCPStreamableHTTPTool

# Local imports
from middleware import function_logger_middleware
from utils import create_openaichat_client

# Load environment variables (e.g., API keys) from .env file
load_dotenv()

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler()]
)
logger = logging.getLogger("filtered_mcp")

# Rich console for pretty output
console = Console()

# ============================================================================
# CONFIGURATION
# ============================================================================
# GitHub Copilot MCP server endpoint
GITHUB_MCP_URL = "https://api.githubcopilot.com/mcp/"

# Safe tools - only read-only operations allowed
SAFE_TOOL_NAMES = ["search_repositories", "search_code", "search_issues"]

# CSV output file for storing responses
CSV_OUTPUT_FILE = Path(__file__).parent / "github_mcp_responses.csv"

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def save_to_csv(query: str, response: str, filtered_tools: list, csv_file: Path) -> None:
    """
    Save query and response to CSV file.

    Args:
        query: The user's query
        response: The agent's response
        filtered_tools: List of tools that were filtered/used
        csv_file: Path to the CSV file
    """
    file_exists = csv_file.exists()

    with open(csv_file, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Write header if file is new
        if not file_exists:
            writer.writerow(['Timestamp', 'Query', 'Response', 'Filtered_Tools', 'Tools_Count'])

        # Write data
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        tools_used = ', '.join([t.name if hasattr(t, 'name') else str(t) for t in filtered_tools]) if filtered_tools else 'All MCP tools'
        tools_count = len(filtered_tools) if filtered_tools else 'N/A'

        writer.writerow([timestamp, query, response, tools_used, tools_count])

    console.print(f"\n[bold green]💾 Response saved to:[/bold green] {csv_file}")


# ============================================================================
# MAIN AGENT LOGIC
# ============================================================================

async def filtered_tools_mcp_example() -> None:
    """
    Demonstrate MCP tool filtering with GitHub Copilot MCP server.

    This function shows how to:
    1. Connect to GitHub Copilot MCP server
    2. Get all available tools
    3. Filter to only allow specific read-only operations
    4. Create an agent with filtered tools
    5. Safely execute queries with restricted capabilities

    Tool filtering is important for:
    - Security: Prevent dangerous operations
    - Cost control: Limit expensive API calls
    - Compliance: Ensure only approved operations
    """
    client = create_openaichat_client()

    console.print("\n[bold cyan]═══════════════════════════════════════════════════[/bold cyan]")
    console.print("[bold cyan]  Filtered Tools MCP Example - GitHub Copilot[/bold cyan]")
    console.print("[bold cyan]═══════════════════════════════════════════════════[/bold cyan]\n")

    async with (
        MCPStreamableHTTPTool(
            name="GitHub Copilot MCP",
            url=GITHUB_MCP_URL,
            headers={"Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}"}
        ) as mcp_server,
    ):
        # Get all available tools from the MCP server
        # MCPStreamableHTTPTool exposes tools through its internal structure
        all_tools = mcp_server.tools if hasattr(mcp_server, 'tools') else []

        console.print(f"[dim]📦 Total tools available: {len(all_tools)}[/dim]")
        if all_tools:
            console.print("[dim]   Showing all available tools:[/dim]")
            for tool in all_tools:
                tool_name = tool.name if hasattr(tool, 'name') else str(tool)
                console.print(f"[dim]   - {tool_name}[/dim]")
        console.print()

        # Filter to ONLY read operations for safety
        filtered_tools = []
        if all_tools:
            filtered_tools = [
                t for t in all_tools
                if (hasattr(t, 'name') and t.name in SAFE_TOOL_NAMES) or
                   (str(t) in SAFE_TOOL_NAMES)
            ]

        console.print("[bold green]✓ Filtered Tools (read-only operations):[/bold green]")
        for tool in filtered_tools:
            tool_name = tool.name if hasattr(tool, 'name') else str(tool)
            console.print(f"  [green]✓[/green] {tool_name}")
        console.print()

        if not filtered_tools:
            console.print("[bold yellow]⚠ No tools to filter or tools not yet loaded.[/bold yellow]")
            console.print("[dim]   Note: Some MCP servers load tools lazily on first use.[/dim]")
            console.print("[dim]   Proceeding with full MCP server access...[/dim]\n")
            filtered_tools = None  # Use all tools from mcp_server

        # Create agent with filtered tools (or full server if filtering not possible)
        async with ChatAgent(
            chat_client=client,
            name="SafeGitHubAgent",
            instructions="You are a helpful GitHub assistant. You can only search repositories, code, and issues. You cannot create, modify, or delete anything.",
            middleware=[function_logger_middleware],
        ) as agent:
            console.print("[bold]Agent Instructions:[/bold]")
            console.print("  • Can search repositories, code, and issues")
            console.print("  • Cannot create, modify, or delete anything")
            console.print("  • Read-only operations only\n")

            # Test query
            query = "Find All Microsoft Agent Accelerator repositories and describe in a bulleted list"

            console.print(f"[bold]Query:[/bold] {query}\n")

            # Run agent with FILTERED tools (if available) or full server
            tools_to_use = filtered_tools if filtered_tools else mcp_server
            result = await agent.run(query, tools=tools_to_use)

            console.print("\n[bold green]📝 Response:[/bold green]")
            console.print(result)

            # Save query and response to CSV file
            save_to_csv(query, str(result), filtered_tools, CSV_OUTPUT_FILE)


if __name__ == "__main__":
    asyncio.run(filtered_tools_mcp_example())
