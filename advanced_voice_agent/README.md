# Advanced Voice Agent System

This package extends the `voice_agent_test2.py` demo into a multi-agent voice stack with:

- Azure Speech input/output with idle shutdown guard
- Persistent conversation threads + AI-driven long-term memory
- Tool registry combining local Python tools and MCP calculator server
- Coordinator orchestration with pluggable lifecycle hooks
- Unit-tested idle controller for graceful exits

## Running the demo

```powershell
cd F:\Projects\agent-framework-demo
python -m advanced_voice_agent.main
```

Set the following environment variables beforehand (see `.env`):

- `AZURE_STT_SUBSCRIPTIONKEY`, `AZURE_STT_REGION`
- `AZURE_TTS_SUBSCRIPTIONKEY`, `AZURE_TTS_REGION`
- `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `OPENAI_MODEL_ID`
- Optional: install `uv` to enable the MCP calculator (`uvx mcp-server-calculator`)

The agent now auto-stops after five consecutive silent/failed recognition attempts or five minutes of inactivity. Conversation threads and long-term memory save under `advanced_voice_agent_state/`.

## Tests

The new idle controller has lightweight unit tests:

```powershell
cd F:\Projects\agent-framework-demo
.\.venv\Scripts\python -m pytest advanced_voice_agent/tests/test_idle.py
```

## Extending

- Adjust `IdleController` thresholds via `advanced_voice_agent.main`
- Add more tools/MCP servers in `MCP_SPECS`
- Build specialized agents using helper scaffolding in `agents.py`
```}
