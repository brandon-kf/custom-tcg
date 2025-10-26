"""Tests for effects in `custom_tcg.common.effect`.

Covers:
- ItemStats.calculate_being_stats mapping
- BeingStatsEvaluator aggregation of base + held item stats
- Holding.activate/deactivate wiring Held and Drop
- Held.deactivate cascades removal of Holding
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import pytest

from custom_tcg.common.being.peasant import Peasant
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.being_stats_evaluator import (
    BeingStatsEvaluator,
)
from custom_tcg.common.effect.held import Held
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.common.item.pile_of_wood import PileOfWood
from custom_tcg.core.anon import Player
from custom_tcg.core.dimension import EffectStateDef
from custom_tcg.core.execution.execution import ExecutionContext

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard


@pytest.fixture
def player() -> Player:
    """Create a minimal player for tests."""
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


@pytest.fixture
def ctx(player: Player) -> ExecutionContext:
    """Create an execution context for a single-player test."""
    return ExecutionContext(players=[player])


def test_item_stats_maps_to_being_stats(player: Player) -> None:
    """ItemStats.calculate_being_stats maps fields to BeingStats correctly."""
    item = PileOfWood.create(player=player)

    # Override with specific values to test mapping distinctly
    heft = 3
    utility = 4
    uniquity = 5
    antiquity = 6

    item.effects = [
        ItemStats(
            name="Item properties",
            card=item,
            heft=heft,
            utility=utility,
            uniquity=uniquity,
            antiquity=antiquity,
        ),
    ]

    istats = next(e for e in item.effects if isinstance(e, ItemStats))
    mapped: BeingStats = istats.calculate_being_stats()

    assert mapped.encumberance == heft
    assert mapped.dexterity == utility
    assert mapped.charisma == uniquity
    assert mapped.wisdom == antiquity


def test_being_stats_evaluator_sums_base_and_held_item(player: Player) -> None:
    """Evaluator adds base BeingStats and item-derived stats via Holding."""
    being: ICard = Peasant.create(player=player)
    item: ICard = PileOfWood.create(player=player)

    # Simulate both cards in play
    player.played.extend([being, item])

    # Attach a Holding effect to the being so evaluator sees held item
    holding = Holding(card=being, card_holding=item)
    being.effects.append(holding)

    # Base stats from Peasant
    base = next(e for e in being.effects if isinstance(e, BeingStats))

    evaluated = BeingStatsEvaluator(being=being).calculate()

    # PileOfWood has ItemStats(heft=2) by default; maps to encumberance=2
    # and other mapped stats are zero by default
    assert evaluated.strength == base.strength
    assert evaluated.dexterity == base.dexterity
    assert evaluated.constitution == base.constitution
    assert evaluated.intelligence == base.intelligence
    assert evaluated.wisdom == base.wisdom
    assert evaluated.charisma == base.charisma

    assert evaluated.encumberance == base.encumberance + 2


def test_holding_activate_and_deactivate_wire_held_and_drop(
    ctx: ExecutionContext,
    player: Player,
) -> None:
    """Holding.activate adds Held and drop; deactivation reverses both."""
    holder = Peasant.create(player=player)
    item = PileOfWood.create(player=player)

    player.played.extend([holder, item])

    holding = Holding(card=holder, card_holding=item)

    # Precondition: no Held on item, no drop action on holder
    assert next((e for e in item.effects if isinstance(e, Held)), None) is None
    assert holding.drop not in holder.actions

    # Activate Holding: should add Held to item and add drop action to holder
    holding.activate(context=ctx)

    held = next((e for e in item.effects if isinstance(e, Held)), None)
    assert held is not None
    assert held.card_held_by is holder
    assert holding.drop in holder.actions

    # Deactivate Holding: remove paired Held and remove drop from holder
    holding.deactivate(context=ctx)

    assert next((e for e in item.effects if isinstance(e, Held)), None) is None
    assert holding.drop not in holder.actions


def test_held_deactivate_removes_holding_from_holder(
    ctx: ExecutionContext,
    player: Player,
) -> None:
    """Held.deactivate removes its paired Holding effect from the holder."""
    holder = Peasant.create(player=player)
    item = PileOfWood.create(player=player)

    player.played.extend([holder, item])

    holding = Holding(card=holder, card_holding=item)
    # Ensure both effects are present as if Holding was added and activated
    holder.effects.append(holding)
    holding.state = EffectStateDef.active
    # Simulate that Holding had been activated before by adding its drop
    # action to the holder (so deactivate can remove it without error.)
    holder.actions.append(holding.drop)
    held = Held(
        card=item,
        card_held_by=holder,
        card_holding_effect=holding,
    )
    item.effects.append(held)

    # Sanity: effects present
    assert holding in holder.effects
    assert held in item.effects

    # Deactivate Held: should remove Holding from holder
    held.deactivate(context=ctx)

    assert holding not in holder.effects
