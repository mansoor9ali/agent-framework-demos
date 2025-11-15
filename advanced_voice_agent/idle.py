"""Idle detection helpers for the voice agent."""

from __future__ import annotations

import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class IdleController:
    """Tracks inactivity to determine when to stop listening."""

    max_idle_attempts: Optional[int] = 5
    idle_timeout: Optional[float] = 300.0
    time_fn: Callable[[], float] = time.monotonic

    def __post_init__(self) -> None:
        self.idle_attempts = 0
        self.last_activity = self.time_fn()

    def record_activity(self) -> None:
        self.idle_attempts = 0
        self.last_activity = self.time_fn()

    def record_idle(self) -> None:
        self.idle_attempts += 1

    def should_stop(self) -> bool:
        attempts_limit = (
            self.max_idle_attempts is not None and self.idle_attempts >= self.max_idle_attempts
        )
        timeout_reached = False
        if self.idle_timeout is not None:
            timeout_reached = (self.time_fn() - self.last_activity) >= self.idle_timeout
        return attempts_limit or timeout_reached

