"""A card returned from the API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.effect_factory import EffectFactory

if TYPE_CHECKING:
    from custom_tcg.game_api.response.effect import Effect
    from custom_tcg.core.interface import ICard


class Card:
    """A card returned from the API."""

    session_object_id: str
    name: str
    types: list[str]
    effects: list[Effect]

    def __init__(self: Card, card: ICard) -> None:
        """Create API data from core object."""
        self.session_object_id = card.session_object_id
        self.name = card.name
        self.types = [type_def.name for type_def in card.types]
        self.effects = [
            EffectFactory.parse(effect=effect) for effect in card.effects
        ]

    def serialize(self: Card) -> dict[str, Any]:
        """Convert this card into a dict."""
        return {
            "session_object_id": self.session_object_id,
            "name": self.name,
            "types": self.types,
            "effects": [effect.serialize() for effect in self.effects],
        }
