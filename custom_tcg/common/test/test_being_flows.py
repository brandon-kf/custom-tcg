"""Behavioral tests that simulate simple action flows.

These tests use the execution context to drive actions like Play/Activate and
verify side effects:
- items created and held
- deliveries transferring items
- draws moving cards from deck to hand
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_tcg.common.action.deliver import Deliver
from custom_tcg.common.being.aimless_wanderer import AimlessWanderer
from custom_tcg.common.being.early_architect import EarlyArchitect
from custom_tcg.common.being.peasant import Peasant
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.core.anon import Player
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.effect.effect import Activated
from custom_tcg.core.execution.activate import Activate
from custom_tcg.core.execution.execution import ExecutionContext
from custom_tcg.core.execution.play import Play

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard


@pytest.fixture
def player() -> Player:
    """Minimal test player suitable for behavior flows."""
    return Player(
        session_object_id="test-player",
        name="Test Player",
        decks=[],
        starting_cards=[],
        main_cards=[],
        processes=[],
        hand=[],
        played=[],
        discard=[],
    )


def _drain_notifications(ctx: ExecutionContext) -> None:
    """Execute all queued notifications until none remain."""
    while ctx.notifications:
        action = ctx.notifications.pop(0)
        # Notifications may be pre-queued by the activator; reset so the
        # execution engine can own the full lifecycle.
        action.state = ActionStateDef.not_started
        ctx.execute(action)


def _play_card(ctx: ExecutionContext, card: ICard) -> None:
    """Move a card from hand to play by executing its Play action."""
    play = next(a for a in card.actions if isinstance(a, Play))
    ctx.execute(play)


def _activate_card(ctx: ExecutionContext, card: ICard) -> None:
    """Execute a card's Activate action and drain resulting notifications."""
    activate = next(a for a in card.actions if isinstance(a, Activate))
    ctx.execute(activate)
    _drain_notifications(ctx)


def test_play_and_activate_finds_item_and_holds(player: Player) -> None:
    """Playing and activating Aimless Wanderer should create and hold wood."""
    ctx = ExecutionContext(players=[player])

    aw = AimlessWanderer.create(player=player)
    player.hand.append(aw)

    # Play the being
    _play_card(ctx, aw)
    assert aw in player.played
    assert aw not in player.hand

    # Activate: should Tap the being and Find a Pile of Wood (held by the being)
    _activate_card(ctx, aw)

    # Activated effect should be present on the being
    assert next((e for e in aw.effects if isinstance(e, Activated)), None)

    # Verify a Pile of Wood exists and is held by the wanderer
    pow_cards = [c for c in player.played if isinstance(c, PileOfWood)]
    assert pow_cards, "Expected a Pile of Wood to be created"
    pow_card = pow_cards[0]

    held = next(
        (e for e in pow_card.effects if isinstance(e, Holding)),
        None,
    )
    assert held is not None
    assert held.card_held is aw

    holding = next((e for e in aw.effects if isinstance(e, Holding)), None)
    assert holding is not None
    assert holding.card_holding is pow_card


def test_deliver_transfers_held_item(player: Player) -> None:
    """Deliver should move a held item from one being to another."""
    ctx = ExecutionContext(players=[player])

    aw = AimlessWanderer.create(player=player)
    ea = EarlyArchitect.create(player=player)  # High enough CON to hold wood
    player.hand.extend([aw, ea])

    _play_card(ctx, aw)
    _play_card(ctx, ea)

    # Ensure AW holds a Pile of Wood
    _activate_card(ctx, aw)
    pow_card = next(c for c in player.played if isinstance(c, PileOfWood))
    assert next(
        (e for e in pow_card.effects if isinstance(e, Holding)),
        None,
    )

    # Deliver wood from AW to EA using explicit receiver/items to avoid
    # selectors
    deliver = Deliver(card=aw, player=player, receiver=ea, items=[pow_card])
    ctx.execute(deliver)

    # Item should now be held by EA, and no longer held by AW
    held = next(
        (e for e in pow_card.effects if isinstance(e, Holding)),
        None,
    )
    assert held is not None
    assert held.card_held is ea
    aw_holding = next(
        (e for e in aw.effects if isinstance(e, Holding)),
        None,
    )
    assert aw_holding is None

    ea_holding = next((e for e in ea.effects if isinstance(e, Holding)), None)
    assert ea_holding is not None
    assert ea_holding.card_holding is pow_card


def test_peasant_activate_draws_from_deck(player: Player) -> None:
    """Peasant activation draws a card from main deck into hand."""
    ctx = ExecutionContext(players=[player])

    # Seed the deck with any card to draw
    deck_card = AimlessWanderer.create(player=player)
    player.main_cards.append(deck_card)

    peas = Peasant.create(player=player)
    player.hand.append(peas)

    _play_card(ctx, peas)
    assert peas in player.played
    assert peas not in player.hand

    # Hand should be empty before draw; after activation it should increase by 1
    assert len(player.hand) == 0

    _activate_card(ctx, peas)

    assert len(player.hand) == 1
    assert deck_card not in player.main_cards
    assert deck_card in player.hand
