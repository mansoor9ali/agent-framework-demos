# Copyright (c) Microsoft. All rights reserved.

import asyncio

from agent_framework import (
    AgentRunUpdateEvent,
    ChatAgent,
    WorkflowBuilder,
    WorkflowOutputEvent
)
from agent_framework.openai import OpenAIChatClient

from utils import create_openaichat_client

"""
Plan-and-Execute Pattern Implementation
---------------------------------------
This workflow demonstrates the "Plan-and-Execute" Agentic Pattern.
It decouples reasoning (Planning) from action (Execution) to optimize performance 
for complex tasks[cite: 24, 26].

Phase 1: Planner Agent generates a full schedule/plan[cite: 27].
Phase 2: Executor Agent (Controller) receives the plan and acts on it.
"""


def create_planner_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    Creates the Planner Agent (Reasoning Module).

    Responsibilities:
    - Analyze the full scope of the task.
    - Generate a detailed step-by-step plan[cite: 29].
    - DOES NOT execute the actions.
    """
    return client.create_agent(
        name="Planner",
        instructions=(
            "You are a strategic Planner Agent. "
            "Your ONLY goal is to analyze the user's request and create a detailed, "
            "step-by-step plan to achieve it. "
            "1. Group thoughts to understand the full scope. "
            "2. Output a numbered list of actions required. "
            "3. Do NOT execute the steps yourself. Just provide the plan."
        ),
        model="gpt-4o",  # Ensure a high-reasoning model is used
    )


def create_executor_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    Creates the Executor Agent (Controller Module).

    Responsibilities:
    - Receive the plan from the Planner.
    - Execute each step sequentially.
    - Produce the final deliverable based on the plan.
    """
    return client.create_agent(
        name="Executor",
        instructions=(
            "You are the Controller and Executor. "
            "You will receive a numbered plan from the Planner. "
            "Your job is to EXECUTE that plan strictly. "
            "1. Read the plan provided in the history. "
            "2. Generate the content or perform the actions described in each step. "
            "3. Compile the results into a final response."
        ),
        model="gpt-4o",
    )


async def main() -> None:
    print("Initializing Plan-and-Execute Agent Workflow...\n")

    # Create the OpenAI chat client (not an async context manager)
    client = create_openaichat_client()

    # Build the workflow: Planner -> Executor
    # This mirrors the pattern where the plan is handed over to the controller.
    workflow = (
        WorkflowBuilder()
        # Phase 1: Reasoning/Planning
        .register_agent(lambda: create_planner_agent(client), name="planner")

        # Phase 2: Execution/Controller
        .register_agent(lambda: create_executor_agent(client), name="executor", output_response=True)

        # Define the linear flow: User -> Planner -> Executor -> Output
        .set_start_executor("planner")
        .add_edge("planner", "executor")
        .build()
    )

    # Example Task: Complex venue planning scenario from the transcript[cite: 4].
    user_request = (
        "I need to organize a half-day team offsite meeting for 15 people next month. "
        "It needs to be in-person, engaging, and include catering."
    )

    print(f"User Request: {user_request}\n")
    print("-" * 50)

    last_executor_id: str | None = None

    # Execute the workflow using streaming to observe the hand-off
    events = workflow.run_stream(user_request)

    async for event in events:
        if isinstance(event, AgentRunUpdateEvent):
            eid = event.executor_id

            # Visual separation between agents (Plan phase vs Execute phase)
            if eid != last_executor_id:
                if last_executor_id is not None:
                    print("\n" + "-" * 50 + "\n")  # Separator between phases

                # Labeling the phases based on the pattern
                phase_label = "PHASE 1: PLANNING" if eid == "planner" else "PHASE 2: EXECUTION"
                print(f"[{phase_label}] ({eid}):", end=" ", flush=True)
                last_executor_id = eid

            print(event.data, end="", flush=True)

        elif isinstance(event, WorkflowOutputEvent):
            print("\n\n" + "=" * 20 + " Final Output " + "=" * 20)
            print(event.data)


if __name__ == "__main__":
    asyncio.run(main())