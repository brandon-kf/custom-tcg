"""Deliver an item to another card."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.common.action.hold import Hold
from custom_tcg.common.card_type_def import CardTypeDef as CommonCardTypeDef
from custom_tcg.common.effect.holding import Holding
from custom_tcg.core.action import Action
from custom_tcg.core.card.select import Select
from custom_tcg.core.card.select_by_choice import SelectByChoice
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.remove_effect import RemoveEffect
from custom_tcg.core.interface import (
    IExecutionContext,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Deliver(Action):
    """Deliver an item to another card."""

    receiver: ICard | Select
    items: list[ICard] | Select

    def __init__(
        self: Deliver,
        card: ICard,
        player: IPlayer,
        receiver: ICard | Select | None = None,
        items: list[ICard] | Select | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a Deliver action."""
        super().__init__(
            name="Deliver",
            card=card,
            player=player,
            bind=bind,
            costs=None,  # Explicit, for a reason.
        )

        self.receiver = receiver or SelectByChoice(
            name="Select a being to deliver to",
            accept_n=1,
            require_n=False,
            options=(
                lambda context: [
                    card
                    for card in context.player.played
                    if CardTypeDef.being in card.types and card is not self.card
                ]
            ),
            card=card,
            player=player,
        )

        self.items = items or SelectByChoice(
            name="Select a material to deliver",
            accept_n=1,
            require_n=False,
            options=(
                lambda context: [
                    card
                    for card in context.player.played
                    for effect in card.effects
                    if CommonCardTypeDef.item in card.types
                    and isinstance(effect, Holding)
                    and effect.card_holding is self.card
                ]
            ),
            card=card,
            player=player,
        )

        for dependency in (self.receiver, self.items):
            if isinstance(dependency, Select):
                self.selectors.append(dependency)

    @override
    def enter(self: Deliver, context: IExecutionContext) -> None:
        super().enter(context=context)

        new_holder: ICard | None = (
            cast("ICard | None", next(iter(self.receiver.selected), None))
            if isinstance(self.receiver, Select)
            else self.receiver
        )

        new_held_cards: list[ICard] = (
            cast("list[ICard]", self.items.selected)
            if isinstance(self.items, Select)
            else self.items
        )

        # If receiver card is not provided (checked below,) or items list is
        # empty (provided by default,) Deliver fails to iterate items and does
        # nothing (by design.)
        if new_holder is None:
            new_held_cards = []
            new_holder = cast("ICard", new_holder)

        for held in new_held_cards:
            holding_effect: Holding = next(
                effect for effect in held.effects if isinstance(effect, Holding)
            )

            # Remove the effect from the holding card.
            context.execute(
                action=RemoveEffect(
                    effect_to_remove=holding_effect,
                    card_to_remove_from=holding_effect.card_holding,
                    card=self.card,
                    player=self.player,
                ),
            )

            # Remove the effect from the held card.
            context.execute(
                action=RemoveEffect(
                    effect_to_remove=holding_effect,
                    card_to_remove_from=holding_effect.card_held,
                    card=self.card,
                    player=self.player,
                ),
            )

            # Create a new holding effect on both holder and held.
            context.execute(
                action=Hold(
                    card_holding=new_holder,
                    card_held=held,
                    card=self.card,
                    player=self.player,
                ),
            )
