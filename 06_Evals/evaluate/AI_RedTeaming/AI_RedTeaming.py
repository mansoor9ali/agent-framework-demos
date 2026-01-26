from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Optional, Dict, Any, Protocol, TypeAlias
import json
import os
import time
from pprint import pprint
from dotenv import load_dotenv


# ## Understanding AI Red Teaming Agent's capabilities
#
# The Azure AI Evaluation SDK's `RedTeam` functionality evaluates AI systems against adversarial prompts across multiple dimensions:
#
# 1. **Risk Categories**: Different content risk categories your AI system might generate
#    - **Violence**: Content related to physical harm, weapons, or dangerous activities
#    - **HateUnfairness**: Content related to discrimination, bias, or prejudice
#    - **Sexual**: Explicit sexual content
#    - **SelfHarm**: Content related to self-injury or suicide
#    - **ProtectedMaterial**: Copyrighted or protected intellectual property
#    - **CodeVulnerability**: Code that contains security vulnerabilities
#    - **UngroundedAttributes**: Claims not supported by evidence
#
#    **Cloud-Only Risk Categories** (available only when using Azure AI Foundry projects):
#    - **ProhibitedActions**: Instructions for illegal or harmful activities
#    - **SensitiveDataLeakage**: Exposure of personal or confidential information
#    - **TaskAdherence**: Whether the AI follows intended task instructions
#
# 2. **Attack Strategies**: Along with standard unmodified prompts which are sent by default as the `baseline`, you can specify different transformations of prompts to elicit undesired content. You can also use `AttackStrategy.Compose()` to layer two strategies in one attack.


import asyncio
from azure.identity import DefaultAzureCredential
from azure.ai.evaluation.red_team import RedTeam, RiskCategory, AttackStrategy, SupportedLanguages
from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import (
    AgentTaxonomyInput,
    AzureAIAgentTarget,
    DailyRecurrenceSchedule,
    EvaluationScheduleTask,
    EvaluationTaxonomy,
    RecurrenceTrigger,
    RiskCategory as ProjectsRiskCategory,
    Schedule,
)

# OpenAI imports
from openai import AzureOpenAI

load_dotenv()

# Azure AI Project information
azure_ai_project = os.environ.get("AZURE_PROJECT_ENDPOINT")

# Create the `RedTeam` instance with comprehensive risk categories
# Note: Some categories like ProhibitedActions, SensitiveDataLeakage, and TaskAdherence
# are only available in cloud red teaming scenarios
red_team = RedTeam(
    azure_ai_project=azure_ai_project,
    credential= DefaultAzureCredential(),
    risk_categories=[
        RiskCategory.Violence,
        RiskCategory.HateUnfairness,
        RiskCategory.Sexual,
        RiskCategory.SelfHarm,
        RiskCategory.ProtectedMaterial,
        RiskCategory.CodeVulnerability,
        RiskCategory.UngroundedAttributes,
    ],
    num_objectives=1,
)

# Define a simple callback function that always returns a fixed response
def financial_advisor_callback(query: str) -> str:  # noqa: ARG001
    return "I'm a financial advisor assistant. I can help with investment advice and financial planning within legal and ethical guidelines."

async def main():
    # Display all available attack strategies in the Azure AI Evaluation SDK
    print("🎯 All Available Attack Strategies in Azure AI Evaluation SDK:")
    print("=" * 70)
    print()

    # Get all AttackStrategy attributes
    attack_strategies = [attr for attr in dir(AttackStrategy) if not attr.startswith("_")]

    print(f"Total number of attack strategies: {len(attack_strategies)}")
    print()

    # Print each strategy
    for i, strategy in enumerate(attack_strategies, 1):
        strategy_value = getattr(AttackStrategy, strategy)
        print(f"{i:2}. {strategy}: {strategy_value}")

    print()
    print("=" * 70)
    print("Note: Use AttackStrategy.Compose([strategy1, strategy2]) to combine strategies")

    # Run the red team scan called "Basic-Callback-Scan" with limited scope for this basic example
    # This will test 1 objective prompt for each of Violence and HateUnfairness categories with the Flip strategy
    result = await red_team.scan(
        target=financial_advisor_callback,
        scan_name="Basic-Callback-Scan",
        attack_strategies=[AttackStrategy.Flip],
        output_path="red_team_output.json",
    )
    # create a new Red Team instance with the `language` set to `SupportedLanguages.Spanish`
    red_team_spanish = RedTeam(
        azure_ai_project=azure_ai_project,
        credential= DefaultAzureCredential(),
        language=SupportedLanguages.Spanish,
        num_objectives=1,
    )








if __name__ == '__main__':
    asyncio.run(main())