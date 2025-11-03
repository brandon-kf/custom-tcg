"""Combine being stats effects to produce a summary."""

from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.interface import ICard

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard


class BeingStatsEvaluator:
    """Combine being stats effects to produce a summary."""

    being: ICard

    def __init__(self: BeingStatsEvaluator, being: ICard) -> None:
        """Create a being stats evaluator."""
        self.being = being

    def calculate(self: BeingStatsEvaluator) -> BeingStats:
        """Calculate the evaluated being stats."""
        result = BeingStats(
            name="Evaluated",
            card=self.being,
        )

        for stats in (
            effect
            for effect in self.being.effects
            if isinstance(effect, BeingStats)
        ):
            result.strength += stats.strength
            result.dexterity += stats.dexterity
            result.constitution += stats.constitution
            result.intelligence += stats.intelligence
            result.wisdom += stats.wisdom
            result.charisma += stats.charisma

            result.encumberance += stats.encumberance

        held_items: Generator[ICard, None, None] = (
            holding_effect.card_held
            for holding_effect in self.being.effects
            if isinstance(holding_effect, Holding)
            and CardTypeDef.item in holding_effect.card_held.types
        )

        item_stats_effects: Generator[ItemStats, None, None] = (
            effect
            for held_item in held_items
            for effect in held_item.effects
            if isinstance(effect, ItemStats)
        )

        for stats in (
            effect.calculate_being_stats() for effect in item_stats_effects
        ):
            result.strength += stats.strength
            result.dexterity += stats.dexterity
            result.constitution += stats.constitution
            result.intelligence += stats.intelligence
            result.wisdom += stats.wisdom
            result.charisma += stats.charisma

            result.encumberance += stats.encumberance

        return result
