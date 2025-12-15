# pip install agent-framework-devui==1.0.0b251016
import asyncio
import os
from typing import Any

from agent_framework import WorkflowOutputEvent, SequentialBuilder, ChatMessage, Role
from agent_framework.openai import OpenAIChatClient
from agent_framework_devui import serve
from dotenv import load_dotenv
from rich import print
# Load environment variables from .env file
load_dotenv()


client = OpenAIChatClient(
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url=os.getenv("OPENAI_BASE_URL"),
        model_id=os.getenv("OPENAI_MODEL_ID"),
    )

customer_support_agent = client.create_agent(
    instructions=(
        "You are a customer support agent. pass to prompt engineering agent to summarize the issue"
    ),
    name="customer_support_agent",
)

prompt_engineering_agent = client.create_agent(
    instructions=(
        "Summarize this customer request in a single, clear sentence that identifies the actionable issue the support team needs to address. Exclude background stories, emotional language, or unrelated details"
    ),
    name="prompt_engineering_agent",
)

# 2) Build sequential workflow: writer -> reviewer
workflow = SequentialBuilder().participants([customer_support_agent, prompt_engineering_agent]).build()


async def main() -> None:
    agent = client.create_agent(
        name="prompt_engineering_agent",
        instructions="Summarize this customer request in a single, clear sentence that identifies the actionable issue the support team needs to address. Exclude background stories, emotional language, or unrelated details.",
    )

    query = "My device keeps shutting down unexpectedly, and I followed all the troubleshooting steps in the manual, but nothing fixed significant compensation the issue. Since this as caused disruption, I’d like to know what options are available."
    print(f"User: {query}")
    result = await agent.run(query)
    print(f"Result: {result}\n")

    # completion: WorkflowOutputEvent | None = None
    # async for event in workflow.run_stream("My device keeps shutting down unexpectedly, and I followed all the troubleshooting steps in the manual, but nothing fixed significant compensation the issue. Since this as caused disruption, I’d like to know what options are available."):
    #     if isinstance(event, WorkflowOutputEvent):
    #         completion = event
    #
    #
    # if completion:
    #     print("===== Final Conversation =====",flush=True)
    #     messages: list[ChatMessage] | Any = completion.data
    #     print(f"Total messages: {len(messages)}", flush=True)
    #     for i, msg in enumerate(messages, start=1):
    #         name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
    #         print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")





if __name__ == "__main__":
    #asyncio.run(main())
    serve(entities=[workflow], port=8093, auto_open=True)
