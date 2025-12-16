# Design Document: ReAct (Reasoning + Acting) Pattern

**Version:** 1.0  
**Context:** Agentic AI Solution Design Patterns

---

## 1. Executive Summary
The **ReAct (Reasoning + Acting)** pattern is a foundational architectural strategy for Agentic AI that synergizes reasoning and action in an iterative loop. By combining Chain-of-Thought (CoT) reasoning with tool-based action execution, this pattern enables agents to dynamically interact with their environment, observe outcomes, and adjust their strategy in real-time. ReAct is the baseline pattern for building adaptive, interactive AI agents capable of solving complex, multi-step problems through continuous feedback.


![ReAct Pattern Architecture](ReAct_Pattern.png)
---

## 2. Problem Statement: The Static Reasoning Limitation
Traditional prompting techniques like **Chain-of-Thought (CoT)** excel at reasoning but operate in isolation from the real world.
* **The Limitation:** Pure reasoning patterns cannot validate assumptions, retrieve current information, or adapt to dynamic environments.
* **The Consequence:** Agents may produce logically sound plans based on outdated, incomplete, or hallucinated information, leading to incorrect outcomes.
* **The Gap:** There is no mechanism for the agent to "learn" from real-world feedback during task execution.

---

## 3. Solution Overview: The Reasoning-Acting Loop
The ReAct pattern introduces a continuous cycle where the agent alternates between **thinking** (reasoning) and **doing** (acting), using observations to inform subsequent reasoning.

### Core Principle: Interleaved Execution
Instead of separating planning from execution, ReAct integrates them:
* **Reason:** The LLM analyzes the current state and decides the next action.
* **Act:** The agent executes a tool or function to interact with the environment.
* **Observe:** The agent receives feedback from the action's result.
* **Iterate:** The new observation informs the next reasoning step.

This creates a **feedback loop** that enables dynamic adaptation and self-correction.

---

## 4. System Architecture

### 4.1 Core Components

#### The Agent
The central orchestrator that manages the reasoning-acting loop and maintains conversation history.

**Key Responsibilities:**
* Execute the iterative think-act-observe cycle
* Maintain message history and context
* Coordinate between reasoning and action modules
* Manage iteration limits and termination conditions

#### The Reasoning Module (LLM)
The cognitive engine that generates thoughts and decides actions.

**Process:**
1. Receives: Current query + conversation history + available tools
2. Analyzes: Determines what information is needed or what action should be taken
3. Outputs: Structured JSON containing either an action to execute or a final answer

#### The Tool Registry
A collection of executable functions that extend the agent's capabilities.

**Common Tools:**
* **Wikipedia Search:** Factual, encyclopedic information retrieval
* **Google Search:** Current information and web content access
* **Calculator:** Mathematical computations
* **Database Query:** Structured data retrieval
* **API Calls:** External service integration

#### The Controller
Manages tool execution and observation handling.

**Responsibilities:**
* Parse LLM decisions
* Invoke appropriate tools
* Capture and format tool outputs
* Handle errors and edge cases
 

---

## 5. Operational Workflow: The ReAct Cycle

### Iteration Structure
Each iteration follows a strict sequence:

**Step 1: Think (Reasoning)**
```
Input: Query + History + Available Tools
LLM Output: {
    "thought": "I need to find factual information about X...",
    "action": {
        "name": "wikipedia",
        "reason": "Wikipedia is reliable for factual data",
        "input": "search query"
    }
}
```

**Step 2: Decide (Routing)**
- Parse LLM output
- Validate action format
- Route to tool execution or final answer

**Step 3: Act (Tool Execution)**
```
Tool: wikipedia.search("search query")
Result: "Wikipedia summary content..."
```

**Step 4: Observe (Feedback)**
```
Observation: "Observation from wikipedia: [result]"
Action: Add observation to conversation history
```

**Step 5: Loop or Terminate**
- If final answer provided → End
- If max iterations reached → End with current state
- Otherwise → Return to Step 1

### Termination Conditions
1. **Success:** LLM provides a final answer
2. **Limit:** Maximum iterations reached (typically 5-10)
3. **Error:** Unrecoverable tool failure (rare)

---

## 6. Operational Example: Research Query

**Query:** *"What is the tallest building in India and when was it built?"*

**Iteration 1:**
- **Thought:** "I need factual information about buildings in India"
- **Action:** Search Wikipedia for "tallest building in India"
- **Observation:** "Lokhandwala Minerva is the tallest completed building at 301 meters..."

**Iteration 2:**
- **Thought:** "The Wikipedia summary doesn't include the construction date"
- **Action:** Search Google for "Lokhandwala Minerva completion year"
- **Observation:** "Multiple sources indicate completion in 2023"

**Iteration 3:**
- **Thought:** "I now have complete information to answer the query"
- **Action:** Provide final answer
- **Output:** "The tallest completed building in India is Lokhandwala Minerva, standing at 301 meters (78 floors), completed in December 2023."

---

## 7. Implementation Details

### 7.1 Prompt Engineering
The ReAct pattern relies heavily on structured prompts that guide the LLM to produce consistent, parseable output.

**Template Structure:**
```
You are an AI agent that reasons and acts to solve problems.

Query: {query}

Available Tools: {tools}

Conversation History:
{history}

Instructions:
1. Think step-by-step about what information you need
2. Choose an appropriate tool if needed
3. Or provide a final answer if you have sufficient information

Output Format (JSON):
{
    "thought": "your reasoning process",
    "action": {
        "name": "tool_name",
        "reason": "why this tool",
        "input": "tool input"
    }
}
OR
{
    "thought": "reasoning",
    "answer": "final answer"
}
```

### 7.2 Error Handling
The pattern includes multiple fallback mechanisms:
- **JSON Parsing Errors:** Retry with error feedback
- **Tool Failures:** Log error, add to history, continue iteration
- **Max Iterations:** Provide best available answer
- **Empty Responses:** Request LLM to retry

### 7.3 State Management
The agent maintains:
- **Message History:** All thoughts, actions, and observations
- **Iteration Counter:** Tracks loop progress
- **Tool Registry:** Available actions and their metadata
- **Trace Log:** Complete execution history for debugging

---

## 8. Comparative Analysis

| Feature | Pure CoT | ReAct Pattern | Plan-and-Execute |
|---------|----------|---------------|------------------|
| **Adaptability** | None | **High** | Low |
| **Real-world Interaction** | No | **Yes** | Yes |
| **Resource Usage** | Low | **Medium** | Low |
| **Latency** | Low | **Medium** | Low |
| **Error Recovery** | None | **Strong** | Weak |
| **Best For** | Static reasoning | **Dynamic tasks** | Sequential workflows |

---

## 9. Trade-Off Analysis

### Strengths
✅ **Dynamic Adaptation:** Adjusts strategy based on real-world feedback  
✅ **Self-Correction:** Can detect and fix mistakes in subsequent iterations  
✅ **Tool Integration:** Seamlessly incorporates external capabilities  
✅ **Transparency:** Clear reasoning trace for debugging and auditing  
✅ **Balanced Approach:** Good trade-off between speed and accuracy  

### Limitations
❌ **Resource Consumption:** Multiple LLM calls per task (more than Plan-and-Execute)  
❌ **Latency:** Sequential nature adds delay compared to pure planning  
❌ **Token Usage:** Conversation history grows with each iteration  
❌ **Complexity:** Requires careful prompt engineering and error handling  
❌ **Linear Path:** Follows single reasoning chain (unlike LATS)  

---

## 10. When to Use ReAct

### Ideal Scenarios
✓ **Information Retrieval Tasks:** Queries requiring up-to-date or factual data  
✓ **Interactive Debugging:** Problems where trial-and-error is acceptable  
✓ **Multi-step Research:** Tasks needing multiple information sources  
✓ **Adaptive Workflows:** Situations where requirements may change based on findings  
✓ **Tool-Heavy Applications:** Solutions requiring frequent external interactions  

### Not Recommended For
✗ **Simple Static Queries:** Where pure CoT suffices  
✗ **High-Speed Requirements:** When milliseconds matter  
✗ **Highly Complex Planning:** Where LATS or Planner-Critic-Refiner is better  
✗ **Budget-Constrained:** When token costs are critical  
✗ **Deterministic Workflows:** Where exact sequence is known upfront  

---

## 11. Advanced Considerations

### 11.1 Optimization Strategies
1. **Early Termination:** Stop when confidence threshold is met
2. **Tool Caching:** Cache expensive tool results
3. **Parallel Tool Calls:** Execute independent tools concurrently (hybrid with CEO pattern)
4. **Streaming:** Stream thoughts and actions for real-time UX
5. **History Compression:** Summarize old iterations to reduce context

### 11.2 Security & Safety
- **Tool Sandboxing:** Isolate tool execution environments
- **Input Validation:** Sanitize all tool inputs
- **Output Filtering:** Screen for sensitive information leakage
- **Rate Limiting:** Prevent infinite loops or excessive API calls
- **Audit Logging:** Complete trace of all actions for compliance

### 11.3 Evaluation Metrics
- **Success Rate:** Percentage of queries correctly answered
- **Average Iterations:** Mean number of loops to completion
- **Tool Efficiency:** Ratio of useful vs. unnecessary tool calls
- **Latency:** End-to-end response time
- **Cost:** Total tokens consumed per query

---

## 12. Pattern Variants

### 12.1 ReAct + Self-Reflection
Add a reflection step after each iteration to evaluate reasoning quality.

### 12.2 ReAct + Memory
Incorporate long-term memory to recall past solutions for similar problems.

### 12.3 Multi-Agent ReAct
Multiple specialized ReAct agents collaborate, each handling different tool categories.

### 12.4 ReAct + Planning
Hybrid approach: Generate initial plan, then use ReAct loop for execution with adaptation.

---

## 13. Conclusion

The **ReAct pattern** represents the foundation of modern Agentic AI architecture. By elegantly combining reasoning with action and observation, it creates agents that can:
- Learn from their environment in real-time
- Correct mistakes dynamically
- Leverage external tools effectively
- Provide transparent reasoning traces

While not optimal for every scenario, ReAct's balanced approach makes it the **default pattern** for building interactive, adaptive AI agents. Its simplicity, transparency, and proven effectiveness have established it as the baseline against which other patterns are measured.

---

**Pattern Classification:** Foundational  
**Complexity:** Medium  
**Resource Profile:** Medium Token Usage, Medium Latency  
**Primary Use Case:** Dynamic information retrieval and interactive problem-solving  
**Maturity:** Production-Ready (Widely Adopted)

---

## References & Further Reading

- **Original Paper:** "ReAct: Synergizing Reasoning and Acting in Language Models" (Yao et al., 2022)
- **Implementation:** See `src/react/agent.py` for reference implementation
- **Related Patterns:** Plan-and-Execute, LATS, Planner-Critic-Refiner
- **Best Practices:** LangChain ReAct Documentation, OpenAI Agent Guidelines

---

*Document Version: 1.0*  
*Last Updated: December 16, 2025*  
*Author: AI Architecture Team*

