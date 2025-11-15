"""Memory subsystem for advanced voice agent."""

from __future__ import annotations

from dataclasses import dataclass, field
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, Tuple, cast

from agent_framework import Context, ContextProvider, ChatMessage
from openai import OpenAI

STATE_DIR = Path("advanced_voice_agent_state")
STATE_DIR.mkdir(exist_ok=True)

MEMORY_FILE = STATE_DIR / "ai_memory_profile.json"
THREAD_FILE = STATE_DIR / "thread_history.json"


@dataclass
class PersistentThreadStore:
    """Save/restore conversation threads using serialization helpers."""

    def __init__(self, path: Path = THREAD_FILE) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    async def restore(self, agent) -> tuple[Any, int]:
        if not self.path.exists():
            return agent.get_new_thread(), 0
        with self.path.open("r", encoding="utf-8") as f:
            data: Dict[str, Any] = json.load(f)
        thread_data = data["thread_data"]
        store_state = cast(dict[str, Any] | None, thread_data.get("chat_message_store_state"))
        if store_state and "messages" in store_state:
            messages = store_state.get("messages")
            if isinstance(messages, list):
                store_state["messages"] = [ChatMessage.from_dict(msg) for msg in messages]
        thread = await agent.deserialize_thread(thread_data)
        return thread, int(data.get("message_number", 0))

    async def persist(self, thread, message_number: int) -> None:
        serialized = cast(Dict[str, Any], await thread.serialize())
        json_serialized: Dict[str, Any] = dict(serialized)
        store_state = cast(dict[str, Any] | None, json_serialized.get("chat_message_store_state"))
        if store_state and "messages" in store_state:
            messages = store_state.get("messages")
            if isinstance(messages, list):
                store_state["messages"] = [msg.to_dict() for msg in messages if hasattr(msg, "to_dict")]
        payload = {
            "timestamp": datetime.now().isoformat(),
            "message_number": int(message_number),
            "thread_data": json_serialized,
        }
        with self.path.open("w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2)


@dataclass
class LongTermMemory(ContextProvider):
    """Injects long-term memory context extracted via AI."""

    ai_client: OpenAI
    model_id: str
    memory_file: Path = MEMORY_FILE
    profile: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.memory_file.parent.mkdir(parents=True, exist_ok=True)
        if self.memory_file.exists():
            try:
                with self.memory_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                self.profile = data.get("profile", {})
            except Exception:
                self.profile = {}

    async def invoking(self, messages: Iterable[ChatMessage], **kwargs) -> Context:
        if not self.profile:
            return Context()
        profile_text = "\n".join(f"- {k}: {v}" for k, v in self.profile.items())
        instructions = (
            "[USER PROFILE]\n"
            f"{profile_text}\n"
            "Use this background info to personalize responses when relevant."
        )
        return Context(instructions=instructions)

    def _save(self) -> None:
        with self.memory_file.open("w", encoding="utf-8") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "profile": self.profile}, f, indent=2)

    async def invoked(self, request_messages, response_messages, **kwargs) -> None:
        user_text = ""
        for msg in reversed(list(request_messages)):
            if msg.role == "user":
                for content in msg.contents:
                    if hasattr(content, "text") and content.text:
                        user_text = content.text
                        break
                if user_text:
                    break
        if not user_text:
            return
        prompt = (
            "Extract personal data worth remembering from this text as JSON.\n"
            f"Text: {user_text}\n"
            "Return {} if nothing."
        )
        try:
            response = self.ai_client.chat.completions.create(
                model=self.model_id,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
            )
            content = response.choices[0].message.content
            if not content:
                return
            start = content.find("{")
            end = content.rfind("}") + 1
            if start == -1 or end == 0:
                return
            new_data = json.loads(content[start:end])
            changed = False
            for key, value in new_data.items():
                if value and self.profile.get(key) != value:
                    self.profile[key] = value
                    changed = True
            if changed:
                self._save()
        except Exception:
            return
