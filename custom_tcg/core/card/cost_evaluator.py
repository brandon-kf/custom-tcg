"""Determine the cost of an action and whether it is satisfied."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast, override

from custom_tcg.core.action import Action
from custom_tcg.core.card.discard import Discard
from custom_tcg.core.card.selector import Selector
from custom_tcg.core.dimension import ActionStateDef

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        INamed,
        IPlayer,
    )


class CostEvaluator(Action):
    """Determine the cost of an action and whether it is satisfied.

    This action is stateful, though it never provides choices. It is only
    stateful so that it may cancel execution if a cost is not satisfied.
    """

    require_cards: Selector
    require_card_factory: type[ICard] | None
    require_n: int
    consume: bool

    def __init__(  # noqa: PLR0913
        self: CostEvaluator,
        require_cards: type[ICard] | Selector,
        require_n: int,
        consume: bool,  # noqa: FBT001
        card: ICard,
        player: IPlayer,
        name: str | None = None,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a cost evaluator."""
        super().__init__(
            name=name or "Evaluate required cards are played.",
            card=card,
            player=player,
            bind=bind,
        )

        # Allow simple init with a card factory, but expand to selector
        # for execution.
        self.require_cards = (
            require_cards
            if isinstance(require_cards, Selector)
            else Selector(
                name=(
                    f"Select {require_n} "
                    f"{'copy' if require_n == 0 else 'copies'} "
                    f"of '{require_cards.name}'"
                ),
                accept_n=lambda n: n == require_n,
                require_n=False,
                options=lambda context: [
                    card
                    for card in context.player.played
                    if card.name == require_cards.name
                ],
                card=card,
                player=player,
            )
        )

        self.require_card_factory: type[ICard] | None = (
            require_cards if type(require_cards) is type else None
        )

        self.require_n = require_n
        self.consume = consume

        # The selector is disruptive to automatic execution, let's only run it
        # in advance via the `ExecutionContext` system if we plan to actually
        # select and consume specific cards. If just evaluating a certain
        # count of cards, we can do that without interruption.
        if consume:
            self.selectors.append(self.require_cards)

    @override
    def reset_state(self: CostEvaluator) -> None:
        super().reset_state()

        self.require_cards.reset_state()

    @override
    def queue(self: CostEvaluator, context: IExecutionContext) -> None:
        super().queue(context=context)

        options: list[ICard] = self.require_cards.create_options(context)

        # If we're only checking the existence of cards, the
        # `self.require_cards` selector isn't actually needed, we can check it
        # here.
        if not self.consume and len(options) < self.require_n:
            self.state = ActionStateDef.cancelled

        elif not self.consume:
            self.state = ActionStateDef.completed

        # If we are consuming cards also, we still don't need that selector, if
        # the simpler invocation with a single card factory was used.
        elif (
            self.consume
            and self.require_card_factory is not None
            and len(options) < self.require_n
        ):
            self.state = ActionStateDef.cancelled

        elif self.consume and self.require_card_factory is not None:
            self.require_cards.selected = cast(
                "list[INamed]",
                options[: self.require_n],
            )
            self.require_cards.state = ActionStateDef.completed

    @override
    def enter(self: CostEvaluator, context: IExecutionContext) -> None:
        super().enter(context=context)

        # Alright, let's handle consumption. If consuming cards to satisfy the
        # cost, we expect the selector to already have evaluated
        # successfully. That means choice and evaluation for any potential
        # cancellation has also already occurred. So, all that's left to do is
        # consume the selected cards by discarding them.
        if self.consume:
            context.execute(
                action=Discard(
                    cards_to_discard=cast(
                        "list[ICard]",
                        self.require_cards.selected,
                    ),
                    card=self.card,
                    player=self.player,
                ),
            )
