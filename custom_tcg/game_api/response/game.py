"""A session state returned from the API."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from custom_tcg.game_api.response.player import Player

if TYPE_CHECKING:
    from custom_tcg.game import Game as CoreGame


class Game:
    """A session state returned from the API."""

    session_id: str
    players: list[Player]

    def __init__(self: Game, game: CoreGame) -> None:
        """Create a session response."""
        self.session_id = game.session_id
        self.players = [Player(player=player) for player in game.players]

    def serialize(self: Game) -> dict[str, Any]:
        """Convert this game into a dict."""
        return {
            "session_id": self.session_id,
            "players": [player.serialize() for player in self.players],
        }
