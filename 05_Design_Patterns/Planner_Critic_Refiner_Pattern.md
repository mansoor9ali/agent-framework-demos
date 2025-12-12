# Design Document: Planner-Critic-Refiner Pattern

**Version:** 1.0
**Context:** Agentic AI Solution Design Patterns
 

---

## 1. Executive Summary
The **Planner-Critic-Refiner** pattern is a robust architectural strategy designed to maximize the reliability and accuracy of Agentic AI solutions. It addresses the inherent fallibility of "single-pass" planning by establishing an iterative feedback loop between a planning agent and a critical review agent. This pattern ensures that complex, multi-step plans are thoroughly vetted and optimized before any execution takes place, making it ideal for high-stakes scenarios where errors must be minimized.

---

## 2. Problem Statement: The Single-Pass Flaw
While patterns like ReAct combine reasoning with action, they often struggle with highly complex or multi-step tasks.
* **Incompleteness:** A plan generated in a single pass by an LLM is often incomplete or inefficient, especially if initial information is limited.
* **Logical Gaps:** The LLM may hallucinate resource availability or skip logical prerequisites (e.g., booking a venue before confirming the attendee count).
* **Risk:** Executing a flawed plan immediately can lead to wasted resources and failed objectives.

---

## 3. Solution Overview: The Feedback Loop
The Planner-Critic-Refiner pattern focuses on improving the quality and completeness of a plan *before* execution. It creates a cycle of self-correction where the agent critiques its own strategy.

### Core Roles
1.  **The Planner:** Responsible for generating the initial high-level plan based on the user's request.
2.  **The Critic:** A specialized module or agent that evaluates the proposed plan against specific criteria (logic, safety, constraints) without performing actions.
3.  **The Refiner:** The Planner assumes this role to incorporate the Critic's feedback and produce a revised, improved plan.

---

## 4. Operational Workflow

1.  **Initial Planning:** The Planner Agent analyzes the task and produces a preliminary plan.
2.  **Assessment:** The Critic Agent receives the plan and assesses it for flaws, missing steps, redundancies, or logical inconsistencies.
3.  **Feedback:** The Critic generates specific feedback and reprompts the Planner with instructions for improvement.
4.  **Refinement:** The Planner (acting as Refiner) ingests the feedback and outputs a refined plan.
5.  **Iteration:** This cycle repeats until the plan meets a defined quality threshold.
6.  **Execution:** Only after the plan is validated does the solution proceed to execute actions.

*Note: Typically, no external actions (tool calls) are performed during the critique loop; the focus is purely on reasoning and strategy optimization.*

---

## 5. System Architecture

### 5.1 The Critic Module
The Critic is a new body of logic designed to identify potential failures. It accesses the LLM using distinct system prompts and evaluation criteria, such as:
* **Resource Availability:** Checking if the plan accounts for necessary budgets or tools.
* **Logical Flow:** Ensuring steps occur in the correct dependency order.
* **Safety & Constraints:** Verifying compliance with user restrictions.

### 5.2 Module Placement
* **Separate Agent:** The Critic logic is often isolated in its own "Critic Agent."
* **Bundled Agent:** For simpler architectures, the Critic logic can be bundled with the Controller or the Planner within a single agent.

---

## 6. Operational Example: Venue Planning
*Scenario: An agent plans a team offsite.*

* **Draft Plan:** "Book Grand Hotel for 15 people."
* **Critic Feedback:** "Flaw detected. The plan assumes venue availability without a pre-check. The plan also lacks a budget step for catering."
* **Refinement:** The agent updates the plan to: "1. Check budget. 2. Call Grand Hotel to check availability. 3. If available, book."

---

## 7. Trade-Off Analysis

This pattern prioritizes **Correctness** over **Speed**.

### Benefits
* **High Reliability:** Drastically reduces the chance of execution errors by preemptively catching logic gaps.
* **Self-Correction:** Allows the system to fix its own mistakes before they become costly real-world actions.
* **Suitability:** Excellent for high-stakes tasks where accuracy is non-negotiable.

### Drawbacks
* **High Latency:** The iterative loop requires multiple LLM inference calls before the first action is taken, making it significantly slower than ReAct.
* **Increased Cost:** Higher token consumption due to the back-and-forth between Planner and Critic.
* **Complexity:** Requires intricate prompt engineering for three distinct roles (Planner, Critic, Refiner) and complex controller logic to manage the loop.

---
 