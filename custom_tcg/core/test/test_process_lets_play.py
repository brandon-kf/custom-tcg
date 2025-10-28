"""Tests for `custom_tcg.core.process.lets_play` module."""

from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.core.process.lets_play import LetsPlay


def test_lets_play_create_initializes_card_and_actions() -> None:
    """Create a Let's Play card with expected types, classes, and actions."""

    # Minimal fake player object with collections used by Card
    class _P:
        def __init__(self) -> None:
            """Initialize containers used by cards."""
            self.starting_cards = []
            self.main_cards = []
            self.processes = []
            self.hand = []
            self.played = []
            self.discard = []

    player = _P()

    card = LetsPlay.create(player=player)  # type: ignore[arg-type]

    assert card.name == "Let's Play"
    assert CardTypeDef.process in card.types
    assert CardClassDef.play in card.classes

    # One Play and one Activate should be present
    assert any(isinstance(a, Play) for a in card.actions)
    activates = [a for a in card.actions if isinstance(a, Activate)]
    assert len(activates) == 1

    # The Activate should include exactly one ProcessManager action
    [activate] = activates
    managers = [
        a for a in activate.actions if isinstance(a, LetsPlay.ProcessManager)
    ]
    assert len(managers) == 1
