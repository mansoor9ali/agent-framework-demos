import asyncio
import json
from typing import List, Dict, Any

from agent_framework import (
    BaseAgent,
    ChatAgent,
    ConcurrentBuilder,
    AgentRunUpdateEvent,
    WorkflowOutputEvent
)
from agent_framework.openai import OpenAIChatClient

from utils import create_openaichat_client



# =============================================================================
# 1. SETUP: Domain Agents (The Workers)
# =============================================================================

async def create_domain_agents(client: OpenAIChatClient) -> Dict[str, ChatAgent]:
    """
    Creates the specialized workers. These are the 'nodes' in our graph.
    """
    researcher = client.create_agent(
        instructions=(
            "You're an expert market and product researcher. Given a prompt, provide concise, "
            "factual insights, opportunities, and risks."
        ),
        name="researcher",
    )

    marketer = client.create_agent(
        instructions=(
            "You're a creative marketing strategist. Craft compelling value propositions and "
            "target messaging aligned to the prompt."
        ),
        name="marketer",
    )

    legal = client.create_agent(
        instructions=(
            "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, "
            "and policy concerns based on the prompt."
        ),
        name="legal",
    )

    return {
        "researcher": researcher,
        "marketer": marketer,
        "legal": legal
    }


# =============================================================================
# 2. THE TASK COMPILER (The Optimizer)
# =============================================================================

def create_task_compiler(client: OpenAIChatClient) -> ChatAgent:
    """
    The Task Compiler translates a natural language request into an OPTIMIZED
    execution schedule (DAG).

    It identifies which tasks are independent and groups them into 'stages'.
    Tasks within the same 'stage' will be executed concurrently.
    """
    return client.create_agent(
        name="Task_Compiler",
        model="gpt-4o",
        instructions=(
            "You are a Concurrent Execution Optimizer. Your goal is to maximize efficiency.\n"
            "1. Analyze the user's complex request.\n"
            "2. Break it down into sub-tasks assignable to these specific agents: ['researcher', 'marketer', 'legal'].\n"
            "3. Identify dependencies. Tasks that do NOT depend on each other should be grouped together.\n"
            "4. Output a JSON object containing a list called 'execution_stages'.\n"
            "   - Each item in 'execution_stages' is a list of agent names to run in parallel.\n"
            "   - Example: [['researcher', 'marketer'], ['legal']] means run researcher and marketer together first, then run legal.\n"
            "5. OUTPUT RAW JSON ONLY. No markdown formatting."
        )
    )


# =============================================================================
# 3. THE EXECUTOR (The Controller Logic)
# =============================================================================

async def run_optimizer_workflow(user_request: str):

    # We use OpenaiChat for standard chat agents
    chat_client = create_openaichat_client()

    # A. Initialize all agents
    domain_agents = await create_domain_agents(chat_client)
    compiler = create_task_compiler(chat_client)

    print(f"--- Incoming Request: {user_request} ---")
    print("\n[Phase 1] Compiling Task Graph...")

    # B. Run the Compiler to get the plan
    # In a real app, you would parse the JSON strictly. Here we assume valid JSON response.
    compiler_response = await compiler.run(user_request)
    raw_plan = compiler_response.messages[-1].contents[0].text

    # Clean potential markdown if present
    raw_plan = raw_plan.replace("```json", "").replace("```", "").strip()

    try:
        plan_data = json.loads(raw_plan)
        execution_stages = plan_data.get("execution_stages", [])
    except json.JSONDecodeError:
        print("Error: Compiler did not return valid JSON.")
        return

    print(f"Optimized Schedule Generated: {execution_stages}")

    # C. Execute the Stages (The 'Graph' Execution)
    context_accumulator = f"Original Request: {user_request}\n\nResults so far:"

    for i, stage in enumerate(execution_stages):
        print(f"\n[Phase 2] Executing Stage {i + 1} (Concurrent Group: {stage})...")

        # 1. Select the agents for this stage
        current_participants = []
        for agent_name in stage:
            if agent_name in domain_agents:
                current_participants.append(domain_agents[agent_name])

        if not current_participants:
            continue

        # 2. Build the Concurrent Workflow for this specific stage
        # This maps to the pattern's concept of executing independent tasks simultaneously[cite: 31, 33].
        concurrent_workflow = ConcurrentBuilder().participants(current_participants).build()

        # 3. Run the stage
        # We pass the accumulated context so subsequent stages know what happened previously.
        results_buffer = []

        events = concurrent_workflow.run_stream(context_accumulator)

        async for event in events:
            if isinstance(event, WorkflowOutputEvent):
                # In a concurrent workflow, output might be a combined object or list.
                # For this demo, we assume string or list of results.
                print(f"   -> Finished: {event.data}")
                results_buffer.append(str(event.data))
            elif isinstance(event, AgentRunUpdateEvent):
                # Optional: Print streaming tokens
                pass

        # 4. Update Context for the next stage (Dependency Injection)
        # This ensures that if Stage 2 depends on Stage 1, it has the data.
        stage_result_text = "\n".join(results_buffer)
        context_accumulator += f"\n\n--- Results from Stage {i + 1} ---\n{stage_result_text}"

    print("\n[Final] Execution Complete. All stages finished.")


# =============================================================================
# 4. MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Example Scenario: A request that benefits from parallelism
    # Research and Marketing can happen together, Legal usually needs to see the result.
    request = "We need to launch a new line of spicy coffee beans. I need market research on trends and a catchy marketing blurb, followed by a legal review of the claims."

    asyncio.run(run_optimizer_workflow(request))