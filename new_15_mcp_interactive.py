
import asyncio
import os

from utils import create_gptoss120b_client
from dotenv import load_dotenv
from agent_framework import MCPStdioTool
from typing import Callable, Awaitable

from agent_framework import (
    AgentRunContext,
    FunctionInvocationContext,
    ChatContext,
    agent_middleware,
    function_middleware,
    chat_middleware
)


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
    print("\n" + "="*75)
    print("MCP INTERACTIVE DEMO - Calculator Server")
    print("="*75)
    print("""
This demo connects to a LOCAL MCP calculator server!

HOW IT WORKS:
1. Starts MCP calculator server (uvx mcp-server-calculator)
2. Agent gets access to calculator tools
3. You ask math questions
4. Agent uses MCP tools to calculate answers

REQUIREMENTS:
- Install 'uv': pip install uv
- MCP server will be installed automatically via 'uvx'

Let's start!
    """)
    
    input("Press Enter to start MCP server...")
    
    try:
        print("\nStarting MCP calculator server...")
        print("Command: uvx mcp-server-calculator")
        
        async with MCPStdioTool(
            name="calculator",
            command="uvx.exe",
            args=["mcp-server-calculator"]
        ) as mcp_calculator:
            
            print("✅ MCP server started successfully!\n")
            
            # Create agent
            print("Creating agent with MCP calculator tools...")

            
            agent = create_gptoss120b_client().create_agent(
                instructions=(
                    "You are a helpful math assistant. "
                    "Use the calculator tools for all mathematical calculations. "
                    "Show your work and explain the steps."
                ),
                tools=mcp_calculator,
                middleware=[
                    function_logger_middleware,  # Function middleware
                ]
            )
            
            print("✅ Agent ready with MCP calculator!\n")
            
            print("="*75)
            print("INTERACTIVE MODE")
            print("="*75)
            print("""
Try these examples:
1. "What is 15 * 23 + 45?"
2. "Calculate the square root of 256"
3. "What is 2 to the power of 16?"
4. "Calculate (100 + 50) * 3 / 2"
5. "Find the sine of 45 degrees"

Type 'quit' to exit
            """)
            
            while True:
                try:
                    user_input = input("\n💭 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    if user_input.lower() in ['quit', 'exit']:
                        print("\n✅ Thanks for trying MCP! Goodbye!")
                        break
                    
                    print("\n🤖 Agent: ", end="", flush=True)
                    result = await agent.run(user_input)
                    print(result)
                    
                except KeyboardInterrupt:
                    print("\n\n✅ Exiting...")
                    break
                except Exception as e:
                    print(f"\n❌ Error: {e}")
    
    except FileNotFoundError:
        print("\n❌ ERROR: 'uvx' command not found!")
        print("\nSOLUTION:")
        print("1. Install 'uv': pip install uv")
        print("2. Or install with pipx: pipx install uv")
        print("3. Documentation: https://docs.astral.sh/uv/")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTROUBLESHOOTING:")
        print("1. Check 'uv' is installed: uv --version")
        print("2. Try manually: uvx mcp-server-calculator")
        print("3. Check Python version (3.10+ required)")


if __name__ == "__main__":
    asyncio.run(main())
