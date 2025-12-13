# Design Document: Second-Pass Verification Pattern

**Version:** 1.0
**Context:** Agentic AI Solution Design Patterns
 
---

## 1. Executive Summary
The **Second-Pass Verification** pattern (also referred to as **Robust Verification** or the **Verifier Agent**) introduces a specialized architectural layer focused on trustworthiness. It addresses the inherent inability of a single Large Language Model (LLM) to critically evaluate its own work by establishing a dedicated "Verifier Agent." This agent audits plans and actions against specific criteria, constraints, and real-world facts before execution, ensuring reliability in high-stakes scenarios.

---

## 2. Problem Statement: The Self-Correction Gap
Agents operating with a single LLM face a critical reliability issue:
* **Lack of Objectivity:** An agent cannot reliably step back and critically evaluate its own output.
* **Undetected Errors:** If the planner's LLM hallucinates or makes a logical error, it is unlikely to catch it within the same reasoning pass.
* **High-Stakes Risk:** In sensitive scenarios, unverified actions can lead to incorrect or dangerous outcomes.

---

## 3. Solution Overview: The Verifier Agent
This pattern introduces verification logic placed into a dedicated **Verifier Agent** whose sole responsibility is to evaluate outputs (plans, actions) from the Planner Agent.

### 3.1 Core Principles
* **Independence:** The Verifier should ideally use its own LLM, separate from the Planner’s LLM. This prevents errors in the Planner's model from contaminating the verification process.
* **Parallel Reasoning:** The Verifier performs its own reasoning step independently, potentially in parallel to other processes.
* **Audit & Validate:** It checks outputs against specific criteria, constraints, or real-world facts.

---

## 4. Operational Workflow

1.  **Planning:** The **Planner Agent** generates a plan or action and forwards it.
2.  **Verification:** The **Verifier Agent** receives the output and performs a check (its own reasoning step).
3.  **Verdict:** The Verifier outputs a verdict:
    * **Pass:** The action proceeds.
    * **Fail:** The Verifier provides an explanation of the error.
4.  **Correction:** The Planner uses the "Fail" verdict and explanation as a new observation to revise its plan.
5.  **Arbitration:** The **Controller Module** acts as the final authority. It typically disallows actions that fail verification, though it may allow minor inconsistencies if configured for "Graded Verification."

---

## 5. System Architecture

### 5.1 Modules
* **Planner Module:** Generates the initial strategy.
* **Verifier Module:** Contains the logic for auditing. Can be part of the Controller or a standalone agent.
* **Controller Module:** Receives the Planner's output and the Verifier's verdict to decide on execution.

### 5.2 Tooling
The Verifier Agent is capable of using external tools to validate claims, such as:
* **Compliance Checkers:** Ensuring a vendor is on a pre-approved list.
* **Cross-Referencing Tools:** Checking dates, times, and addresses against confirmed booking documentation to prevent factual drift.

---

## 6. Operational Example: Meeting Organization
*Scenario: An agent creates an agenda for a company meeting.*

* **Draft Plan:** The Planner lists "Lunch and Networking" at 9:00 AM and "Kickoff" at 12:00 PM.
* **Verification Check:** The Verifier checks the logical sequence.
* **Verdict:** **FAIL**.
* **Explanation:** "Logical error detected: Lunch is scheduled before the Kickoff event."
* **Outcome:** The Planner revises the agenda to place Kickoff first.

---

## 7. Graded Verification & Human-in-the-Loop
Not all errors require a full stop. The pattern supports **Graded Verification**:
* **Fatal Error:** Immediate stop (e.g., wrong venue address).
* **Minor Inconsistency:** The Controller may trigger a **Human-in-the-Loop** warning but allow the process to proceed, or pause for human approval.

---

## 8. Risks & Drawbacks
* **Infinite Regress:** There is a risk of "false negatives" where the Verifier identifies errors that don't exist. This theoretically leads to the question: "Who verifies the verifier?"
* **Complexity & Cost:** Involving a second, independent LLM increases token usage, operational costs, and architectural complexity (debugging two distinct reasoning flows).

---