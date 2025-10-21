"""Find cards by creating from factories."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.common.action.hold import Hold
from custom_tcg.common.card_type_def import CardTypeDef
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


class Find(Action):
    """Find cards by creating from factories."""

    finder: ICard
    cards_to_find: list[type[ICard]] | Selector
    n: int | None
    bind_n: Callable[[IExecutionContext, type[ICard]], int]

    def __init__(  # noqa: PLR0913
        self: Find,
        finder: ICard,
        cards_to_find: list[type[ICard]] | Selector,
        card: ICard,
        player: IPlayer,
        n: int | None = None,
        bind_n: Callable[[IExecutionContext, type[ICard]], int] | None = None,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create a find item action."""
        super().__init__(
            name=name or f"Find from '{finder.name}'",
            card=card,
            player=player,
            bind=bind,
            costs=costs,
        )
        self.finder = finder
        self.cards_to_find = cards_to_find
        self.n = n
        self.bind_n = bind_n or (lambda context, card_factory: n or 1)  # noqa: ARG005

        if isinstance(cards_to_find, Selector):
            self.selectors.append(cards_to_find)

    @override
    def reset_state(self: Find) -> None:
        super().reset_state()

        if isinstance(self.cards_to_find, Selector):
            self.cards_to_find.reset_state()

    @override
    def enter(self: Find, context: IExecutionContext) -> None:
        super().enter(context=context)

        card_factories: list[type[ICard]] = (
            self.cards_to_find
            if isinstance(self.cards_to_find, list)
            else cast("Selector", self.cards_to_find).selected
        )  # pyright: ignore[reportAssignmentType]

        for card_factory in card_factories:
            for _ in range(
                self.bind_n(context, card_factory),
            ):
                card: ICard = card_factory.create(player=self.player)
                self.player.played.append(card)
                if CardTypeDef.item in card.types:
                    context.execute(
                        action=Hold(
                            card_to_hold=card,
                            card_holding=self.finder,
                            card=self.card,
                            player=self.player,
                        ),
                    )
