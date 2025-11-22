import os

from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()


# ------------------------------------------------------------------------------q
# Defining the Protocol: The MCP Standard
# ------------------------------------------------------------------------------
# Before we build our agents, we must define the language they will speak.
# MCP provides a simple, structured way to pass context. For this example,
# our MCP message will be a Python dictionary with key fields.
# ------------------------------------------------------------------------------
def create_mcp_message(sender, content, metadata=None):
    """Creates a standardized MCP message."""
    return {
        "protocol_version": "1.0",
        "sender": sender,
        "content": content,
        "metadata": metadata or {}
    }


# ------------------------------------------------------------------------------
# Building the Agents: The Specialists
# ------------------------------------------------------------------------------
# Each agent is a function that takes an MCP message as input and returns one
# as output. The core of each agent is a carefully crafted "Semantic Blueprint"
# in the system prompt that defines its persona and task.
# ------------------------------------------------------------------------------

def call_llm(system_prompt, user_content):
    """A helper function to call the OpenAI API using the new client syntax."""
    try:
        client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),
                        base_url=os.getenv("DEEPSEEK_BASE_URL"),

                        )
        # Using the updated client.chat.completions.create method
        response = client.chat.completions.create(
            model="deepseek-reasoner",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"An error occurred with the API call: {e}"


# --- Agent 1: The Researcher ---
def researcher_agent(mcp_input):
    """
    This agent takes a research topic, finds information, and returns a summary.
    """
    print("\n[Researcher Agent Activated]")
    simulated_database = {
        "mediterranean diet": "The Mediterranean diet is rich in fruits, vegetables, whole grains, olive oil, and fish. Studies show it is associated with a lower risk of heart disease, improved brain health, and a longer lifespan. Key components include monounsaturated fats and antioxidants."
    }
    research_topic = mcp_input['content']
    research_result = simulated_database.get(research_topic.lower(), "No information found on this topic.")
    system_prompt = "You are a research analyst. Your task is to synthesize the provided information into 3-4 concise bullet points. Focus on the key findings."
    summary = call_llm(system_prompt, research_result)
    print(f"Research summary created for: '{research_topic}'")
    return create_mcp_message(
        sender="ResearcherAgent",
        content=summary,
        metadata={"source": "Simulated Internal DB"}
    )


# --- Agent 2: The Writer ---
def writer_agent(mcp_input):
    """
    This agent takes research findings and writes a short blog post.
    """
    print("\n[Writer Agent Activated]")
    research_summary = mcp_input['content']
    system_prompt = "You are a skilled content writer for a health and wellness blog. Your tone is engaging, informative, and encouraging. Your task is to take the following research points and write a short, appealing blog post (approx. 150 words) with a catchy title."
    blog_post = call_llm(system_prompt, research_summary)
    print("Blog post drafted.")
    return create_mcp_message(
        sender="WriterAgent",
        content=blog_post,
        metadata={"word_count": len(blog_post.split())}
    )


# ------------------------------------------------------------------------------
# Building the Orchestrator: The Project Manager
# ------------------------------------------------------------------------------
# The Orchestrator manages the workflow. It calls the agents in the correct
# order, passing context from one to the next using MCP messages.
# ------------------------------------------------------------------------------

def orchestrator(initial_goal):
    """
    Manages the multi-agent workflow to achieve a high-level goal.
    """
    print("=" * 50)
    print(f"[Orchestrator] Goal Received: '{initial_goal}'")
    print("=" * 50)

    # --- Step 1: Orchestrator plans and calls the Researcher Agent ---
    print("\n[Orchestrator] Task 1: Research. Delegating to Researcher Agent.")
    research_topic = "Mediterranean Diet"
    mcp_to_researcher = create_mcp_message(
        sender="Orchestrator",
        content=research_topic
    )
    mcp_from_researcher = researcher_agent(mcp_to_researcher)
    print("\n[Orchestrator] Research complete. Received summary:")
    print("-" * 20)
    print(mcp_from_researcher['content'])
    print("-" * 20)

    # --- Step 2: Orchestrator calls the Writer Agent ---
    print("\n[Orchestrator] Task 2: Write Content. Delegating to Writer Agent.")
    mcp_to_writer = create_mcp_message(
        sender="Orchestrator",
        content=mcp_from_researcher['content']
    )
    mcp_from_writer = writer_agent(mcp_to_writer)
    print("\n[Orchestrator] Writing complete.")

    # --- Step 3: Orchestrator presents the final result ---
    final_output = mcp_from_writer['content']
    print("\n" + "=" * 50)
    print("[Orchestrator] Workflow Complete. Final Output:")
    print("=" * 50)
    print(final_output)


# ------------------------------------------------------------------------------
# Let's give our Orchestrator a high-level goal and watch the agent team work.
# ------------------------------------------------------------------------------
if __name__ == '__main__':
    print("\n=== Multi-Agent Collaboration using MCP Protocol ===\n")
    user_goal = "Create a blog post about the benefits of the Mediterranean diet."
    orchestrator(user_goal)
