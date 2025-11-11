# pip install agent-framework-devui==1.0.0b251016
import asyncio
import os
from typing import Any

from agent_framework import WorkflowOutputEvent, SequentialBuilder, ChatMessage, Role, ConcurrentBuilder
from agent_framework.openai import OpenAIChatClient
from agent_framework_devui import serve
from dotenv import load_dotenv
from rich import print
# Load environment variables from .env file
load_dotenv()

chat_client = OpenAIChatClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_id=os.getenv("OPENAI_MODEL_ID"),
    )

researcher = chat_client.create_agent(
    instructions=(
        "You're an expert market and product researcher. Given a prompt, provide concise, factual insights,"
        " opportunities, and risks."
    ),
    name="researcher",
)

marketer = chat_client.create_agent(
    instructions=(
        "You're a creative marketing strategist. Craft compelling value propositions and target messaging"
        " aligned to the prompt."
    ),
    name="marketer",
)

legal = chat_client.create_agent(
    instructions=(
        "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, and policy concerns"
        " based on the prompt."
    ),
    name="legal",
)

# Participants are either Agents (type of AgentProtocol) or Executors
workflow = ConcurrentBuilder().participants([researcher, marketer, legal]).build()


async def main() -> None:
    completion: WorkflowOutputEvent | None = None
    async for event in workflow.run_stream("We are launching a new budget-friendly electric bike for urban commuters."):
        if isinstance(event, WorkflowOutputEvent):
            completion = event


    if completion:
        print("===== Final Conversation =====",flush=True)
        messages: list[ChatMessage] | Any = completion.data
        print(f"Total messages: {len(messages)}", flush=True)
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")





if __name__ == "__main__":
    asyncio.run(main())
    serve(entities=[workflow], port=8093, auto_open=True)
