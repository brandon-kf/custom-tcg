"""Allow a card to hold another card."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override

from custom_tcg.common.card_type_def import CardTypeDef
from custom_tcg.common.effect.being_stats_evaluator import BeingStatsEvaluator
from custom_tcg.common.effect.holding import Holding
from custom_tcg.common.effect.item_stats import ItemStats
from custom_tcg.core.action import Action
from custom_tcg.core.effect.add_effect import AddEffect

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.common.effect.being_stats import BeingStats
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )

logger: logging.Logger = logging.getLogger(name=__name__)


class Hold(Action):
    """Allow a card to hold another card."""

    card_to_hold: ICard
    card_holding: ICard

    def __init__(
        self: Hold,
        card_to_hold: ICard,
        card_holding: ICard,
        card: ICard,
        player: IPlayer,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a hold action."""
        super().__init__(
            name=f"'{card_holding.name}' holds '{card_to_hold.name}'",
            card=card,
            player=player,
            bind=bind,
        )
        self.card_to_hold = card_to_hold
        self.card_holding = card_holding

    @override
    def enter(self: Hold, context: IExecutionContext) -> None:
        super().enter(context=context)

        would_become_overencumbered: bool = False

        if CardTypeDef.item in self.card_to_hold.types:
            item_stats: ItemStats = next(
                effect
                for effect in self.card_to_hold.effects
                if isinstance(effect, ItemStats)
            )

            item_encumberance_added: int = (
                item_stats.calculate_being_stats().encumberance
            )

            being_current_stats: BeingStats = BeingStatsEvaluator(
                being=self.card_holding,
            ).calculate()

            logger.info(
                (
                    "Hold check: encumberance stats are "
                    "(current for holder: %s, "
                    "added by held: %s, "
                    "holder constitution: %s)"
                ),
                being_current_stats.encumberance,
                item_encumberance_added,
                being_current_stats.constitution,
            )

            if (
                being_current_stats.encumberance + item_encumberance_added
                > being_current_stats.constitution
            ):
                logger.info(
                    "Attempting '%s' would cause overencumberance, hold failed",
                    self.name,
                )
                would_become_overencumbered = True

        if not would_become_overencumbered:
            context.execute(
                action=AddEffect(
                    effect_to_add=Holding(
                        card=self.card_holding,
                        card_holding=self.card_to_hold,
                    ),
                    card_to_add_to=self.card_holding,
                    card=self.card,
                    player=self.player,
                ),
            )
