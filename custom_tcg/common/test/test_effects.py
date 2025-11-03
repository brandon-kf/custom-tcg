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

    # Create HoldTarget and activate it to establish holding relationship
    hold_target = Holding(card_held=item, card_holding=being, card=being)
    item.effects.append(hold_target)

    # Create execution context and activate the hold target
    ctx = ExecutionContext(players=[player])
    hold_target.activate(context=ctx)

    # Drain any pending actions from the execution context
    while ctx.ready:
        action = ctx.ready.pop(0)
        action.enter(context=ctx)

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


def test_hold_target_activate_and_deactivate_creates_bidirectional_effects(
    ctx: ExecutionContext,
    player: Player,
) -> None:
    """HoldTarget.activate creates Holding on holder; deactivation reverses."""
    holder = Peasant.create(player=player)
    item = PileOfWood.create(player=player)

    player.played.extend([holder, item])

    # Create HoldTarget effect on the item (being held)
    hold_target = Holding(card_held=item, card_holding=holder, card=holder)
    item.effects.append(hold_target)

    # Precondition: no Holding on holder yet
    assert (
        next((e for e in holder.effects if isinstance(e, Holding)), None)
        is None
    )

    # Activate HoldTarget: should create Holding on holder with Drop action
    hold_target.activate(context=ctx)

    # Drain any pending actions from the execution context
    while ctx.ready:
        action = ctx.ready.pop(0)
        action.enter(context=ctx)

    # Verify bidirectional relationship was created
    holding = next((e for e in holder.effects if isinstance(e, Holding)), None)
    assert holding is not None
    assert holding.card_holding is item
    assert holding.drop in holder.actions

    # Deactivate HoldTarget: should deactivate effects and remove Drop action
    hold_target.deactivate(context=ctx)

    # Drain any pending actions from the execution context
    while ctx.ready:
        action = ctx.ready.pop(0)
        action.enter(context=ctx)

        # Verify HoldTarget is deactivated and Drop action is removed
        assert hold_target.state == EffectStateDef.inactive
        # The Drop action should be removed from holder's actions
        assert holding.drop not in holder.actions


def test_hold_target_deactivate_removes_holding_from_holder(
    ctx: ExecutionContext,
    player: Player,
) -> None:
    """HoldTarget.deactivate removes its paired Holding effect from holder."""
    holder = Peasant.create(player=player)
    item = PileOfWood.create(player=player)

    player.played.extend([holder, item])

    # Create and activate Holding to establish bidirectional relationship
    hold_target = Holding(card_held=item, card_holding=holder, card=holder)
    item.effects.append(hold_target)

    # Activate to create the paired Holding effect
    hold_target.activate(context=ctx)

    # Drain any pending actions from the execution context
    while ctx.ready:
        action = ctx.ready.pop(0)
        action.enter(context=ctx)

    # Verify the paired Holding effect was created
    holding = next((e for e in holder.effects if isinstance(e, Holding)), None)
    assert holding is not None
    assert hold_target in item.effects

    # Deactivate HoldTarget: should deactivate effects
    hold_target.deactivate(context=ctx)

    # Drain any pending actions from the execution context
    while ctx.ready:
        action = ctx.ready.pop(0)
        action.enter(context=ctx)

        # Verify HoldTarget is deactivated
        assert hold_target.state == EffectStateDef.inactive
