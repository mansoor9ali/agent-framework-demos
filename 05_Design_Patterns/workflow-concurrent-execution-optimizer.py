import asyncio
import json
from typing import Dict, Any, Callable

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
    execution schedule (DAG) with detailed tasks and sub-tasks.

    It identifies which tasks are independent and groups them into 'stages'.
    Tasks within the same 'stage' will be executed concurrently.
    """
    return client.create_agent(
        name="Task_Compiler",
        model="gpt-4o",
        instructions="""You are a Concurrent Execution Optimizer (Task Compiler). Your goal is to maximize efficiency by creating a detailed execution plan.

## Available Agents:
- **researcher**: Expert market and product researcher - provides insights, opportunities, and risks
- **marketer**: Creative marketing strategist - crafts value propositions and target messaging  
- **legal**: Legal/compliance reviewer - highlights constraints, disclaimers, and policy concerns

## Your Task:
1. Analyze the user's complex request thoroughly
2. Break it down into specific tasks and sub-tasks for each relevant agent
3. Identify dependencies between tasks - tasks that do NOT depend on each other should be grouped together
4. Create a comprehensive execution plan

## Output Format (JSON only, no markdown):
{
  "request_summary": "Brief summary of the user's request",
  "execution_stages": [
    {
      "stage_number": 1,
      "stage_name": "Descriptive name for this stage",
      "description": "What this stage accomplishes",
      "agents": [
        {
          "agent_name": "researcher",
          "task": "Main task for this agent",
          "sub_tasks": [
            "Specific sub-task 1",
            "Specific sub-task 2"
          ],
          "expected_output": "What output is expected from this agent"
        },
        {
          "agent_name": "marketer", 
          "task": "Main task for this agent",
          "sub_tasks": [
            "Specific sub-task 1",
            "Specific sub-task 2"
          ],
          "expected_output": "What output is expected from this agent"
        }
      ],
      "dependencies": [],
      "can_run_parallel": true
    },
    {
      "stage_number": 2,
      "stage_name": "Review Stage",
      "description": "Legal review of previous outputs",
      "agents": [
        {
          "agent_name": "legal",
          "task": "Review and validate",
          "sub_tasks": [
            "Review marketing claims",
            "Check compliance"
          ],
          "expected_output": "Compliance report"
        }
      ],
      "dependencies": ["stage_1"],
      "can_run_parallel": false
    }
  ],
  "total_stages": 2,
  "optimization_notes": "Explanation of why this ordering is optimal"
}

OUTPUT RAW JSON ONLY. No markdown formatting, no code blocks."""
    )


# =============================================================================
# 3. THE EXECUTOR (The Controller Logic)
# =============================================================================

def display_execution_plan(plan_data: Dict[str, Any]) -> None:
    """Display the detailed execution plan in a formatted way."""
    print("\n" + "=" * 70)
    print("📋 OPTIMIZED EXECUTION PLAN")
    print("=" * 70)

    # Request Summary
    if "request_summary" in plan_data:
        print(f"\n📝 Request Summary: {plan_data['request_summary']}")

    # Total Stages
    total_stages = plan_data.get("total_stages", len(plan_data.get("execution_stages", [])))
    print(f"📊 Total Stages: {total_stages}")

    # Optimization Notes
    if "optimization_notes" in plan_data:
        print(f"💡 Optimization: {plan_data['optimization_notes']}")

    print("\n" + "-" * 70)

    # Display each stage with details
    for stage in plan_data.get("execution_stages", []):
        stage_num = stage.get("stage_number", "?")
        stage_name = stage.get("stage_name", "Unnamed Stage")
        description = stage.get("description", "No description")
        can_parallel = stage.get("can_run_parallel", False)
        dependencies = stage.get("dependencies", [])

        parallel_icon = "⚡" if can_parallel else "🔗"
        print(f"\n{parallel_icon} Stage {stage_num}: {stage_name}")
        print(f"   Description: {description}")
        if dependencies:
            print(f"   Dependencies: {', '.join(dependencies)}")
        print(f"   Parallel Execution: {'Yes' if can_parallel else 'No'}")

        # Display agents and their tasks
        for agent_info in stage.get("agents", []):
            agent_name = agent_info.get("agent_name", "unknown")
            task = agent_info.get("task", "No task specified")
            sub_tasks = agent_info.get("sub_tasks", [])
            expected_output = agent_info.get("expected_output", "Not specified")

            print(f"\n   🤖 Agent: {agent_name.upper()}")
            print(f"      Task: {task}")

            if sub_tasks:
                print("      Sub-tasks:")
                for j, sub_task in enumerate(sub_tasks, 1):
                    print(f"         {j}. {sub_task}")

            print(f"      Expected Output: {expected_output}")

    print("\n" + "=" * 70 + "\n")


def extract_agent_names_from_stage(stage: Dict[str, Any]) -> list[str]:
    """Extract agent names from a stage in the new format."""
    agents = stage.get("agents", [])
    return [agent.get("agent_name") for agent in agents if agent.get("agent_name")]


def build_agent_context(stage: Dict[str, Any], agent_name: str, base_context: str) -> str:
    """Build a detailed context for an agent including its specific tasks."""
    agent_info = None
    for agent in stage.get("agents", []):
        if agent.get("agent_name") == agent_name:
            agent_info = agent
            break

    if not agent_info:
        return base_context

    task = agent_info.get("task", "")
    sub_tasks = agent_info.get("sub_tasks", [])
    expected_output = agent_info.get("expected_output", "")

    context = f"{base_context}\n\n"
    context += f"--- YOUR SPECIFIC ASSIGNMENT ---\n"
    context += f"Main Task: {task}\n"

    if sub_tasks:
        context += "Sub-tasks to address:\n"
        for i, sub_task in enumerate(sub_tasks, 1):
            context += f"  {i}. {sub_task}\n"

    if expected_output:
        context += f"Expected Output: {expected_output}\n"

    return context


async def run_optimizer_workflow(user_request: str):
    """
    Main workflow executor that:
    1. Compiles the request into an optimized DAG with tasks/sub-tasks
    2. Displays the detailed execution plan
    3. Executes stages concurrently where possible
    """
    # We use OpenaiChat for standard chat agents
    chat_client = create_openaichat_client()

    # A. Create factory functions for lazy initialization (state isolation)
    def create_researcher() -> Executor:
        return ResearcherExec(chat_client)

    def create_marketer() -> Executor:
        return MarketerExec(chat_client)

    def create_legal() -> Executor:
        return LegalExec(chat_client)

    # Map of factory functions for dynamic workflow building
    executor_factories: Dict[str, Callable[[], Executor]] = {
        "researcher": create_researcher,
        "marketer": create_marketer,
        "legal": create_legal
    }

    # Also keep simple agents for single-agent execution
    domain_agents = await create_domain_agents(chat_client)
    compiler = create_task_compiler(chat_client)

    print(f"\n{'='*70}")
    print("🚀 CONCURRENT EXECUTION OPTIMIZER")
    print(f"{'='*70}")
    print(f"\n📥 Incoming Request: {user_request}")
    print("\n⏳ [Phase 1] Compiling Task Graph (DAG)...")

    # B. Run the Compiler to get the detailed plan
    compiler_response = await compiler.run(user_request)
    raw_plan = compiler_response.messages[-1].contents[0].text

    # Clean potential markdown if present
    raw_plan = raw_plan.replace("```json", "").replace("```", "").strip()

    # Save to file for inspection
    plan_file_path = "05_Design_Patterns/optimized_plan.json"
    with open(plan_file_path, "w") as f:
        f.write(raw_plan)
    print(f"   💾 Plan saved to: {plan_file_path}")

    try:
        plan_data = json.loads(raw_plan)
        execution_stages = plan_data.get("execution_stages", [])
    except json.JSONDecodeError as e:
        print(f"❌ Error: Compiler did not return valid JSON: {e}")
        print(f"   Raw response: {raw_plan[:500]}...")
        return

    # Display the detailed execution plan
    display_execution_plan(plan_data)

    # C. Execute the Stages (The 'Graph' Execution)
    print("⚡ [Phase 2] Executing Optimized Plan...")
    context_accumulator = f"Original Request: {user_request}\n\nResults so far:"

    for stage in execution_stages:
        stage_num = stage.get("stage_number", "?")
        stage_name = stage.get("stage_name", "Unnamed")
        can_parallel = stage.get("can_run_parallel", False)

        # Extract agent names from the new structure
        current_agent_names = extract_agent_names_from_stage(stage)
        current_agent_names = [name for name in current_agent_names if name in executor_factories]

        if not current_agent_names:
            print(f"\n   ⚠️ Stage {stage_num}: No valid agents found, skipping...")
            continue

        parallel_mode = "PARALLEL" if can_parallel and len(current_agent_names) >= 2 else "SEQUENTIAL"
        print(f"\n   📍 Stage {stage_num}: {stage_name} [{parallel_mode}]")
        print(f"      Agents: {', '.join(current_agent_names)}")

        results_buffer = []

        # Execute based on number of agents and parallel capability
        if len(current_agent_names) >= 2 and can_parallel:
            # Build Concurrent Workflow
            # Note: Warning is informational - we create fresh instances from factories
            current_executors = [executor_factories[name]() for name in current_agent_names]
            concurrent_workflow = ConcurrentBuilder().participants(current_executors).build()

            # Build context with specific tasks for each agent
            stage_context = build_agent_context(stage, current_agent_names[0], context_accumulator)

            async for event in concurrent_workflow.run_stream(stage_context):
                if isinstance(event, WorkflowOutputEvent):
                    messages: list[ChatMessage] | Any = event.data
                    for msg in messages:
                        if hasattr(msg, 'author_name') and hasattr(msg, 'text'):
                            author = msg.author_name if msg.author_name else "agent"
                            print(f"      ✅ [{author}] Completed")
                            results_buffer.append(f"[{author}]: {msg.text}")
                elif isinstance(event, AgentRunUpdateEvent):
                    pass  # Optional: streaming tokens
        else:
            # Single agent or sequential execution
            for agent_name in current_agent_names:
                agent = domain_agents.get(agent_name)
                if not agent:
                    continue

                # Build context with specific tasks for this agent
                agent_context = build_agent_context(stage, agent_name, context_accumulator)
                response = await agent.run(agent_context)

                for msg in response.messages:
                    if hasattr(msg, 'author_name') and hasattr(msg, 'text'):
                        author = msg.author_name if msg.author_name else agent_name
                        print(f"      ✅ [{author}] Completed")
                        results_buffer.append(f"[{author}]: {msg.text}")

        # Update Context for the next stage (Dependency Injection)
        stage_result_text = "\n".join(results_buffer)
        context_accumulator += f"\n\n--- Results from Stage {stage_num}: {stage_name} ---\n{stage_result_text}"

    print(f"\n{'='*70}")
    print("🎉 [Final] Execution Complete. All stages finished.")
    print(f"{'='*70}\n")


# =============================================================================
# 4. MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Example Scenario: A request that benefits from parallelism
    # Research and Marketing can happen together, Legal usually needs to see the result.
    request = "We need to launch a new line of spicy coffee beans. I need market research on trends and a catchy marketing blurb, followed by a legal review of the claims."

    asyncio.run(run_optimizer_workflow(request))