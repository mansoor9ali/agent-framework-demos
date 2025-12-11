# 📚 Agent Framework Demo - Student Learning Index

> **A comprehensive guide to learning AI Agents with practical examples**
> Organized by complexity level and functionality to help students progress systematically

---

## 🎯 Learning Path Overview

| Level | Focus Area | Recommended Time |
|-------|-----------|------------------|
| 🟢 **Beginner** | Basic agent creation, simple tools | 2-3 hours |
| 🟡 **Intermediate** | Multiple tools, threads, structured output | 4-6 hours |
| 🟠 **Advanced** | Middleware, memory, workflows | 6-8 hours |
| 🔴 **Expert** | Multi-agent systems, voice, MCP | 8-10 hours |

---

## 📁 File Index by Complexity Level

### 🟢 Level 1: Beginner (Start Here!)

| # | File Name | Description | Key Concepts |
|---|-----------|-------------|--------------|
| 1.1 | `basic_agent_creation.py` | Create your first AI agent with interactive chat | Agent creation, streaming responses, basic chat loop |
| 1.2 | `basic_chat_streaming_example.py` | Streaming vs non-streaming responses | `run()` vs `run_stream()`, async/await basics |
| 1.3 | `function_tool_calculator.py` | Single function tool (calculator) | Tool definition with `@Annotated`, safe eval |

**🎯 Learning Goals:**
- Understand how to create an AI agent
- Learn the difference between streaming and non-streaming
- Create your first function tool

---

### 🟡 Level 2: Intermediate

| # | File Name | Description | Key Concepts |
|---|-----------|-------------|--------------|
| 2.1 | `agent_function_tools_example.py` | Agent-level vs run-level tools | Tool injection patterns, tool composition |
| 2.2 | `multiple_tools_weather_search.py` | Multiple tools (weather, calculator, timezone) | Tool selection, multi-tool agents |
| 2.3 | `agent_structured_output_example.py` | Extract structured data using Pydantic | `response_format`, Pydantic models |
| 2.4 | `structured_output_pydantic.py` | Interactive structured extraction | Schema validation, typed outputs |
| 2.5 | `agent_thread_management_example.py` | Conversation persistence | `AgentThread`, message stores, context preservation |

**🎯 Learning Goals:**
- Understand different tool injection patterns
- Work with multiple tools simultaneously
- Extract structured data from AI responses
- Maintain conversation context across turns

---

### 🟠 Level 3: Advanced

| # | File Name | Description | Key Concepts |
|---|-----------|-------------|--------------|
| 3.1 | `threading_conversation_persistence.py` | Save/restore conversations to file | Thread serialization, JSON persistence, `ChatMessage` |
| 3.2 | `long_term_memory_mem0.py` | AI-powered long-term memory | `ContextProvider`, memory extraction, profile storage |
| 3.3 | `human_in_the_loop_approval.py` | Approval system for dangerous operations | `ApprovalRequiredTool`, function wrapping, security |
| 3.4 | `middleware_timing_security_logging.py` | Complete middleware stack | `@agent_middleware`, `@function_middleware`, `@chat_middleware` |
| 3.5 | `observability_telemetry_report.py` | OpenTelemetry observability with HTML reports | Telemetry collection, span processing, reporting |
| 3.6 | `file_search_vector_store.py` | Document search with vector stores | `HostedFileSearchTool`, RAG basics, Azure AI Foundry |

**🎯 Learning Goals:**
- Persist conversations across sessions
- Implement AI-powered memory systems
- Add approval workflows for sensitive operations
- Monitor and observe agent behavior
- Search through documents with vector stores

---

### 🔴 Level 4: Expert

| # | File Name | Description | Key Concepts |
|---|-----------|-------------|--------------|
| 4.1 | `agent_supervisor_subagents_example.py` | Supervisor with sub-agents | Agent hierarchies, tool delegation, nested agents |
| 4.2 | `mcp_calculator_server.py` | MCP (Model Context Protocol) integration | `MCPStdioTool`, external tool servers |
| 4.3 | `workflow_basic_example.py` | Writer → Reviewer → Editor workflow | `WorkflowBuilder`, conditional routing, agents collaboration |
| 4.4 | `workflow_handoff_basic.py` | Triage agent with specialist handoffs | `HandoffBuilder`, coordinator pattern |
| 4.5 | `workflow_handoff_context_passing.py` | Single-tier handoff with context | User input requests, conversation routing |
| 4.6 | `workflow_handoff_conditional.py` | Return-to-previous routing | Specialist continuity, domain switching |
| 4.7 | `workflow_handoff_multi_agent.py` | Multi-tier specialist handoffs | Complex routing graphs, agent chains |
| 4.8 | `voice_agent_basic.py` | Voice agent with Azure Speech | STT, TTS, speech recognition |
| 4.9 | `voice_agent_advanced.py` | Advanced voice with streaming TTS | Real-time synthesis, WebSocket streaming |

**🎯 Learning Goals:**
- Build hierarchical multi-agent systems
- Integrate external tool servers via MCP
- Design complex agent workflows
- Implement voice-enabled AI assistants
- Handle complex handoff scenarios

---

## 🗂️ Files by Functionality

### 🤖 Agent Basics
| File | Complexity | Description |
|------|------------|-------------|
| `basic_agent_creation.py` | 🟢 | Create and chat with agent |
| `basic_chat_streaming_example.py` | 🟢 | Streaming responses |

### 🔧 Tools & Functions
| File | Complexity | Description |
|------|------------|-------------|
| `function_tool_calculator.py` | 🟢 | Single calculator tool |
| `agent_function_tools_example.py` | 🟡 | Agent-level vs run-level tools |
| `multiple_tools_weather_search.py` | 🟡 | Multiple tools combined |

### 📊 Structured Output
| File | Complexity | Description |
|------|------------|-------------|
| `agent_structured_output_example.py` | 🟡 | Basic Pydantic extraction |
| `structured_output_pydantic.py` | 🟡 | Interactive extraction |

### 🧵 Threading & Persistence
| File | Complexity | Description |
|------|------------|-------------|
| `agent_thread_management_example.py` | 🟡 | Thread basics |
| `threading_conversation_persistence.py` | 🟠 | File-based persistence |

### 🧠 Memory & Context
| File | Complexity | Description |
|------|------------|-------------|
| `long_term_memory_mem0.py` | 🟠 | AI-powered memory extraction |

### 🔒 Security & Approval
| File | Complexity | Description |
|------|------------|-------------|
| `human_in_the_loop_approval.py` | 🟠 | Human approval workflows |

### 📈 Middleware & Observability
| File | Complexity | Description |
|------|------------|-------------|
| `middleware_timing_security_logging.py` | 🟠 | Full middleware stack |
| `observability_telemetry_report.py` | 🟠 | Telemetry & reporting |

### 📄 Document Search (RAG)
| File | Complexity | Description |
|------|------------|-------------|
| `file_search_vector_store.py` | 🟠 | Vector store search |

### 👥 Multi-Agent Systems
| File | Complexity | Description |
|------|------------|-------------|
| `agent_supervisor_subagents_example.py` | 🔴 | Supervisor pattern |
| `workflow_basic_example.py` | 🔴 | Sequential workflows |
| `workflow_handoff_basic.py` | 🔴 | Basic handoffs |
| `workflow_handoff_context_passing.py` | 🔴 | Context passing |
| `workflow_handoff_conditional.py` | 🔴 | Conditional routing |
| `workflow_handoff_multi_agent.py` | 🔴 | Multi-tier handoffs |

### 🎙️ Voice Agents
| File | Complexity | Description |
|------|------------|-------------|
| `voice_agent_basic.py` | 🔴 | Basic voice agent |
| `voice_agent_advanced.py` | 🔴 | Streaming TTS |

### 🔌 External Integrations (MCP)
| File | Complexity | Description |
|------|------------|-------------|
| `mcp_calculator_server.py` | 🔴 | MCP server integration |

---

## 📋 Prerequisites by Level

### 🟢 Beginner
- Python 3.10+
- Basic async/await understanding
- `.env` file with API credentials

### 🟡 Intermediate
- Pydantic basics
- Understanding of type hints
- JSON manipulation

### 🟠 Advanced
- Decorator patterns
- Context managers
- OpenTelemetry basics
- Azure AI Foundry familiarity

### 🔴 Expert
- Multi-agent design patterns
- WebSocket protocols
- Azure Cognitive Services
- MCP (Model Context Protocol)

---

## 🚀 Quick Start Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run beginner examples
python basic_agent_creation.py
python function_tool_calculator.py

# Run intermediate examples
python multiple_tools_weather_search.py
python structured_output_pydantic.py

# Run advanced examples
python middleware_timing_security_logging.py
python long_term_memory_mem0.py

# Run expert examples (requires additional setup)
python workflow_handoff_basic.py
python voice_agent_basic.py
```

---

## 📖 Recommended Learning Order

```
Week 1: Foundations
├── Day 1-2: basic_agent_creation.py, basic_chat_streaming_example.py
├── Day 3-4: function_tool_calculator.py
└── Day 5-7: agent_function_tools_example.py, multiple_tools_weather_search.py

Week 2: Data & Persistence
├── Day 1-2: structured_output_pydantic.py, agent_structured_output_example.py
├── Day 3-4: agent_thread_management_example.py
└── Day 5-7: threading_conversation_persistence.py

Week 3: Advanced Features
├── Day 1-2: long_term_memory_mem0.py
├── Day 3-4: human_in_the_loop_approval.py
└── Day 5-7: middleware_timing_security_logging.py, observability_telemetry_report.py

Week 4: Multi-Agent & Workflows
├── Day 1-2: agent_supervisor_subagents_example.py
├── Day 3-4: workflow_basic_example.py, workflow_handoff_basic.py
└── Day 5-7: workflow_handoff_multi_agent.py

Week 5: Specialized Applications
├── Day 1-2: file_search_vector_store.py
├── Day 3-4: mcp_calculator_server.py
└── Day 5-7: voice_agent_basic.py, voice_agent_advanced.py
```

---

## 🎓 Key Concepts Summary

| Concept | Files | Description |
|---------|-------|-------------|
| **Agent Creation** | 1.1, 1.2 | Basic agent setup and configuration |
| **Function Tools** | 1.3, 2.1, 2.2 | Adding capabilities to agents |
| **Structured Output** | 2.3, 2.4 | Type-safe AI responses |
| **Threading** | 2.5, 3.1 | Conversation persistence |
| **Memory** | 3.2 | Long-term user knowledge |
| **Security** | 3.3, 3.4 | Approval and middleware |
| **Observability** | 3.5 | Monitoring and telemetry |
| **RAG** | 3.6 | Document retrieval |
| **Multi-Agent** | 4.1-4.7 | Agent collaboration |
| **Voice** | 4.8, 4.9 | Speech interfaces |
| **MCP** | 4.2 | External tool protocols |

---

## 💡 Tips for Students

1. **Start Simple**: Begin with `basic_agent_creation.py` before anything else
2. **Read the Code**: Each file has detailed docstrings explaining concepts
3. **Experiment**: Modify the examples to understand how they work
4. **Use Rich Output**: Files use `rich` library for better console output
5. **Check Utils**: The `utils.py` file contains client creation helpers
6. **Set Up .env**: Create `.env` file with your API credentials first

---

## 📝 Notes

- All files are **interactive demos** - you can chat with the agents
- Type `quit` or `q` to exit most interactive sessions
- Check `utils.py` for client creation patterns
- Some examples require Azure AI Foundry setup

---

*Generated for agent-framework-demo project | December 2025*

