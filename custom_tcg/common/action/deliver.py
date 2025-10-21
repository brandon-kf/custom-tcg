"""Deliver an item to another card."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.common.action.hold import Hold
from custom_tcg.common.card_type_def import CardTypeDef as CommonCardTypeDef
from custom_tcg.common.effect.held import Held
from custom_tcg.common.effect.interface import IHeld
from custom_tcg.core.action import Action
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.remove_effect import RemoveEffect
from custom_tcg.core.interface import (
    ICard,
    IExecutionContext,
)

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        IExecutionContext,
        IPlayer,
    )


class Deliver(Action):
    """Deliver an item to another card."""

    receiver: ICard | Selector
    items: list[ICard] | Selector

    def __init__(  # noqa: PLR0913
        self: Deliver,
        card: ICard,
        player: IPlayer,
        receiver: ICard | Selector | None = None,
        items: list[ICard] | Selector | None = None,
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

        self.receiver = receiver or Selector(
            name="Select a being to deliver to",
            accept_n=lambda n: n == 1,
            require_n=False,
            options=(
                lambda context: [
                    card
                    for card in context.player.played
                    if CardTypeDef.being in card.types and card != self.card
                ]
            ),
            card=card,
            player=player,
        )

        self.items = items or Selector(
            name="Select a material to deliver",
            accept_n=lambda n: n == 1,
            require_n=False,
            options=(
                lambda context: [
                    card
                    for card in context.player.played
                    for effect in card.effects
                    if CommonCardTypeDef.item in card.types
                    and isinstance(effect, IHeld)
                    and effect.card_held_by == self.card
                ]
            ),
            card=card,
            player=player,
        )

        for dependency in (self.receiver, self.items):
            if isinstance(dependency, Selector):
                self.selectors.append(dependency)

    @override
    def reset_state(self: Deliver) -> None:
        super().reset_state()

        if isinstance(self.receiver, Selector):
            self.receiver.reset_state()

        if isinstance(self.items, Selector):
            self.items.reset_state()

    @override
    def enter(self: Deliver, context: IExecutionContext) -> None:
        super().enter(context=context)

        receiver_card: ICard | None = (
            cast(ICard | None, next(iter(self.receiver.selected), None))
            if isinstance(self.receiver, Selector)
            else self.receiver
        )

        item_cards: list[ICard] = (
            cast(list[ICard], self.items.selected)
            if isinstance(self.items, Selector)
            else self.items
        )

        # If receiver card is not provided (checked below,) or items list is
        # empty (provided by default,) Deliver fails to iterate items and does
        # nothing (by design.)
        if receiver_card is None:
            item_cards = []
            receiver_card = cast("ICard", receiver_card)

        for item in item_cards:
            held_effect: Held = next(
                effect for effect in item.effects if isinstance(effect, Held)
            )

            context.execute(
                action=RemoveEffect(
                    effect_to_remove=held_effect,
                    card_to_remove_from=item,
                    card=self.card,
                    player=self.player,
                ),
            )

            context.execute(
                action=Hold(
                    card_to_hold=item,
                    card_holding=receiver_card,
                    card=self.card,
                    player=self.player,
                ),
            )
