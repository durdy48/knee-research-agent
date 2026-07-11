"""A tiny synchronous event bus. Steps publish; observers (metrics, logging) subscribe."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List


@dataclass
class Event:
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)


class EventBus:
    def __init__(self) -> None:
        self._subscribers: Dict[str, List[Callable[[Event], None]]] = {}
        self.log: List[Event] = []

    def subscribe(self, name: str, handler: Callable[[Event], None]) -> None:
        """Subscribe to an event name, or to '*' for every event."""
        self._subscribers.setdefault(name, []).append(handler)

    def publish(self, event: Event) -> None:
        self.log.append(event)
        for handler in self._subscribers.get(event.name, []):
            handler(event)
        for handler in self._subscribers.get("*", []):
            handler(event)
