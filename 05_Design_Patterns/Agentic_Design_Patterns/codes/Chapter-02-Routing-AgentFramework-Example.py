# Copyright (c) 2025 Marco Fago
#
# This code is licensed under the MIT License.
# See the LICENSE file in the repository for the full license text.

import asyncio
import logging
from typing import Annotated

from agent_framework import ChatAgent
from utils import create_synthetic_client
from dotenv import load_dotenv
from pydantic import Field
from rich import print
from rich.logging import RichHandler

# Setup logging
handler = RichHandler(show_path=False, rich_tracebacks=True, show_level=False)
logging.basicConfig(level=logging.WARNING, handlers=[handler], force=True, format="%(message)s")
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Load environment variables from .env file
load_dotenv()

client = create_synthetic_client()

# --- Define Tool Functions ---
# These functions simulate the actions of the specialist agents.
# --- 定义工具函数 ---
# 这些函数模拟了专业智能体的具体行动。

def booking_handler(
    request: Annotated[str, Field(description="The user's request for a booking.")]
) -> str:
    """
    Handles booking requests for flights and hotels.
    Args:
        request: The user's request for a booking.
    Returns:
        A confirmation message that the booking was handled.
    """
    logger.info("-------------------------- Booking Handler Called ----------------------------")
    return f"Booking action for '{request}' has been simulated."

def info_handler(
    request: Annotated[str, Field(description="The user's question.")]
) -> str:
    """
    Handles general information requests.
    Args:
        request: The user's question.
    Returns:
        A message indicating the information request was handled.
    """
    logger.info("-------------------------- Info Handler Called ----------------------------")
    return f"Information request for '{request}'. Result: Simulated information retrieval."


# ----------------------------------------------------------------------------------
# Sub-agent tools: booking and info handlers wrapped as async functions
# ----------------------------------------------------------------------------------

async def plan_booking(query: str) -> str:
    """Handle booking requests for flights and hotels based on user query."""
    logger.info("Tool: plan_booking invoked")
    booking_agent = ChatAgent(
        chat_client=client,
        instructions=(
            "You help users with booking requests for flights and hotels. "
            "Use the booking_handler tool to process the request. "
            "Provide clear confirmation of the booking action."
        ),
        tools=[booking_handler],
    )
    response = await booking_agent.run(query)
    return response.text


async def get_information(query: str) -> str:
    """Handle general information requests and answer user questions."""
    logger.info("Tool: get_information invoked")
    info_agent = ChatAgent(
        chat_client=client,
        instructions=(
            "You help users with general information requests and answer questions. "
            "Use the info_handler tool to retrieve the information. "
            "Provide clear and helpful responses."
        ),
        tools=[info_handler],
    )
    response = await info_agent.run(query)
    return response.text


async def main():
    # ----------------------------------------------------------------------------------
    # Supervisor agent orchestrating sub-agents for routing
    # ----------------------------------------------------------------------------------
    """Main function to run the routing example."""
    """运行路由示例的主函数。"""

    print("--- Agent Framework Routing Example (Supervisor Pattern) ---")
    print("The coordinator routes requests to specialized agents.\n")

    coordinator_agent = ChatAgent(
        chat_client=client,
        instructions=(
            "You are a supervisor coordinator managing two specialist agents: a booking agent and an information agent. "
            "Analyze incoming user requests and delegate them to the appropriate specialist agent.\n"
            "- For any requests related to booking flights or hotels, use the plan_booking tool.\n"
            "- For all other general information questions, use the get_information tool.\n"
            "Provide clear, helpful responses based on the specialist's output."
        ),
        tools=[plan_booking, get_information],
    )

    # Example Usage
    # 使用示例
    test_queries = [
        "Book me a hotel in Paris.",
        "What is the highest mountain in the world?",
        "Tell me a random fact.",
        "Find flights to Tokyo next month."
    ]

    for query in test_queries:
        print(f"\n--- Running Coordinator with request: '{query}' ---")
        response = await coordinator_agent.run(query)
        print(f"Coordinator Final Response: {response.text}\n")


if __name__ == "__main__":
    asyncio.run(main())
