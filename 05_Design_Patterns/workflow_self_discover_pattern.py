import asyncio
import os
import sys
import json

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from utils import create_openaichat_client

# Load environment variables
load_dotenv()


# =============================================================================
# 1. DISCOVERY AGENT (Stage 1: Meta-Reasoning)
# =============================================================================

def create_discovery_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    The Discovery Agent does NOT solve the problem.
    It acts as a Meta-Reasoning engine to 'program' the best thinking process.

    Transcript Ref: "The LLM is first prompted... not to solve the original task,
    but to think about how the task should be solved."
    """
    return client.create_agent(
        name="Discovery_Agent",
        model="gpt-4o",
        instructions=(
            "You are a Self-Discover Reasoning Engine.\n"
            "Your Goal: Do NOT solve the user's task directly. Instead, analyze the task "
            "and generate a specialized 'Reasoning Structure' (a unique step-by-step methodology) "
            "that an expert would use to solve it.\n\n"
            "Process:\n"
            "1. Decompose the problem into core sub-problems.\n"
            "2. Identify specific constraints and critical dependencies.\n"
            "3. Select the best reasoning modules (e.g., 'Critical Thinking', 'Creative Association', 'Step-by-Step Verification').\n"
            "4. Output a logical JSON structure representing this plan.\n\n"
            "Output Format (JSON Only):\n"
            "{\n"
            "  \"reasoning_modules_selected\": [\"module1\", \"module2\"],\n"
            "  \"reasoning_structure\": [\n"
            "    \"1. [Action] because [Reason]\",\n"
            "    \"2. [Action] based on [Dependency]\"\n"
            "  ]\n"
            "}"
        )
    )


# =============================================================================
# 2. SOLVER AGENT (Stage 2: Execution)
# =============================================================================

def create_solver_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    The Solver Agent executes the task using the structure provided by the Discovery Agent.

    Transcript Ref: "Execution stage, where those reasoning steps are then integrated
    into the system prompt sent to the LLM."
    """
    return client.create_agent(
        name="Solver_Agent",
        model="gpt-4o",
        instructions=(
            "You are an Expert Problem Solver.\n"
            "You will be given a Task and a strict 'Reasoning Structure'.\n"
            "You must solve the task by following the Reasoning Structure step-by-step.\n"
            "Do not skip steps. Do not use generic reasoning. Stick to the plan."
        )
    )


# =============================================================================
# 3. META-CONTROLLER (The Orchestrator)
# =============================================================================

async def run_self_discover_workflow(user_task: str):
    """
    Orchestrates the Self-Discover pattern:
    1. Discovery Phase: Generate the 'How-To' structure.
    2. Execution Phase: Apply the structure to the task.
    """
    # Initialize Client
    client = create_openaichat_client()

    discovery_agent = create_discovery_agent(client)
    solver_agent = create_solver_agent(client)

    print(f"\n{'=' * 70}")
    print("🧠 SELF-DISCOVER PATTERN INITIALIZED")
    print(f"{'=' * 70}")
    print(f"📥 Incoming Task: \"{user_task}\"\n")

    # --- PHASE 1: DISCOVERY ---
    print(f"🕵️  [Phase 1] Discovery: Meta-Reasoning on HOW to solve...")

    # We prompt the Discovery Agent with the task
    discovery_response = await discovery_agent.run(f"Analyze this task: {user_task}")
    raw_structure = discovery_response.messages[-1].contents[0].text

    # Parse JSON (Handling potential markdown blocks)
    clean_json = raw_structure.replace("```json", "").replace("```", "").strip()

    try:
        structure_data = json.loads(clean_json)
        modules = structure_data.get("reasoning_modules_selected", [])
        steps = structure_data.get("reasoning_structure", [])

        print(f"\n   ✅ Structure Discovered!")
        print(f"   🧩 Modules Selected: {', '.join(modules)}")
        print(f"   📋 Plan:")
        for step in steps:
            print(f"      - {step}")

    except json.JSONDecodeError:
        print("   ❌ Error: Discovery Agent produced invalid JSON. Falling back to raw text.")
        structure_data = {"reasoning_structure": [raw_structure]}

    # --- PHASE 2: EXECUTION ---
    print(f"\n⚙️  [Phase 2] Execution: Solving using the Discovery Structure...")

    # Construct the "Augmented Prompt" (Task + Structure)
    # Transcript Ref: "Reasoning steps are then integrated into the system prompt"
    formatted_structure = json.dumps(structure_data, indent=2)

    augmented_prompt = (
        f"ORIGINAL TASK: {user_task}\n\n"
        f"REQUIRED REASONING STRUCTURE:\n{formatted_structure}\n\n"
        f"Please solve the task now, adhering strictly to the structure above."
    )

    # Run the Solver
    solution_response = await solver_agent.run(augmented_prompt)
    final_answer = solution_response.messages[-1].contents[0].text

    print(f"\n{'=' * 70}")
    print("🏆 FINAL OUTPUT")
    print(f"{'=' * 70}")
    print(final_answer)


# =============================================================================
# 4. MAIN ENTRY POINT
# =============================================================================

if __name__ == "__main__":
    # Example: A high-stakes, novel scenario (e.g., Crisis Management or Complex Logistics)
    complex_task = (
        "I need to create a recovery plan for a supply chain disruption. "
        "Our main supplier in Region A is offline due to a storm. "
        "We have 2 days of inventory left. Region B has stock but costs 40% more. "
        "Region C is cheaper but takes 5 days to ship."
    )

    asyncio.run(run_self_discover_workflow(complex_task))