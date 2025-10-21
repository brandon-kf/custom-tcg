"""A card returned from the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.card import Card
from custom_tcg.game_api.response.player import Player

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction


@dataclass
class Action:
    """An action returned from the API."""

    session_object_id: str
    name: str
    type: str
    state: str

    card: Card
    player: Player

    def __init__(self: Action, action: IAction) -> None:
        """Create an API action."""
        self.session_object_id = action.session_object_id
        self.name = action.name
        self.type = action.__class__.__name__
        self.state = action.state.name
        self.card = Card(card=action.card)
        self.player = Player(player=action.player)

    def serialize(self: Action) -> dict[str, Any]:
        """Convert this action into a dict."""
        return {
            "session_object_id": self.session_object_id,
            "name": self.name,
            "type": self.type,
            "state": self.state,
            "card": self.card.serialize(),
            "player": self.player.serialize(),
        }
