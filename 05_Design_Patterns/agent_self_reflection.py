import asyncio
import math
import os
import sys
import time
import pandas as pd
from typing import Any, Dict

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
from utils import create_deepseek_client
from agent_framework import ChatAgent, ChatMessage

# Azure AI Evaluation SDK - using official Microsoft evaluators
from azure.ai.evaluation import GroundednessEvaluator


"""
Self-Reflection LLM Runner

Reflexion: language agents with verbal reinforcement learning.
Noah Shinn, Federico Cassano, Ashwin Gopinath, Karthik Narasimhan, and Shunyu Yao. 2023.
In Proceedings of the 37th International Conference on Neural Information Processing Systems (NIPS '23). Curran Associates Inc., Red Hook, NY, USA, Article 377, 8634–8652.
https://arxiv.org/abs/2303.11366 

This module implements a self-reflection loop for LLM responses using groundedness evaluation.
It loads prompts from a JSONL file, runs them through an LLM with self-reflection,
and saves the results.

Now using Azure AI Evaluation SDK for groundedness evaluation:
https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/develop/evaluate-sdk

Usage as CLI:
    python agent_self_reflection.py

Usage as CLI with extra options:
    python agent_self_reflection.py --input resources/suboptimal_groundedness_prompts.jsonl \\
                              --output resources/results.jsonl \\
                              --max-reflections 3 \\
                              -n 10  # Optional: process only first 10 prompts
"""
load_dotenv()

DEFAULT_AGENT_MODEL = os.getenv("DEEPSEEK_MODEL_ID")
DEFAULT_JUDGE_MODEL = os.getenv("DEEPSEEK_MODEL_ID")


def create_evaluator_model_config(judge_model: str = None) -> Dict[str, Any]:
    """
    Create model configuration for Azure AI Evaluation SDK.

    Per Microsoft docs: For AI-assisted quality evaluators, you must specify
    a GPT model (gpt-4, gpt-4o, gpt-4o-mini) in your model_config.

    For OpenAI (non-Azure), you need to specify type: "openai"

    Args:
        judge_model: Optional model name override
    Returns:
        Dictionary with model configuration
    """
    return {
        "type": "openai",  # Required: specify connection type for OpenAI-compatible endpoints
        "api_key": os.getenv("DEEPSEEK_API_KEY"),
        "base_url": os.getenv("DEEPSEEK_BASE_URL"),
        "model": judge_model or DEFAULT_JUDGE_MODEL,
    }


def create_groundedness_evaluator(judge_model: str = None) -> GroundednessEvaluator:
    """
    Create a groundedness evaluator using Azure AI Evaluation SDK.

    Args:
        judge_model: Model deployment name for evaluation
    Returns:
        Configured GroundednessEvaluator from Azure AI Evaluation SDK
    """
    model_config = create_evaluator_model_config(judge_model)
    return GroundednessEvaluator(model_config=model_config)


async def execute_query_with_self_reflection(
        *,
        agent: ChatAgent,
        full_user_query: str,
        context: str,
        evaluator: GroundednessEvaluator,
        max_self_reflections: int = 3,
) -> dict[str, Any]:
    """
    Execute a query with self-reflection loop.

    Args:
        agent: ChatAgent instance to use for generating responses
        full_user_query: Complete prompt including system prompt, user request, and context
        context: Context document for groundedness evaluation
        evaluator: Groundedness evaluator function
        max_self_reflections: Maximum number of self-reflection iterations

    Returns:
        Dictionary containing:
            - best_response: The best response achieved
            - best_response_score: Best groundedness score
            - best_iteration: Iteration number where best score was achieved
            - iteration_scores: List of groundedness scores for each iteration
            - messages: Full conversation history
            - usage_metadata: Token usage information
            - num_retries: Number of iterations performed
            - total_groundedness_eval_time: Time spent on evaluations (seconds)
            - total_end_to_end_time: Total execution time (seconds)
    """
    messages = [ChatMessage(role="user", text=full_user_query)]

    best_score = 0
    max_score = 5
    best_response = None
    best_iteration = 0
    raw_response = None
    total_groundedness_eval_time = 0.0
    start_time = time.time()
    iteration_scores = []  # Store all iteration scores in structured format
    i = 0  # Initialize loop counter

    for i in range(max_self_reflections):
        print(f"  Self-reflection iteration {i + 1}/{max_self_reflections}...")

        raw_response = await agent.run(messages=messages)
        agent_response = raw_response.text

        # Evaluate groundedness
        start_time_eval = time.time()
        groundedness_res = evaluator(
            query=full_user_query,
            response=agent_response,
            context=context
        )
        end_time_eval = time.time()
        total_groundedness_eval_time += (end_time_eval - start_time_eval)

        feedback = groundedness_res.get('groundedness_reason', 'No reason provided')
        raw_score = groundedness_res.get('groundedness', 0)

        # Handle NaN or invalid scores
        if raw_score is None or (isinstance(raw_score, float) and math.isnan(raw_score)):
            print(f"  ⚠️ Invalid score received (NaN), using 0")
            score = 0
        else:
            score = int(raw_score)

        # Store score in structured format
        iteration_scores.append(score)

        # Show groundedness score
        print(f"  Groundedness score: {score}/{max_score}")

        # Update best response if improved
        if score > best_score:
            if best_score > 0:
                print(f"  ✓ Score improved from {best_score} to {score}/{max_score}")
            best_score = score
            best_response = agent_response
            best_iteration = i + 1
            if score == max_score:
                print(f"  ✓ Perfect groundedness score achieved!")
                break
        else:
            print(f"  → No improvement (score: {score}/{max_score}). Trying again...")

        # Add to conversation history
        messages.append(ChatMessage(role="assistant", text=agent_response))

        # Request improvement
        reflection_prompt = (
            f"The groundedness score of your response is {score}/{max_score}. "
            f"Explanation for score: [{feedback}]. "
            f"Reflect on your answer and improve it to get the maximum score of {max_score} "
            f"considering the explanation. Now please provide an updated response, taking into "
            f"account the feedback, but make your answer sound as if it was your first response. "
            f"Don't refer to the feedback in your answer."
        )
        messages.append(ChatMessage(role="user", text=reflection_prompt))

    end_time = time.time()
    latency = end_time - start_time

    # Handle edge case where no response improved the score
    if best_response is None and raw_response is not None and len(raw_response.messages) > 0:
        best_response = raw_response.messages[0].text
        best_iteration = i + 1

    return {
        "best_response": best_response,
        "best_response_score": best_score,
        "best_iteration": best_iteration,
        "iteration_scores": iteration_scores,  # Structured list of all scores
        "messages": [message.to_json() for message in messages],
        "num_retries": i + 1,
        "total_groundedness_eval_time": total_groundedness_eval_time,
        "total_end_to_end_time": latency,
    }


async def run_self_reflection_batch(
        input_file: str,
        output_file: str,
        agent_model: str = DEFAULT_AGENT_MODEL,
        judge_model: str = DEFAULT_JUDGE_MODEL,
        max_self_reflections: int = 3,
        env_file: str | None = None,
        limit: int | None = None
):
    """
    Run self-reflection on a batch of prompts.

    Args:
        input_file: Path to input JSONL file with prompts
        output_file: Path to save output JSONL file
        agent_model: Model to use for generating responses
        judge_model: Model to use for groundedness evaluation
        max_self_reflections: Maximum number of self-reflection iterations
        env_file: Optional path to .env file
        limit: Optional limit to process only the first N prompts
    """
    # Load environment variables
    if env_file and os.path.exists(env_file):
        load_dotenv(env_file, override=True)
    else:
        load_dotenv(override=True)

    # Create agent, it loads environment variables AZURE_OPENAI_API_KEY and AZURE_OPENAI_ENDPOINT automatically
    agent =  create_deepseek_client().create_agent(
        instructions="You are a helpful agent.",
        model_id=agent_model,
    )

    # Load input data
    print(f"Loading prompts from: {input_file}")
    df = pd.read_json(input_file, lines=True)
    print(f"Loaded {len(df)} prompts")

    # Apply limit if specified
    if limit is not None and limit > 0:
        df = df.head(limit)
        print(f"Processing first {len(df)} prompts (limited by -n {limit})")

    # Validate required columns
    required_columns = ['system_instruction', 'user_request', 'context_document',
                        'full_prompt', 'domain', 'type', 'high_level_type']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Input file missing required columns: {missing_columns}")

    # Configure clients
    print(f"Configuring OpenAI client...")

    print(f"Creating groundedness evaluator with model: {judge_model}")
    evaluator = create_groundedness_evaluator(judge_model)

    # Process each prompt
    print(f"Max self-reflections: {max_self_reflections}\n")

    results = []
    for counter, (idx, row) in enumerate(df.iterrows(), start=1):
        print(f"[{counter}/{len(df)}] Processing prompt {row.get('original_index', idx)}...")

        try:
            result = await execute_query_with_self_reflection(
                agent=agent,
                full_user_query=row['full_prompt'],
                context=row['context_document'],
                evaluator=evaluator,
                max_self_reflections=max_self_reflections,
            )

            # Prepare result data
            result_data = {
                "original_index": row.get('original_index', idx),
                "domain": row['domain'],
                "question_type": row['type'],
                "high_level_type": row['high_level_type'],
                "full_prompt": row['full_prompt'],
                "system_prompt": row['system_instruction'],
                "user_request": row['user_request'],
                "context_document": row['context_document'],
                "agent_response_model": agent_model,
                "agent_response": result,
                "error": None,
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            results.append(result_data)

            print(f"  ✓ Completed with score: {result['best_response_score']}/5 "
                  f"(best at iteration {result['best_iteration']}/{result['num_retries']}, "
                  f"time: {result['total_end_to_end_time']:.1f}s)\n")

        except Exception as e:
            print(f"  ✗ Error: {str(e)}\n")

            # Save error information
            error_data = {
                "original_index": row.get('original_index', idx),
                "domain": row['domain'],
                "question_type": row['type'],
                "high_level_type": row['high_level_type'],
                "full_prompt": row['full_prompt'],
                "system_prompt": row['system_instruction'],
                "user_request": row['user_request'],
                "context_document": row['context_document'],
                "agent_response_model": agent_model,
                "agent_response": None,
                "error": str(e),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            }
            results.append(error_data)
            continue

    # Create DataFrame and save
    results_df = pd.DataFrame(results)

    print(f"\nSaving results to: {output_file}")
    results_df.to_json(output_file, orient='records', lines=True)

    # Generate detailed summary
    successful_runs = results_df[results_df['error'].isna()]
    failed_runs = results_df[results_df['error'].notna()]

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Total prompts processed: {len(results_df)}")
    print(f"  ✓ Successful: {len(successful_runs)}")
    print(f"  ✗ Failed: {len(failed_runs)}")

    if len(successful_runs) > 0:
        # Extract scores and iteration data from nested agent_response dict
        best_scores = [r['best_response_score'] for r in successful_runs['agent_response'] if r is not None]
        iterations = [r['best_iteration'] for r in successful_runs['agent_response'] if r is not None]
        iteration_scores_list = [r['iteration_scores'] for r in successful_runs['agent_response'] if
                                 r is not None and 'iteration_scores' in r]

        if best_scores:
            avg_score = sum(best_scores) / len(best_scores)
            perfect_scores = sum(1 for s in best_scores if s == 5)
            print(f"\nGroundedness Scores:")
            print(f"  Average best score: {avg_score:.2f}/5")
            print(
                f"  Perfect scores (5/5): {perfect_scores}/{len(best_scores)} ({100 * perfect_scores / len(best_scores):.1f}%)")

            # Calculate improvement metrics
            if iteration_scores_list:
                first_scores = [scores[0] for scores in iteration_scores_list if len(scores) > 0]
                last_scores = [scores[-1] for scores in iteration_scores_list if len(scores) > 0]
                improvements = [last - first for first, last in zip(first_scores, last_scores)]
                improved_count = sum(1 for imp in improvements if imp > 0)

                if first_scores and last_scores:
                    avg_first_score = sum(first_scores) / len(first_scores)
                    avg_last_score = sum(last_scores) / len(last_scores)
                    avg_improvement = sum(improvements) / len(improvements)

                    print(f"\nImprovement Analysis:")
                    print(f"  Average first score: {avg_first_score:.2f}/5")
                    print(f"  Average final score: {avg_last_score:.2f}/5")
                    print(f"  Average improvement: +{avg_improvement:.2f}")
                    print(
                        f"  Responses that improved: {improved_count}/{len(improvements)} ({100 * improved_count / len(improvements):.1f}%)")

            # Show iteration statistics
            if iterations:
                avg_iteration = sum(iterations) / len(iterations)
                first_try = sum(1 for it in iterations if it == 1)
                print(f"\nIteration Statistics:")
                print(f"  Average best iteration: {avg_iteration:.2f}")
                print(f"  Best on first try: {first_try}/{len(iterations)} ({100 * first_try / len(iterations):.1f}%)")

    print("=" * 60)


# =============================================================================
# CONFIGURATION - Fixed Values (No command-line arguments)
# =============================================================================

# Input/Output paths
INPUT_FILE = "resources/suboptimal_groundedness_prompts.jsonl"
OUTPUT_FILE = "resources/results.jsonl"

# Model configuration
AGENT_MODEL = DEFAULT_AGENT_MODEL  # Uses DEEPSEEK_MODEL_ID from .env
JUDGE_MODEL = DEFAULT_JUDGE_MODEL  # Uses DEEPSEEK_MODEL_ID from .env

# Self-reflection settings
MAX_REFLECTIONS = 3  # Maximum number of self-reflection iterations
LIMIT = None  # Set to a number to process only first N prompts (e.g., 5), or None for all


async def main():
    """Main entry point with fixed configuration values."""
    print("=" * 60)
    print("🔄 Self-Reflection LLM Runner")
    print("   Using Azure AI Evaluation SDK for Groundedness")
    print("=" * 60)
    print(f"\n📋 Configuration:")
    print(f"   Input file:       {INPUT_FILE}")
    print(f"   Output file:      {OUTPUT_FILE}")
    print(f"   Agent model:      {AGENT_MODEL}")
    print(f"   Judge model:      {JUDGE_MODEL}")
    print(f"   Max reflections:  {MAX_REFLECTIONS}")
    print(f"   Limit:            {LIMIT if LIMIT else 'All prompts'}")
    print()

    # Run the batch processing
    try:
        await run_self_reflection_batch(
            input_file=INPUT_FILE,
            output_file=OUTPUT_FILE,
            agent_model=AGENT_MODEL,
            judge_model=JUDGE_MODEL,
            max_self_reflections=MAX_REFLECTIONS,
            env_file=None,
            limit=LIMIT
        )
        print("\n✓ Processing complete!")

    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    exit(asyncio.run(main()))