# Enterprise Agentic AI Architecture: Design Specification

**Document Type:** Technical Architecture & Interview Guide  
**System Concept:** The "Digital Program Manager"  
**Core Frameworks:** LangGraph, FastAPI, Streamlit, PostgreSQL

---

## 1. Executive Summary & Philosophy

**Concept:** This system is not a chatbot; it is a **Stateful, Governed Workflow Automation System**.  
**Objective:** To assist human program managers by proactively identifying risks, tracking dependencies, and enforcing governance—audited at every step.  
**Key Differentiator:** Unlike hobbyist "Chat with PDF" applications, this architecture prioritizes **Safety, Auditability, and Control** over speed or conversational flair.

### The "Not a Chatbot" Rule
* **Users:** Program Managers, Product Owners.
* **Queries:** "What is the risk profile for the next sprint?", "Who needs approval?", "What are the hidden dependencies?"
* **Behavior:** The system reads Jira tickets, understands risks, communicates status, takes action, and logs every decision for audit purposes.

---

## 2. Technical Architecture Layers

### Layer 1: The Presentation Layer (Frontend)
* **Technology:** Streamlit (MVP/Internal) or React (Enterprise).
* **Design Pattern:** Dashboard-centric.
* **Key Components:**
    * **Daily Status Tab:** High-level project health.
    * **Risk Dashboard:** Visual representation of blockers/delays.
    * **Approvals Queue:** Human-in-the-loop interface for authorizing actions.
    * **Audit Trail:** Read-only view of AI decisions.

### Layer 2: The API Gatekeeper (Backend)
* **Technology:** FastAPI.
* **Role:** Security Boundary. (The UI *never* talks to the LLM directly).
* **Responsibilities:**
    * **Authentication & Validation:** Verifies identity.
    * **RBAC (Role-Based Access Control):** Ensures permission levels (e.g., Junior vs. Senior).
    * **API Contracts:** Enforces strict data schemas.

### Layer 3: The Orchestration Brain
* **Technology:** LangGraph (Python).
* **Key Concept:** **Stateful Orchestration**.
    * Unlike linear chains, a Graph can loop, pause, wait for human input, and persist state.
    * Maintains "memory" of the workflow state (e.g., *Waiting for Approval*).
* **Function:** Controls execution flow and decides which agent runs next.

---

## 3. Multi-Agent Topology (The "Team")

Each agent has **one** specialized job.

| Agent Name | Role | Responsibility | Input/Output |
| :--- | :--- | :--- | :--- |
| **Planner Agent** | The Strategist | Breaks user intent into steps. Does *not* execute code. | Prompt → Step-by-step Plan |
| **Jira Analyst** | The Integrator | Connects to Jira/ServiceNow APIs. Extracts signals. No hallucination allowed. | Plan → Structured Ticket Data |
| **Risk Agent** | The Skeptic | Analyzes data for "What can go wrong?" (Delays, blockers). | Jira Data → Risk Report |
| **Dependency Agent** | The Connector | Checks cross-team impacts and upstream/downstream blockers. | Jira Data → Dependency Graph |
| **Comms Agent** | The Narrator | Synthesizes logs into clear business narratives for humans. | Tech Logs → Executive Summary |
| **Action Agent** | The Doer | Executes changes (update ticket, send email) *only* after analysis. | Approved Plan → Execution Result |
| **Governance Agent** | The Policeman | Checks compliance, policy, and permissions. | Proposed Action → Approval/Denial |
| **Evaluator Agent** | The QA | Scores output quality and decision correctness. Feeds fine-tuning. | Final Output → Quality Score |

---

## 4. Governance & Safety (The Enterprise Requirement)

These layers sit between the user/tools and the agents to prevent abuse.

1.  **PII Detection:** Redacts sensitive data (names, SSNs) before LLM processing.
2.  **Rate Limiting (Redis):** Prevents DOS attacks and manages API costs.
3.  **Auth & RBAC:** Ensures the user has permission to trigger specific workflows.
4.  **Human-in-the-Loop:** Critical actions require explicit approval via the UI before the Graph proceeds.

---

## 5. Data Layer Strategy

**Memory ≠ Records.** We use a dual-database approach.

### A. State Database (PostgreSQL)
* **Schema:** `chat_store`
* **Purpose:** **Auditing.**
* **Stores:** Workflow state, human approval logs, conversation history.
* **Why:** "Who approved this action and when?"

### B. Vector Database (PostgreSQL + pgvector)
* **Schema:** `vector_store`
* **Purpose:** **Knowledge Base (RAG).**
* **Stores:** Embeddings of documentation, past tickets, and wikis.

### C. Cache (Redis)
* **Purpose:** Performance caching and Rate Limiting.

---

## 6. Implementation Roadmap

1.  **Phase 1: Infrastructure**
    * Docker setup for PostgreSQL (`pgvector`) and Redis.
    * Define SQL schemas for `audit_logs` and `workflow_state`.
2.  **Phase 2: Tooling Layer**
    * Write Python functions for Jira API interaction.
    * Ensure tool isolation (no LLM yet).
3.  **Phase 3: The Brain (LangGraph)**
    * Implement `Planner` and `Jira Analyst`.
    * Create the graph edges: `Start -> Planner -> Analyst -> End`.
4.  **Phase 4: Risk & Governance**
    * Add parallel nodes for `Risk` and `Dependency`.
    * Insert `Governance` node before any "Write" actions.
5.  **Phase 5: API & UI**
    * Wrap LangGraph in FastAPI.
    * Build Streamlit dashboard to consume the API.

---

## 7. Interview Cheat Sheet: "How do you design Agentic Systems?"

* **Start with Control:** "I don't build black-box chatbots. I build stateful, governed systems using **LangGraph**."
* **Separation of Concerns:** "I separate the **Planner** (reasoning) from the **Executor** (tools). This prevents impulsive AI actions."
* **Governance First:** "The most critical component is the **Governance Agent** acting as middleware to enforce RBAC and policy."
* **Feedback Loops:** "I use an **Evaluator Agent** to score performance, creating a dataset for continuous fine-tuning."