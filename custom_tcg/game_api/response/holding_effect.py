"""A card returned from the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.common.test.test_being_flows import Holding


@dataclass
class HoldingEffect(Effect):
    """An action returned from the API."""

    holding_id: str
    held_id: str

    def __init__(self: HoldingEffect, effect: Holding) -> None:
        """Create an API action."""
        super().__init__(effect=effect)
        self.holding_id = effect.card_holding.session_object_id
        self.held_id = effect.card_held.session_object_id

    def serialize(self: HoldingEffect) -> dict[str, Any]:
        """Convert this action into a dict."""
        base_dict: dict[str, Any] = super().serialize()

        base_dict["holding_id"] = self.holding_id
        base_dict["held_id"] = self.held_id

        return base_dict
