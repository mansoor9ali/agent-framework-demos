import asyncio
from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv
import os

from utils import create_openaichat_client

load_dotenv()


# =============================================================================
# 1. AGENT FACTORIES
# =============================================================================

def create_planner_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    The Planner acts as both the initial Creator and the Refiner.
    It takes a user request (or critique feedback) and outputs a plan.
    """
    return client.create_agent(
        name="Planner",
        model="gpt-4o",
        instructions=(
            "You are a Travel Planner. "
            "Create detailed, realistic itineraries based on requests. "
            "If you receive FEEDBACK from a Critic, you must modify your previous plan "
            "to address every specific point of criticism. "
            "Output the plan in clean Markdown format."
        )
    )


def create_critic_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    The Critic reviews plans. It does NOT generate plans.
    It outputs either 'APPROVED' or a list of specific flaws.
    """
    return client.create_agent(
        name="Critic",
        model="gpt-4o",
        instructions=(
            "You are a harsh Logistics Critic. Review the provided Travel Itinerary. "
            "Check for these specific failures:\n"
            "1. Are there meal breaks (Lunch/Dinner)?\n"
            "2. Is there travel time included between distant locations?\n"
            "3. Is the schedule too packed (more than 12 hours active)?\n\n"
            "If the plan is perfect, output ONLY the single word: APPROVED\n"
            "If there are flaws, list them as bullet points and tell the planner to fix them."
        )
    )


# =============================================================================
# 2. THE FEEDBACK LOOP (Orchestrator Logic)
# =============================================================================

async def run_planner_critic_loop(user_request: str, max_iterations: int = 3):
    # Initialize Client
    client = create_openaichat_client()

    planner = create_planner_agent(client)
    critic = create_critic_agent(client)

    print(f"\n{'=' * 50}")
    print(f"🎬 STARTING PLANNER-CRITIC LOOP")
    print(f"📝 Request: {user_request}")
    print(f"{'=' * 50}\n")

    # --- Step 1: Initial Plan ---
    current_plan_response = await planner.run(user_request)
    current_plan = current_plan_response.messages[-1].contents[0].text

    print(f"--- 🗓️  DRAFT PLAN (Iteration 0) ---")
    print(current_plan)

    # --- Loop ---
    for i in range(1, max_iterations + 1):
        print(f"\n\n🔍 CRITIC REVIEWING (Iteration {i})...")

        # Critic looks at the plan
        critique_response = await critic.run(f"Review this plan:\n\n{current_plan}")
        feedback = critique_response.messages[-1].contents[0].text

        print(f"--- 💬 CRITIC FEEDBACK ---")
        print(feedback)

        # Check for Approval
        if "APPROVED" in feedback.upper() and len(feedback) < 20:
            print(f"\n\n✅ PLAN APPROVED! Exiting loop.")
            break

        # --- Refinement Step ---
        print(f"\n\n🛠️  REFINING PLAN...")

        # We send the specific critique back to the planner
        refine_prompt = (
            f"Here is the previous plan you generated:\n{current_plan}\n\n"
            f"Here is the Critic's feedback:\n{feedback}\n\n"
            "Please rewrite the plan to fix these issues."
        )

        refinement_response = await planner.run(refine_prompt)
        current_plan = refinement_response.messages[-1].contents[0].text

        print(f"--- 🗓️  REFINED PLAN (Iteration {i}) ---")
        print(current_plan)

    # Final Output
    print(f"\n{'=' * 50}")
    print("🏆 FINAL RESULT")
    print(f"{'=' * 50}")
    print(current_plan)


# =============================================================================
# 3. MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # A request deliberately designed to fail a logistics check (no lunch, too busy)
    complex_request = (
        "Plan a 1-day trip to Paris. I want to visit the Louvre, the Eiffel Tower, "
        "Notre Dame, Versailles Palace, and do a Seine River Cruise. "
        "I want to start at 8 AM and finish by 8 PM."
    )

    asyncio.run(run_planner_critic_loop(complex_request))