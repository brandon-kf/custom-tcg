"""A card returned from the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.common.effect.interface import IHolding


@dataclass
class HoldingEffect(Effect):
    """An action returned from the API."""

    held_id: str

    def __init__(self: HoldingEffect, effect: IHolding) -> None:
        """Create an API action."""
        super().__init__(effect=effect)
        self.held_id = effect.card_holding.session_object_id

    def serialize(self: HoldingEffect) -> dict[str, Any]:
        """Convert this action into a dict."""
        base_dict: dict[str, Any] = super().serialize()

        base_dict["held_id"] = self.held_id

        return base_dict
