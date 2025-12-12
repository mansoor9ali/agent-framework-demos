import asyncio
import math
import json
import os
import sys
from typing import List, Optional
from dataclasses import dataclass

# Add parent directory to path for utils import
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_framework import ChatAgent
from agent_framework.openai import OpenAIChatClient
from dotenv import load_dotenv

from utils import create_openaichat_client

load_dotenv()


# =============================================================================
# 1. SETUP: Mock Tools & Configuration
# =============================================================================

# A simple mock search tool to make this example runnable without API keys
async def mock_search_tool(query: str) -> str:
    """Simulates a search engine returning results."""
    # Simulated knowledge base
    knowledge = {
        "lithium": "Lithium mining can cause soil degradation and water loss.",
        "pollution": "Industrial pollution affects groundwater quality.",
        "solution": "New extraction technologies reduce water usage by 40%."
    }

    # Simple keyword match
    results = []
    for k, v in knowledge.items():
        if k in query.lower():
            results.append(v)

    if not results:
        return "No specific data found, but general research suggests environmental impact is high."
    return " | ".join(results)


# =============================================================================
# 2. DATA STRUCTURES (The Tree)
# =============================================================================

@dataclass
class Reflection:
    score: float  # 0.0 to 1.0
    critique: str
    found_solution: bool


class Node:
    def __init__(self, content: str, parent: Optional['Node'] = None):
        self.content = content  # The action/thought taken at this step
        self.parent = parent
        self.children: List['Node'] = []

        # MCTS Stats
        self.value = 0.0  # Cumulative reward
        self.visits = 0
        self.reflection: Optional[Reflection] = None

    @property
    def depth(self) -> int:
        d = 0
        curr = self
        while curr.parent:
            d += 1
            curr = curr.parent
        return d

    def upper_confidence_bound(self, exploration_weight: float = 1.0) -> float:
        """Standard UCB formula to balance Exploration vs Exploitation."""
        if self.visits == 0:
            return float('inf')  # Always visit unvisited nodes first

        # Exploitation: Average value
        average_reward = self.value / self.visits

        # Exploration: UCB term
        # Avoid log(0) for root
        parent_visits = self.parent.visits if self.parent else self.visits
        exploration_term = math.sqrt(math.log(parent_visits) / self.visits)

        return average_reward + (exploration_weight * exploration_term)

    def best_child(self) -> Optional['Node']:
        if not self.children:
            return None
        # Select child with highest UCB
        return max(self.children, key=lambda c: c.upper_confidence_bound())

    def get_trajectory(self) -> List[str]:
        """Returns the full path of steps from root to this node."""
        path = []
        curr = self
        while curr:
            path.append(curr.content)
            curr = curr.parent
        return path[::-1]  # Reverse to get Root -> Leaf order


# =============================================================================
# 3. SPECIALIZED AGENTS
# =============================================================================

class LATSAgents:
    def __init__(self, client: OpenAIChatClient):
        self.client = client

    def create_generator(self) -> ChatAgent:
        """
        Role: Expansion
        Generates N diverse candidate next steps based on the current trajectory.
        """
        return self.client.create_agent(
            name="Generator",
            model="gpt-4o",
            instructions=(
                "You are an AI decision planner. "
                "Given a history of actions, propose 3 distinct, diverse 'next steps' to solve the user's problem. "
                "Output MUST be a raw JSON list of strings. Example: "
                "[\"Search for X\", \"Calculate Y\", \"Draft outline\"]"
            )
        )

    def create_reflector(self) -> ChatAgent:
        """
        Role: Simulation/Reflection
        Evaluates a step and assigns a reward score (0-10).
        """
        return self.client.create_agent(
            name="Reflector",
            model="gpt-4o",
            instructions=(
                "You are a strict Judge. Evaluate the latest step in the context of the goal. "
                "1. Provide a 'score' from 0 to 10 (10 is a perfect solution). "
                "2. Provide a short 'critique'. "
                "3. Boolean 'solved': true if the goal is fully achieved. "
                "Output raw JSON: {\"score\": 8, \"critique\": \"...\", \"solved\": false}"
            )
        )


# =============================================================================
# 4. THE LATS ENGINE (The Algorithm)
# =============================================================================

class LATSEngine:
    def __init__(self, client: OpenAIChatClient, max_iterations=5):
        self.agents = LATSAgents(client)
        self.generator = self.agents.create_generator()
        self.reflector = self.agents.create_reflector()
        self.max_iterations = max_iterations
        self.root: Optional[Node] = None

    async def search(self, user_query: str):
        print(f"\n🚀 STARTING LATS SEARCH: \"{user_query}\"")

        # 1. Initialize Root
        self.root = Node(content=f"Goal: {user_query}")

        for i in range(self.max_iterations):
            print(f"\n--- 🔄 Iteration {i + 1}/{self.max_iterations} ---")

            # A. SELECTION
            # Traverse tree to find a leaf node to expand
            node_to_expand = self._select(self.root)
            print(f"📍 Selected Node (Depth {node_to_expand.depth}): {node_to_expand.content[:50]}...")

            if node_to_expand.reflection and node_to_expand.reflection.found_solution:
                print("✅ Solution found in selection phase!")
                return node_to_expand.get_trajectory()

            # B. EXPANSION
            # Generate candidates
            trajectory = node_to_expand.get_trajectory()
            print("🌱 Expanding...")
            candidates = await self._expand(trajectory)

            if not candidates:
                print("⚠️ No candidates generated. Backtracking...")
                continue

            # C. SIMULATION (Reflection)
            # Evaluate each candidate and add to tree
            for candidate_text in candidates:
                # Create node
                child_node = Node(content=candidate_text, parent=node_to_expand)

                # Simulate/Reflect (Get Reward)
                reflection = await self._reflect(trajectory + [candidate_text], user_query)
                child_node.reflection = reflection
                child_node.visits = 1
                child_node.value = reflection.score  # Initialize with its own score

                # Add to tree
                node_to_expand.children.append(child_node)

                print(
                    f"   📝 Simulated Branch: \"{candidate_text[:40]}...\" | Score: {reflection.score} | Solved: {reflection.found_solution}")

                # D. BACKPROPAGATION
                # Propagate the score up the tree
                self._backpropagate(child_node, reflection.score)

                # Check for termination
                if reflection.found_solution:
                    print("\n🎉 OPTIMAL SOLUTION FOUND!")
                    return child_node.get_trajectory()

        print("\n⏹️ Max iterations reached. Returning best path found.")
        best_leaf = self._get_best_leaf(self.root)
        return best_leaf.get_trajectory()

    def _select(self, node: Node) -> Node:
        """Recursive UCB Selection"""
        # If node has no children, it's a leaf -> expand it
        if not node.children:
            return node

        # If node has children but we haven't explored them all?
        # (In standard LATS, we usually expand all at once, so we just pick best child)
        best = node.best_child()
        return self._select(best)

    async def _expand(self, history: List[str]) -> List[str]:
        """Calls Generator Agent to get N options"""
        context = "\n".join([f"Step {i}: {step}" for i, step in enumerate(history)])
        try:
            response = await self.generator.run(f"History:\n{context}\n\nPropose 3 possible next steps.")
            text = response.messages[-1].contents[0].text
            # Clean JSON
            text = text.replace("```json", "").replace("```", "").strip()
            candidates = json.loads(text)
            return candidates if isinstance(candidates, list) else []
        except Exception as e:
            print(f"Expansion Error: {e}")
            return []

    async def _reflect(self, full_path: List[str], goal: str) -> Reflection:
        """Calls Reflector Agent to score the path"""
        context = "\n".join([f"Step {i}: {step}" for i, step in enumerate(full_path)])
        try:
            prompt = f"Goal: {goal}\n\nCurrent Trajectory:\n{context}\n\nEvaluate progress."
            response = await self.reflector.run(prompt)
            text = response.messages[-1].contents[0].text
            text = text.replace("```json", "").replace("```", "").strip()
            data = json.loads(text)

            # Normalize score 0-1 for math, but keep 0-10 for display
            normalized_score = float(data.get("score", 0)) / 10.0

            return Reflection(
                score=normalized_score,
                critique=data.get("critique", ""),
                found_solution=data.get("solved", False)
            )
        except Exception as e:
            print(f"Reflection Error: {e}")
            return Reflection(0.0, "Error", False)

    def _backpropagate(self, node: Node, score: float):
        """Updates values up the tree"""
        curr = node
        while curr:
            curr.visits += 1
            # Running Average Update
            curr.value = curr.value + (score - curr.value) / curr.visits
            curr = curr.parent

    def _get_best_leaf(self, node: Node) -> Node:
        """Finds highest valued leaf at end of search"""
        if not node.children:
            return node
        # Pick child with highest value (Exploitation only)
        best_child = max(node.children, key=lambda c: c.value)
        return self._get_best_leaf(best_child)


# =============================================================================
# 5. MAIN ENTRY POINT
# =============================================================================

async def main():
    # Setup Client
    client = create_openaichat_client()

    # Initialize LATS
    lats = LATSEngine(client, max_iterations=3)  # Low iterations for demo speed

    # Run a complex query requiring reasoning
    query = "Write a research report on Lithium Pollution."

    final_trajectory = await lats.search(query)

    print(f"\n\n{'=' * 60}")
    print("🏆 FINAL LATS TRAJECTORY")
    print(f"{'=' * 60}")
    for i, step in enumerate(final_trajectory):
        print(f"[{i}] {step}")


if __name__ == "__main__":
    asyncio.run(main())