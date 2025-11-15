"""Unit tests for the idle controller."""

from __future__ import annotations

from advanced_voice_agent.idle import IdleController


class FakeClock:
    def __init__(self, start: float = 0.0) -> None:
        self.value = start

    def advance(self, delta: float) -> None:
        self.value += delta

    def __call__(self) -> float:  # pragma: no cover - trivial getter
        return self.value


def test_idle_attempt_limit_triggers_stop() -> None:
    clock = FakeClock()
    controller = IdleController(max_idle_attempts=2, idle_timeout=None, time_fn=clock)

    controller.record_idle()
    assert not controller.should_stop()

    controller.record_idle()
    assert controller.should_stop()


def test_activity_resets_idle_counter() -> None:
    clock = FakeClock()
    controller = IdleController(max_idle_attempts=1, idle_timeout=None, time_fn=clock)

    controller.record_idle()
    assert controller.should_stop()

    controller.record_activity()
    assert not controller.should_stop()


def test_timeout_triggers_stop_without_attempts() -> None:
    clock = FakeClock()
    controller = IdleController(max_idle_attempts=None, idle_timeout=5.0, time_fn=clock)

    controller.record_activity()
    assert not controller.should_stop()

    clock.advance(4.0)
    assert not controller.should_stop()

    clock.advance(1.1)
    assert controller.should_stop()

