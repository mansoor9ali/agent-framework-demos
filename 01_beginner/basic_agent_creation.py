"""
NEW 01: Create Azure AI Foundry Agent (Interactive Demo)

This is an INTERACTIVE demo where you can create a new agent in Azure AI Foundry
and chat with it in real-time.

The agent is persistent and will be saved to Azure AI Foundry service.
"""

import asyncio
from dotenv import load_dotenv
from utils import create_dotted_client

# Load environment variables
load_dotenv()

async def main():
    """Interactive demo: Create agent and chat."""
    
    print("\n" + "="*70)
    print("🤖 DEMO: Create Azure AI Foundry Agent (Interactive)")
    print("="*70)

    agent = create_dotted_client().create_agent(
        name="DemoAgent",
        instructions="You are a helpful AI assistant. Be concise and friendly."
    )


    query= "What is the capital of France?"
    async for chunk in agent.run_stream(query):
        if chunk.text:
            print(chunk.text, end="", flush=True)
    print("\n")

    #
    # print(f"✅ Agent created successfully!")
    # print(f"   Agent ID: {agent.id}")
    #
    #
    #
    # print("\n" + "="*70)
    # print("💬 Interactive Chat (Type 'quit' to exit)")
    # print("="*70 + "\n")
    #
    # while True:
    #     # Get user input
    #     user_input = input("You: ")
    #
    #     if user_input.lower() in ['quit', 'exit', 'q']:
    #         print("\n👋 Goodbye!")
    #         break
    #
    #     if not user_input.strip():
    #         continue
    #
    #     # Get response from agent
    #     print("Agent: ", end="", flush=True)
    #     async for chunk in agent.run_stream(user_input):
    #         if chunk.text:
    #             print(chunk.text, end="", flush=True)
    #     print("\n")


if __name__ == "__main__":
    asyncio.run(main())
