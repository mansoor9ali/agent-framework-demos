import asyncio
import os
import sys
from typing import Dict, Any, Tuple

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from azure.ai.evaluation import (
    GroundednessEvaluator,
    RelevanceEvaluator,
)
from dotenv import load_dotenv

from utils import create_openaichat_client

# Load environment variables
load_dotenv()


# =============================================================================
# 1. CONFIGURATION: Azure AI Evaluation SDK
# =============================================================================

def create_evaluator_model_config() -> Dict[str, Any]:
    """
    Configures the model settings for the Azure AI Evaluation SDK.
    Using dictionary-based config for OpenAI-compatible endpoints.

    Per Microsoft docs: For AI-assisted quality evaluators, you must specify
    a GPT model (gpt-4, gpt-4o, gpt-4o-mini) in your model_config.

    For OpenAI (non-Azure), you need to specify type: "openai"
    """
    return {
        "type": "openai",  # Required: specify connection type
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "model": os.getenv("OPENAI_MODEL_ID", "gpt-4o"),
    }


# =============================================================================
# 2. VERIFIER MODULE (Using Azure AI SDK)
# =============================================================================

class VerifierModule:
    """
    The Verifier Module acts as the auditing authority.
    It uses Azure AI SDK evaluators to produce a 'Pass/Fail' verdict.
    """

    def __init__(self):
        self.model_config = create_evaluator_model_config()
        # Initialize built-in evaluators from the SDK
        # GroundednessEvaluator checks if response is grounded in context
        self.groundedness_eval = GroundednessEvaluator(model_config=self.model_config)
        # RelevanceEvaluator checks if response is relevant to the query
        self.relevance_eval = RelevanceEvaluator(model_config=self.model_config)

    def verify(self, query: str, response: str, context: str) -> Tuple[bool, str]:
        """
        Performs the Second-Pass Verification.
        Returns: (passed: bool, feedback: str)
        """
        print("\n🔍 [Verifier] Auditing response using Azure AI Evaluators...")

        # 1. Check Groundedness (Hallucination Check)
        groundedness_result = self.groundedness_eval(
            query=query,
            response=response,
            context=context
        )

        # Parse score (usually 1-5 scale)
        groundedness_score = groundedness_result.get("groundedness", 0)
        groundedness_reason = groundedness_result.get("groundedness_reason", "No reason provided.")

        print(f"   📊 Groundedness Score: {groundedness_score}/5")

        # 2. Check Relevance
        relevance_result = self.relevance_eval(
            query=query,
            response=response
        )
        relevance_score = relevance_result.get("relevance", 0)
        print(f"   📊 Relevance Score: {relevance_score}/5")

        # Define Threshold (Graded Verification)
        if groundedness_score < 3:  # Threshold for 'Minor Inconsistency' vs 'Fatal Error'
            return False, f"FAIL: Groundedness check failed (Score: {groundedness_score}/5). Reason: {groundedness_reason}"

        if relevance_score < 3:
            return False, f"FAIL: Relevance check failed (Score: {relevance_score}/5)."

        return True, f"PASS: Response is grounded ({groundedness_score}/5) and relevant ({relevance_score}/5)."


# =============================================================================
# 3. PLANNER AGENT (The Worker)
# =============================================================================

def create_planner_agent(client: OpenAIChatClient) -> ChatAgent:
    """
    The Planner Agent generates the initial attempt.
    """
    return client.create_agent(
        name="Planner",
        model="gpt-5",  # User requested GPT-5
        instructions=(
            "You are a helpful AI assistant. Answer the user's questions based ONLY "
            "on the provided context. Do not hallucinate external information."
        )
    )


# =============================================================================
# 4. CONTROLLER (The Second-Pass Workflow)
# =============================================================================

async def run_second_pass_verification_workflow(query: str, context: str):
    """
    Orchestrates the Planner -> Verifier -> Correction loop.
    """
    client = create_openaichat_client()


    planner = create_planner_agent(client)
    verifier = VerifierModule()

    # Initial attempt
    print(f"\n👤 User Query: {query}")
    print(f"📄 Context: {context[:50]}...")

    # Construct prompt with context
    prompt = f"Context: {context}\n\nQuestion: {query}"

    # === Attempt 1 ===
    response_obj = await planner.run(prompt)
    current_response = response_obj.messages[-1].contents[0].text
    print(f"\n🤖 [Planner] Draft 1: {current_response}")

    # === Second-Pass Verification ===
    passed, feedback = verifier.verify(query=query, response=current_response, context=context)

    if passed:
        print(f"\n✅ {feedback}")
        print(f"\n🏆 Final Output: {current_response}")
    else:
        print(f"\n❌ {feedback}")
        print(f"\n🔄 [Controller] Triggering Self-Correction Loop...")

        # === Correction Phase ===
        # The Planner uses the Verifier's feedback as a new observation
        correction_prompt = (
            f"Here is your previous response: '{current_response}'\n\n"
            f"It failed verification with the following feedback: {feedback}\n\n"
            f"Please rewrite the response to address these specific errors based on the context."
        )

        correction_obj = await planner.run(correction_prompt)
        final_response = correction_obj.messages[-1].contents[0].text
        print(f"\n🤖 [Planner] Corrected Response: {final_response}")

        # Optional: Verify again (Double-Check)
        passed_2, feedback_2 = verifier.verify(query=query, response=final_response, context=context)
        if passed_2:
            print(f"\n✅ Correction Verified: {feedback_2}")
        else:
            print(f"\n⚠️ Correction still failed: {feedback_2}. Escalating to human.")


# =============================================================================
# 5. MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    # Scenario: High-stakes information retrieval where accuracy is critical [cite: 11, 27]

    # Context (Source of Truth)
    wiki_context = (
        "The Alpine Explorer Tent is the most waterproof tent in our lineup. "
        "It costs $120. The Adventure Dining Table weighs 5kg."
    )

    # 1. Success Case
    asyncio.run(run_second_pass_verification_workflow(
        query="Which tent is waterproof and how much is it?",
        context=wiki_context
    ))

    print("\n" + "=" * 50 + "\n")

    # 2. Failure Case (Inducing Hallucination to trigger Verification)
    # Planner might hallucinate that the Dining Table is waterproof if not careful.
    asyncio.run(run_second_pass_verification_workflow(
        query="Is the Adventure Dining Table waterproof?",
        context=wiki_context
    ))