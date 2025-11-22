#
# # Building a Multi-Agent System with MCP
# 
# *Adding controls to the MAS and MCP system*
# 
# copyright 2025, Denis Rothman
# 
# **Making the Agent System More Robust**
# 
# We will now add several important controls to our multi agent system. These additions will change our functional prototype into a more reliable and intelligent system. We will focus on handling real world failures ensuring data is correct and implementing a quality control process.
# 
# First we will make our communication with the API more resilient. We will replace the original call_llm function with a new one called `call_llm_robust`. This new function adds an automatic retry mechanism. The system will now attempt to call the API multiple times if it fails. This protects our system from temporary network problems.
# 
# Next we will validate all messages. A new function called `validate_mcp_message` will check every message passed between agents. It will confirm that the message is formatted correctly and contains all the required information. This prevents corrupted data from breaking our workflow.
# 
# We will also expand our agent team with a new `validator_agent`. This agent has one job. It acts as a fact checker. It compares the writer's draft against the researcher's summary to make sure the facts are consistent. This adds a layer of quality control to the system.
# 
# Finally we will create a self correcting workflow. We will upgrade the orchestrator to include a validation and revision loop. If the validator agent finds a problem with the draft the new logic will send the content back to the writer agent with feedback. The writer will then make a revision. The system can now correct its own mistakes to produce a more accurate final output.
import os

from dotenv import load_dotenv
from openai import OpenAI
from rich import print

load_dotenv()

import json
import time

def create_mcp_message(sender, content, metadata=None):
    """Creates a standardized MCP message."""
    return {
        "protocol_version": "1.0",
        "sender": sender,
        "content": content,
        "metadata": metadata or {}
    }



# New: Robust Component Controls
# This is a completely new section that introduces the core engineering principles of resilience and reliability.
# We've added two crucial functions here. The call_llm_robust function hardens our system against network failures by adding an automatic retry mechanism.
# The validate_mcp_message function acts as a critical guardrail, ensuring that every message passed between our agents is correctly formatted,
# which prevents data corruption in the workflow.
# Building Robust Components
# --- Hardening the call_llm Function ---
def call_llm_robust(system_prompt, user_content, retries=3, delay=5):
    """A more robust helper function to call the OpenAI API with retries."""
    for i in range(retries):
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
            print(f"API call failed on attempt {i+1}/{retries}. Error: {e}")
            if i < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                print("All retries failed.")
                return None

# --- The MCP Validator ---
def validate_mcp_message(message):
    """A simple validator to check the structure of an MCP message."""
    required_keys = ["protocol_version", "sender", "content", "metadata"]
    if not isinstance(message, dict):
        print(f"MCP Validation Failed: Message is not a dictionary.")
        return False
    for key in required_keys:
        if key not in message:
            print(f"MCP Validation Failed: Missing key '{key}'")
            return False
    print(f"MCP message from {message['sender']} validated successfully.")
    return True

# Building the Agents: The Specialists
# --- Agent 1: The Researcher ---
def researcher_agent(mcp_input):
    """This agent takes a research topic, finds information, and returns a summary."""
    print("\n[Researcher Agent Activated]")
    simulated_database = {
        "mediterranean diet": "The Mediterranean diet is rich in fruits, vegetables, whole grains, olive oil, and fish. Studies show it is associated with a lower risk of heart disease, improved brain health, and a longer lifespan."
    }
    research_topic = mcp_input['content']
    research_result = simulated_database.get(research_topic.lower(), "No information found.")
    system_prompt = "You are a research analyst. Synthesize the provided information into 3-4 concise bullet points."
    summary = call_llm_robust(system_prompt, research_result)
    print(f"Research summary created for: '{research_topic}'")
    return create_mcp_message(
        sender="ResearcherAgent",
        content=summary,
        metadata={"source": "Simulated Internal DB"}
    )

# --- Agent 2: The Writer ---
def writer_agent(mcp_input):
    """This agent takes research findings and writes a short blog post."""
    print("\n[Writer Agent Activated]")
    research_summary = mcp_input['content']
    system_prompt = "You are a content writer. Take the following research points and write a short, appealing blog post (approx. 150 words) with a catchy title."
    blog_post = call_llm_robust(system_prompt, research_summary)
    print("Blog post drafted.")
    return create_mcp_message(
        sender="WriterAgent",
        content=blog_post,
        metadata={"word_count": len(blog_post.split())}
    )

# --- Agent 3: The Validator ---
def validator_agent(mcp_input):
    """This agent fact-checks a draft against a source summary."""
    print("\n[Validator Agent Activated]")
    source_summary = mcp_input['content']['summary']
    draft_post = mcp_input['content']['draft']
    system_prompt = """
    You are a meticulous fact-checker. Determine if the 'DRAFT' is factually consistent with the 'SOURCE SUMMARY'.
    - If all claims in the DRAFT are supported by the SOURCE, respond with only the word \"pass\".
    - If the DRAFT contains any information not in the SOURCE, respond with \"fail\" and a one-sentence explanation.
    """
    validation_context = f"SOURCE SUMMARY:\n{source_summary}\n\nDRAFT:\n{draft_post}"
    validation_result = call_llm_robust(system_prompt, validation_context)
    print(f"Validation complete. Result: {validation_result}")
    return create_mcp_message(
        sender="ValidatorAgent",
        content=validation_result
    )
# New: Orchestrator Logic Controls
# Here, the original simple orchestrator has been replaced with the far more intelligent final_orchestrator. This new version is no longer just a linear task manager. It now includes a validation and revision loop. After the writer_agent produces a draft, the orchestrator delegates to the validator_agent. If the validation fails, the orchestrator sends the draft back to the writer with the validator's feedback, creating a powerful, self-correcting system that mimics a real-world editorial process.
# The Final Orchestrator with Validation Loop
def final_orchestrator(initial_goal):
    """Manages the full multi-agent workflow, including validation and revision."""
    print("="*50)
    print(f"[Orchestrator] Goal Received: '{initial_goal}'")
    print("="*50)

    # --- Step 1: Research ---
    print("\n[Orchestrator] Task 1: Research. Delegating to Researcher Agent.")
    research_topic = "Mediterranean Diet"
    mcp_to_researcher = create_mcp_message(sender="Orchestrator", content=research_topic)
    mcp_from_researcher = researcher_agent(mcp_to_researcher)

    if not validate_mcp_message(mcp_from_researcher) or not mcp_from_researcher['content']:
        print("Workflow failed due to invalid or empty message from Researcher.")
        return

    research_summary = mcp_from_researcher['content']
    print("\n[Orchestrator] Research complete.")

    # --- Step 2 & 3: Iterative Writing and Validation Loop ---
    final_output = "Could not produce a validated article."
    max_revisions = 2
    for i in range(max_revisions):
        print(f"\n[Orchestrator] Writing Attempt {i+1}/{max_revisions}")

        writer_context = research_summary
        if i > 0:
            writer_context += f"\n\nPlease revise the previous draft based on this feedback: {validation_result}"

        mcp_to_writer = create_mcp_message(sender="Orchestrator", content=writer_context)
        mcp_from_writer = writer_agent(mcp_to_writer)

        if not validate_mcp_message(mcp_from_writer) or not mcp_from_writer['content']:
            print("Aborting revision loop due to invalid message from Writer.")
            break
        draft_post = mcp_from_writer['content']

        # --- Validation Step ---
        print("\n[Orchestrator] Draft received. Delegating to Validator Agent.")
        validation_content = {"summary": research_summary, "draft": draft_post}
        mcp_to_validator = create_mcp_message(sender="Orchestrator", content=validation_content)
        mcp_from_validator = validator_agent(mcp_to_validator)

        if not validate_mcp_message(mcp_from_validator) or not mcp_from_validator['content']:
            print("Aborting revision loop due to invalid message from Validator.")
            break
        validation_result = mcp_from_validator['content']

        if "pass" in validation_result.lower():
            print("\n[Orchestrator] Validation PASSED. Finalizing content.")
            final_output = draft_post
            break
        else:
            print(f"\n[Orchestrator] Validation FAILED. Feedback: {validation_result}")
            if i < max_revisions - 1:
                print("Requesting revision.")
            else:
                print("Max revisions reached. Workflow failed.")

    # --- Step 4: Final Presentation ---
    print("\n" + "="*50)
    print("[Orchestrator] Workflow Complete. Final Output:")
    print("="*50)
    print(final_output)

if __name__ == '__main__':
    user_goal = "Create a blog post about the benefits of the Mediterranean diet."
    final_orchestrator(user_goal)