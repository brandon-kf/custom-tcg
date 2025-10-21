"""A card returned from the API."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.action import Action
from custom_tcg.game_api.response.player import Player

if TYPE_CHECKING:
    from custom_tcg.core.interface import IActionContext


@dataclass
class ActionContext:
    """An action returned from the API."""

    action: Action
    ready: list[Action]
    choices: list[Action]
    players: list[Player]

    def __init__(
        self: ActionContext,
        action_context: IActionContext,
    ) -> None:
        """Create an API action."""
        self.action = Action(action=action_context.action)
        self.ready = [Action(action=action) for action in action_context.ready]
        self.choices = [
            Action(action=action) for action in action_context.choices
        ]
        self.players = [
            Player(player=player) for player in action_context.players
        ]

    def serialize(self: ActionContext) -> dict[str, Any]:
        """Serialize an event context."""
        return {
            "action": self.action.serialize(),
            "ready": [action.serialize() for action in self.ready],
            "choices": [action.serialize() for action in self.choices],
            "players": [player.serialize() for player in self.players],
        }
