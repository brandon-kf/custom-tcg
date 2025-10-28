"""Search for an item card and find on success."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.common.action.find import Find
from custom_tcg.core.action import Action
from custom_tcg.core.dimension import ActionStateDef

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.card.select import Select
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


# TODO: Composition isn't necessarily needed here, could inherit from Find directly.  # noqa: E501, FIX002, TD002, TD003
class Search(Action):
    """Search for an item card and find on success."""

    bind_success: Callable[[IExecutionContext], bool]
    find_item_action: Find

    def __init__(  # noqa: PLR0913
        self: Search,
        searcher: ICard,
        cards_to_search_for: list[type[ICard]] | Select,
        bind_success: Callable[[IExecutionContext], bool],
        card: ICard,
        player: IPlayer,
        n: int | None = None,
        bind_n: Callable[[IExecutionContext, type[ICard]], int] | None = None,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
        costs: list[IAction] | None = None,
    ) -> None:
        """Create a search for item action."""
        super().__init__(
            name=name or "Search for cards",
            card=card,
            player=player,
            bind=bind,
            costs=costs,  # pyright: ignore[reportArgumentType]
        )
        self.bind_success = bind_success
        self.find_item_action = Find(
            finder=searcher,
            cards_to_find=cards_to_search_for,
            n=n,
            bind_n=bind_n,
            card=card,
            player=player,
        )

    @override
    def reset_state(self: Search) -> None:
        super().reset_state()

        self.find_item_action.reset_state()

    @override
    def enter(self: Search, context: IExecutionContext) -> None:
        super().enter(context=context)

        if (
            self.find_item_action.state == ActionStateDef.not_started
            and self.bind_success(context)
        ):
            context.execute(action=self.find_item_action)
            self.state = ActionStateDef.queued

        elif self.find_item_action.state == ActionStateDef.not_started:
            self.state = ActionStateDef.cancelled

        if self.find_item_action.state in (
            ActionStateDef.completed,
            ActionStateDef.cancelled,
        ):
            self.state = self.find_item_action.state
