"""A player returned from the API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.card import Card

if TYPE_CHECKING:
    from custom_tcg.core.interface import IPlayer


class Player:
    """A player returned from the API."""

    session_object_id: str
    name: str
    deck_size: int
    hand: list[Card]
    played: list[Card]
    discard: list[Card]

    def __init__(self: Player, player: IPlayer) -> None:
        """Create a player response."""
        self.session_object_id = player.session_object_id
        self.name = player.name
        self.deck_size = len(player.main_cards)
        self.hand = [Card(card=card) for card in player.hand]
        self.played = [Card(card=card) for card in player.played]
        self.discard = [Card(card=card) for card in player.discard]

    def serialize(self: Player) -> dict[str, Any]:
        """Convert this player into a dict."""
        return {
            "session_object_id": self.session_object_id,
            "name": self.name,
            "deck_size": self.deck_size,
            "hand": [card.serialize() for card in self.hand],
            "played": [card.serialize() for card in self.played],
            "discard": [card.serialize() for card in self.discard],
        }
