import asyncio
import json
from typing import Dict, Any

from agent_framework import (
    ChatAgent,
    ChatMessage,
    ConcurrentBuilder,
    AgentRunUpdateEvent,
    WorkflowOutputEvent,
    Executor,
    WorkflowContext,
    handler,
    AgentExecutorRequest,
    AgentExecutorResponse,
)
from agent_framework.openai import OpenAIChatClient

from utils import create_openaichat_client



# =============================================================================
# 1. SETUP: Domain Agent Executors (The Workers with State Isolation)
# =============================================================================

class ResearcherExec(Executor):
    """Researcher agent executor with proper state isolation."""

    def __init__(self, chat_client: OpenAIChatClient, id: str = "researcher"):
        self._agent = chat_client.create_agent(
            instructions=(
                "You're an expert market and product researcher. Given a prompt, provide concise, "
                "factual insights, opportunities, and risks."
            ),
            name=id,
        )
        super().__init__(agent=self._agent, id=id)

    @handler
    async def run(self, request: AgentExecutorRequest, ctx: WorkflowContext[AgentExecutorResponse]) -> None:
        response = await self._agent.run(request.messages)
        full_conversation = list(request.messages) + list(response.messages)
        await ctx.send_message(AgentExecutorResponse(self.id, response, full_conversation=full_conversation))


class MarketerExec(Executor):
    """Marketer agent executor with proper state isolation."""

    def __init__(self, chat_client: OpenAIChatClient, id: str = "marketer"):
        self._agent = chat_client.create_agent(
            instructions=(
                "You're a creative marketing strategist. Craft compelling value propositions and "
                "target messaging aligned to the prompt."
            ),
            name=id,
        )
        super().__init__(agent=self._agent, id=id)

    @handler
    async def run(self, request: AgentExecutorRequest, ctx: WorkflowContext[AgentExecutorResponse]) -> None:
        response = await self._agent.run(request.messages)
        full_conversation = list(request.messages) + list(response.messages)
        await ctx.send_message(AgentExecutorResponse(self.id, response, full_conversation=full_conversation))


class LegalExec(Executor):
    """Legal/compliance reviewer executor with proper state isolation."""

    def __init__(self, chat_client: OpenAIChatClient, id: str = "legal"):
        self._agent = chat_client.create_agent(
            instructions=(
                "You're a cautious legal/compliance reviewer. Highlight constraints, disclaimers, "
                "and policy concerns based on the prompt."
            ),
            name=id,
        )
        super().__init__(agent=self._agent, id=id)

    @handler
    async def run(self, request: AgentExecutorRequest, ctx: WorkflowContext[AgentExecutorResponse]) -> None:
        response = await self._agent.run(request.messages)
        full_conversation = list(request.messages) + list(response.messages)
        await ctx.send_message(AgentExecutorResponse(self.id, response, full_conversation=full_conversation))


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

    # A. Create executor instances (used for both approaches)
    researcher = ResearcherExec(chat_client)
    marketer = MarketerExec(chat_client)
    legal = LegalExec(chat_client)

    # Map of executor instances for stage execution
    domain_executors: Dict[str, Executor] = {
        "researcher": researcher,
        "marketer": marketer,
        "legal": legal
    }

    # Also keep simple agents for single-agent execution
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

        # 1. Select the executors for this stage
        current_executor_names = [name for name in stage if name in domain_executors]

        if not current_executor_names:
            continue

        results_buffer = []

        # 2. Check if we have multiple participants (use ConcurrentBuilder with factory registration) or single
        if len(current_executor_names) >= 2:
            # Build Concurrent Workflow using factory registration pattern (no warnings!)
            current_executors = [domain_executors[name] for name in current_executor_names]
            concurrent_workflow = ConcurrentBuilder().participants(current_executors).build()

            # 3. Run the stage with streaming
            async for event in concurrent_workflow.run_stream(context_accumulator):
                if isinstance(event, WorkflowOutputEvent):
                    # Extract text from ChatMessage objects
                    messages: list[ChatMessage] | Any = event.data
                    for msg in messages:
                        if hasattr(msg, 'author_name') and hasattr(msg, 'text'):
                            author = msg.author_name if msg.author_name else "agent"
                            print(f"   -> [{author}] Finished")
                            results_buffer.append(f"[{author}]: {msg.text}")
                elif isinstance(event, AgentRunUpdateEvent):
                    # Optional: Print streaming tokens
                    pass
        else:
            # Single agent: run directly without ConcurrentBuilder
            agent = domain_agents[current_executor_names[0]]
            response = await agent.run(context_accumulator)

            for msg in response.messages:
                if hasattr(msg, 'author_name') and hasattr(msg, 'text'):
                    author = msg.author_name if msg.author_name else current_executor_names[0]
                    print(f"   -> [{author}] Finished")
                    results_buffer.append(f"[{author}]: {msg.text}")

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