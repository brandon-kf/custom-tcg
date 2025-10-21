"""A card returned from the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.common.effect.interface import IHeld


@dataclass
class HeldEffect(Effect):
    """An action returned from the API."""

    holding_id: str

    def __init__(self: HeldEffect, effect: IHeld) -> None:
        """Create an API action."""
        super().__init__(effect=effect)
        self.holding_id = effect.card_held_by.session_object_id

    def serialize(self: HeldEffect) -> dict[str, Any]:
        """Convert this action into a dict."""
        base_dict: dict[str, Any] = super().serialize()

        base_dict["holding_id"] = self.holding_id

        return base_dict
