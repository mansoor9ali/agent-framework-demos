import asyncio
import json
import os
import re
import sys

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from utils import create_openaichat_client

# Ensure you have your .env file with OPENAI_API_KEY, etc.
load_dotenv()

# =============================================================================
# 1. SETUP: Dummy Data & Mock Tools (The "External" World)
# =============================================================================

DUMMY_DATA_FILE = "offsite_booking_data.json"


def create_dummy_data():
    """Creates a local JSON file simulating an external database or API."""
    data = {
        "venue_reservation": {
            "code": "CONF-VENUE-9988",
            "location": "Grand Oak Conference Center, Room B",
            "status": "Confirmed"
        },
        "attendee_data": {
            "count": 15,
            "departments": ["Engineering", "Product"],
            "status": "All RSVP'd"
        },
        "catering_service": {
            "provider": "Gourmet Bites Inc.",
            "menu": "Mediterranean Buffet (Vegan/GF options included)",
            "confirmation_message": "Order #CAT-554 received. Delivery at 11:30 AM.",
            "total_cost": 1500.00
        }
    }
    with open(DUMMY_DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"📄 Dummy data source created: {DUMMY_DATA_FILE}")


# Mock Tool Functions (Simulating API calls)
async def fetch_venue_confirmation() -> str:
    """Simulates fetching venue details."""
    await asyncio.sleep(1)  # Simulate network latency
    with open(DUMMY_DATA_FILE, "r") as f:
        data = json.load(f)
    venue = data["venue_reservation"]
    return f"{venue['location']} (Code: {venue['code']})"


async def fetch_attendee_count() -> str:
    """Simulates fetching attendee metrics."""
    await asyncio.sleep(1)
    with open(DUMMY_DATA_FILE, "r") as f:
        data = json.load(f)
    attendees = data["attendee_data"]
    return f"{attendees['count']} people ({', '.join(attendees['departments'])})"


async def fetch_caterer_message() -> str:
    """Simulates fetching catering status."""
    await asyncio.sleep(1)
    with open(DUMMY_DATA_FILE, "r") as f:
        data = json.load(f)
    cat = data["catering_service"]
    return f"{cat['provider']}: {cat['confirmation_message']} Est Cost: ${cat['total_cost']}"


# Map tool names (from the Planner's JSON) to actual Python functions
TOOL_MAP = {
    "get_venue_confirmation": fetch_venue_confirmation,
    "get_attendee_count": fetch_attendee_count,
    "get_caterer_message": fetch_caterer_message
}


# =============================================================================
# 2. THE PLANNER AGENT (Reasoning Module)
# =============================================================================

def create_planner_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    The Planner Agent uses the 'Reasoning without Observation' pattern.
    It does NOT call tools directly.
    Instead, it outputs a JSON plan containing:
      1. 'retrieval_sub_plan': A list of keys representing data to fetch.
      2. 'synthesis_template': A text template with placeholders (e.g., {venue_info}).
    """
    return client.create_agent(
        name="Planner",
        model="gpt-4o",  # Use a strong model for reasoning
        instructions="""You are an expert Event Planner utilizing the 'Reasoning without Observation' pattern.

Your goal is to organize a meeting proposal by generating a plan and a template BEFORE any data is fetched.

You have access to the following hypothetical data sources (keys):
- "get_venue_confirmation": Returns venue location and code.
- "get_attendee_count": Returns confirmed attendee count.
- "get_caterer_message": Returns catering details and cost.

## Your Task:
1. Analyze the user's request.
2. Generate a JSON object containing:
   - "retrieval_sub_plan": A dictionary where keys are the placeholder names you want to use in your template (e.g., "venue_info"), and values are the exact tool names from the list above.
   - "synthesis_template": A detailed markdown report string. It MUST use the placeholders defined in your sub-plan (e.g., "{venue_info}") so the controller can fill them in later.

## Output Format (Raw JSON Only):
{
  "retrieval_sub_plan": {
    "variable_name_1": "tool_name_a",
    "variable_name_2": "tool_name_b"
  },
  "synthesis_template": "# Title\n\nDetails: {variable_name_1}..."
}

Do NOT execute tools. Do NOT output markdown code blocks. Just the raw JSON string."""
    )


# =============================================================================
# 3. CONTROLLER LOGIC (Observation & Synthesis)
# =============================================================================

async def run_reasoning_without_observation_workflow(user_request: str):
    # 0. Initialize Client
    api_key = os.getenv("OPENAI_API_KEY")
    base_url = os.getenv("OPENAI_BASE_URL")
    model_id = os.getenv("OPENAI_MODEL_ID")

    if not api_key:
        print("❌ Error: OPENAI_API_KEY not found in environment.")
        return

    client = create_openaichat_client()

    # 1. Create Dummy Data
    create_dummy_data()

    # 2. Reasoning Phase (Planner)
    print(f"\n{'=' * 60}")
    print("🧠 PHASE 1: REASONING (Generating Plan & Template)")
    print(f"{'=' * 60}")
    print(f"User Request: \"{user_request}\"\n")

    planner = create_planner_agent(client)

    # Run planner to get the JSON structure
    response = await planner.run(user_request)
    raw_response = response.messages[-1].contents[0].text

    # Clean response if LLM adds markdown blocks
    cleaned_json = raw_response.replace("```json", "").replace("```", "").strip()

    # Try to fix potentially truncated or malformed JSON
    def try_parse_json(json_str: str):
        """Attempt multiple strategies to parse potentially malformed JSON."""
        # Strategy 1: Direct parse
        try:
            return json.loads(json_str, strict=False)
        except json.JSONDecodeError:
            pass

        # Strategy 2: Add missing closing brace if truncated
        if json_str.count('{') > json_str.count('}'):
            try:
                fixed = json_str + '}' * (json_str.count('{') - json_str.count('}'))
                return json.loads(fixed, strict=False)
            except json.JSONDecodeError:
                pass

        # Strategy 3: Try to extract JSON object using regex
        match = re.search(r'\{[\s\S]*}', json_str)
        if match:
            try:
                return json.loads(match.group(), strict=False)
            except json.JSONDecodeError:
                pass

        return None

    plan_data = try_parse_json(cleaned_json)

    if plan_data:
        sub_plan = plan_data.get("retrieval_sub_plan", {})
        template = plan_data.get("synthesis_template", "")

        print("✅ Plan Generated Successfully.")
        print(f"   Variables to Fetch: {list(sub_plan.keys())}")
        print(f"   Template Length: {len(template)} chars")
    else:
        print("❌ Error: Planner failed to return valid JSON.")
        print(f"Raw Output: {raw_response}")
        return

    # 3. Observation Phase (Parallel Retrieval)
    print(f"\n{'=' * 60}")
    print("👀 PHASE 2: OBSERVATION (Parallel Data Retrieval)")
    print(f"{'=' * 60}")

    fetched_data = {}
    tasks = []
    keys_in_order = []

    # Prepare async tasks
    for variable_name, tool_name in sub_plan.items():
        if tool_name in TOOL_MAP:
            print(f"🚀 Launching async task: {tool_name} -> '{variable_name}'")
            tasks.append(TOOL_MAP[tool_name]())
            keys_in_order.append(variable_name)
        else:
            print(f"⚠️ Warning: Unknown tool '{tool_name}' requested.")
            fetched_data[variable_name] = "[Data Not Available]"

    # Execute all tasks concurrently (Wait for all)
    results = await asyncio.gather(*tasks)

    # Map results back to variable names
    for i, result in enumerate(results):
        key = keys_in_order[i]
        fetched_data[key] = result
        print(f"   ⬇️  Received {key}: {result}")

    # 4. Synthesis Phase (Filling the Template)
    print(f"\n{'=' * 60}")
    print("📝 PHASE 3: SYNTHESIS (Final Report Generation)")
    print(f"{'=' * 60}")

    try:
        # The 'Reasoning without Observation' pattern relies on the template being
        # perfectly aligned with the fetched data keys.
        final_report = template.format(**fetched_data)

        print("\n" + final_report)

        # Save output to file
        with open("final_confirmation_report.md", "w") as f:
            f.write(final_report)
        print(f"\n💾 Report saved to 'final_confirmation_report.md'")

    except KeyError as e:
        print(f"❌ Synthesis Error: Template contained a placeholder {e} that was not in the sub-plan.")
    except Exception as e:
        print(f"❌ Synthesis Error: {e}")


# =============================================================================
# 4. MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # User Request: Complex venue planning scenario
    request = (
        "I need to organize a half-day team offsite meeting for 15 people next month. "
        "It needs to be in-person, engaging, and include catering. "
        "Generate a proposal confirmation report."
    )

    asyncio.run(run_reasoning_without_observation_workflow(request))