"""Tests for `custom_tcg.core.process.lets_rest` module."""

from custom_tcg.core.dimension import CardClassDef, CardTypeDef
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.play import Play
from custom_tcg.core.process.lets_rest import LetsRest
from custom_tcg.core.process.process_manager import ProcessManager
from custom_tcg.core.process.rest import Rest


def test_lets_rest_create_initializes_card_and_actions() -> None:
    """Create a Let's Rest card with expected types, classes, and actions."""

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

    card = LetsRest.create(player=player)  # type: ignore[arg-type]

    assert card.name == "Let's Rest"
    assert CardTypeDef.process in card.types
    assert CardClassDef.rest in card.classes

    assert any(isinstance(a, Play) for a in card.actions)
    activates = [a for a in card.actions if isinstance(a, Activate)]
    assert len(activates) == 1

    [activate] = activates
    # Rest and a ProcessManager should be included in Activate.actions
    assert any(isinstance(a, Rest) for a in activate.actions)
    assert any(isinstance(a, ProcessManager) for a in activate.actions)
