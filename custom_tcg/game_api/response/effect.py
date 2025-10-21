"""A card returned from the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from custom_tcg.core.interface import IEffect


@dataclass
class Effect:
    """An action returned from the API."""

    session_object_id: str
    name: str
    type: str

    def __init__(self: Effect, effect: IEffect) -> None:
        """Create an API action."""
        self.session_object_id = effect.session_object_id
        self.name = effect.name
        self.type = effect.__class__.__name__

    def serialize(self: Effect) -> dict[str, Any]:
        """Convert this action into a dict."""
        return {
            "session_object_id": self.session_object_id,
            "name": self.name,
            "type": self.type,
        }
