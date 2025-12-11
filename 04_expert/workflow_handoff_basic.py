# pip install agent-framework-devui==1.0.0b251016
from typing import Any

from agent_framework import WorkflowOutputEvent, ChatMessage, Role, HandoffBuilder
from agent_framework_devui import serve
from dotenv import load_dotenv
from rich import print

from utils import create_deepseek_client

# Load environment variables from .env file
load_dotenv()




historyTutor = create_deepseek_client().create_agent(
    instructions="You provide assistance with historical queries. Explain important events and context clearly. Only respond about history.",
     name="history_tutor",
    description="Specialist agent for historical questions")

mathTutor = create_deepseek_client().create_agent(
    instructions="You provide help with math problems. Explain your reasoning at each step and include examples. Only respond about math.",
     name="math_tutor",
     description="Specialist agent for math questions")

triageAgent = create_deepseek_client().create_agent(
    instructions="You determine which agent to use based on the user's homework question. ALWAYS handoff to another agent.",
     name="triage_agent",
     description="Routes messages to the appropriate specialist agent")

# var workflow = AgentWorkflowBuilder.StartHandoffWith(triageAgent)
#     .WithHandoffs(triageAgent, [mathTutor, historyTutor]) // Triage can route to either specialist
#     .WithHandoff(mathTutor, triageAgent)                  // Math tutor can return to triage
#     .WithHandoff(historyTutor, triageAgent)               // History tutor can return to triage
#     .Build();

workflow = (
    HandoffBuilder(
        name="homework_handoff",
        description="A workflow that hands off between a triage agent and specialist tutors.",)
    .participants([triageAgent, mathTutor, historyTutor])
    .set_coordinator("triage_agent")
    .add_handoff("triage_agent", ["math_tutor", "history_tutor"])
    .add_handoff("math_tutor", "triage_agent")
    .add_handoff("history_tutor", "triage_agent")
    .build()
)

async def main() -> None:
    completion: WorkflowOutputEvent | None = None
    async for event in workflow.run_stream("Write a tagline for a budget-friendly eBike."):
        if isinstance(event, WorkflowOutputEvent):
            completion = event


    if completion:
        print("===== Final Conversation =====",flush=True)
        messages: list[ChatMessage] | Any = completion.data
        print(f"Total messages: {len(messages)}", flush=True)
        for i, msg in enumerate(messages, start=1):
            name = msg.author_name or ("assistant" if msg.role == Role.ASSISTANT else "user")
            print(f"{'-' * 60}\n{i:02d} [{name}]\n{msg.text}")





if __name__ == "__main__":
    #asyncio.run(main())
    serve(entities=[workflow], port=8093, auto_open=True)
