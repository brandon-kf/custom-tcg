"""Rest to remove exertion from all owned beings in play."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.dimension import CardTypeDef
from custom_tcg.core.effect.effect import Activated

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        IPlayer,
    )


class Rest(Action):
    """Rest to remove exertion from all owned beings in play."""

    def __init__(
        self: Rest,
        card: ICard,
        player: IPlayer,
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Create a rest action."""
        super().__init__(
            name="Rest",
            card=card,
            player=player,
            bind=bind,
        )

    @override
    def enter(self: Rest, context: IExecutionContext) -> None:
        """Remove all activated effects."""
        super().enter(context=context)

        for effect, affected_card in (
            (effect, card)
            for card in context.player.played
            for effect in card.effects
            if isinstance(effect, Activated) and CardTypeDef.being in card.types
        ):
            affected_card.effects.remove(effect)
