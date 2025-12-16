"""
Shared Middleware for MCP Examples

This module contains reusable middleware functions that can be shared across
multiple MCP examples. Middleware provides cross-cutting concerns like logging,
monitoring, and observability for agent operations.

Available Middleware:
- function_logger_middleware: Logs all function/tool invocations with arguments and results
"""

from __future__ import annotations

import logging
from typing import Callable, Awaitable

from agent_framework import FunctionInvocationContext, function_middleware

# Get logger for middleware operations
logger = logging.getLogger("mcp_middleware")

# ============================================================================
# SHARED MIDDLEWARE: FUNCTION LOGGER
# ============================================================================
# This middleware can be reused across any agent to provide visibility into
# tool/function calls, their arguments, and results.
# ============================================================================

@function_middleware
async def function_logger_middleware(
        context: FunctionInvocationContext,  # Contains function metadata, arguments, and results
        next: Callable[[FunctionInvocationContext], Awaitable[None]],  # Next middleware or actual function
) -> None:
    """
    Logs every function/tool call with arguments and results.

    This middleware demonstrates the function middleware pattern:
    1. Pre-execution: Log the function name and arguments
    2. Execute: Call the actual function via next()
    3. Post-execution: Log the function result

    Args:
        context: Contains function information, arguments, and result after execution
        next: Continuation function to invoke the actual tool/function

    Usage:
        from middleware import function_logger_middleware

        ChatAgent(
            chat_client=client,
            name="MyAgent",
            instructions="...",
            middleware=[function_logger_middleware]
        )
    """

    # Log before function execution
    logger.info(f"\n🔧 [FUNCTION] Calling tool: {context.function.name}")
    logger.info(f"🔧 [FUNCTION] Arguments: {context.arguments}")

    # Execute the actual function (this is where the MCP tool gets called)
    await next(context)

    # Log after function execution - context.result now contains the return value
    logger.info(f"🔧 [FUNCTION] Result: {context.result}")

