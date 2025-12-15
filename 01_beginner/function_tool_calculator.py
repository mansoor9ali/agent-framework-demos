"""
NEW 05: Function Tools - Calculator (Interactive Demo)

This demo shows a calculator function tool.
The agent can perform mathematical calculations.
"""

import asyncio
from typing import Annotated
from typing import Callable, Awaitable

from agent_framework import (
    FunctionInvocationContext,
    function_middleware
)
from dotenv import load_dotenv
from pydantic import Field

from utils import create_openaichat_client

load_dotenv()

# Define calculator function
def calculate(
    expression: Annotated[str, Field(description="Mathematical expression to evaluate, e.g. '2 + 2' or '10 * 5'")]
) -> str:
    """Evaluate a mathematical expression."""
    try:
        # Safe evaluation with limited namespace
        result = eval(
            expression,
            {"__builtins__": {}},
            {
                "abs": abs,
                "round": round,
                "min": min,
                "max": max,
                "sum": sum,
                "pow": pow,
                "sqrt": lambda x: x ** 0.5,
            }
        )
        return f"Result: {result}"
    except Exception as e:
        return f"Error: Could not calculate '{expression}'"


# ============================================================================
# MIDDLEWARE 3: FUNCTION LOGGER (Function Middleware)
# ============================================================================

@function_middleware
async def function_logger_middleware(
        context: FunctionInvocationContext,
        next: Callable[[FunctionInvocationContext], Awaitable[None]],
) -> None:
    """Logs every function/tool call with arguments and results."""

    print(f"\n🔧 [FUNCTION] Calling tool: {context.function.name}")
    print(f"🔧 [FUNCTION] Arguments: {context.arguments}")

    # Execute the function
    await next(context)

    # Log the result
    print(f"🔧 [FUNCTION] Result: {context.result}")



async def main():
    """Interactive demo: Agent with calculator tool."""
    
    print("\n" + "="*70)
    print("🧮 DEMO: Function Tools - Calculator")
    print("="*70)
    
    # Create agent with calculator tool
    agent = create_openaichat_client().create_agent(
        instructions="You are a math assistant. Use the calculate tool for math problems. Only give answers related to calculations. otherwise, respond with 'I can only help with math calculations.'",
        name="CalculatorBot",
        tools=[calculate],
        middleware=[
            function_logger_middleware,  # Function middleware
        ]
    )
    
    print("\n✅ Agent created with calculator tool")
    print("💡 TIP: Ask math questions or calculations")
    
    print("\n" + "="*70)
    print("💬 Interactive Chat (Type 'quit' to exit)")
    print("="*70 + "\n")
    
    while True:
        user_input = input("You: ")
        
        if user_input.lower() in ['quit', 'exit', 'q']:
            print("\n👋 Goodbye!")
            break
        
        if not user_input.strip():
            continue
        
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream(user_input):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
