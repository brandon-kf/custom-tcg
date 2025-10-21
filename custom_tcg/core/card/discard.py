"""Discard cards."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.core.action import Action
from custom_tcg.core.card.selector import Selector

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Discard(Action):
    """Discard cards."""

    cards_to_discard: list[ICard] | Selector
    n: int | None

    def __init__(  # noqa: PLR0913
        self: Discard,
        cards_to_discard: list[ICard] | type[ICard] | Selector,
        card: ICard,
        player: IPlayer,
        n: int | None = None,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a discard cards action."""
        super().__init__(
            name=name or "Discard cards",
            card=card,
            player=player,
            bind=bind,
        )

        # Allow simple init with a list of card factories, but expand to
        # selector for execution.
        n_: int | None = n
        self.cards_to_discard = (
            cast("list[ICard] | Selector", cards_to_discard)
            if (isinstance(cards_to_discard, (Selector, list)))
            else Selector(
                name=(
                    f"Discard {n_} {'card' if n_ == 1 else 'cards'} "
                    f"named '{cards_to_discard.name}'"
                ),
                accept_n=lambda n: n == n_,
                require_n=True,
                options=lambda context: [
                    card
                    for card in context.player.played
                    if card.name == cards_to_discard.name
                ],
                card=card,
                player=player,
            )
        )

        self.n = n

        if isinstance(cards_to_discard, Selector):
            self.selectors.append(cards_to_discard)

    @override
    def reset_state(self: Discard) -> None:
        super().reset_state()

        if isinstance(self.cards_to_discard, Selector):
            self.cards_to_discard.reset_state()

    @override
    def enter(self: Discard, context: IExecutionContext) -> None:
        super().enter(context=context)

        cards: list[ICard] = (
            cast("list[ICard]", self.cards_to_discard)
            if isinstance(self.cards_to_discard, list)
            else cast("list[ICard]", self.cards_to_discard.selected)
        )

        for card in cards:
            if card in card.player.hand:
                card.player.hand.remove(card)

            if card in card.player.played:
                card.player.played.remove(card)

            for effect in card.effects:
                effect.deactivate(context=context)
