"""A session state returned from the API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.action import Action
from custom_tcg.game_api.response.player import Player

if TYPE_CHECKING:
    from custom_tcg.core.interface import IExecutionContext


class Choice:
    """A session state returned from the API."""

    prompt: str
    actions: list[Action]
    player: Player

    def __init__(
        self: Choice,
        context: IExecutionContext,
    ) -> None:
        """Create a session response."""
        self.prompt = context.ready[0].name
        self.actions = [Action(action=action) for action in context.choices]
        self.player = Player(player=context.player)

    def serialize(self: Choice) -> dict[str, Any]:
        """Convert this game into a dict."""
        return {
            "prompt": self.prompt,
            "actions": [action.serialize() for action in self.actions],
            "player": self.player.serialize(),
        }
