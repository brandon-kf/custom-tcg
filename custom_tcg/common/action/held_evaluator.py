"""A cost evaluator that sources from cards held by another."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.effect.interface import IHeld
from custom_tcg.core.card.cost_evaluator import CostEvaluator

if TYPE_CHECKING:
    from custom_tcg.core.card.selector import Selector
    from custom_tcg.core.interface import ICard, IPlayer


class HeldEvaluator(CostEvaluator):
    """A cost evaluator that sources from cards held by another."""

    def __init__(  # noqa: PLR0913
        self: HeldEvaluator,
        require_cards: type[ICard] | Selector,
        require_n: int,
        consume: bool,  # noqa: FBT001
        card: ICard,
        player: IPlayer,
        name: str | None = None,
    ) -> None:
        """Create a held evaluator."""
        super().__init__(
            name=name or "Evaluate required cards are held.",
            require_cards=require_cards,
            require_n=require_n,
            consume=consume,
            card=card,
            player=player,
        )

        # Adjust the simple execution to filter held cards.
        if type(require_cards) is type:
            self.require_cards.create_options = lambda context: [
                card
                for card in context.player.played
                for effect in card.effects
                if isinstance(effect, IHeld)
                and effect.card_held_by == self.card
                and card.name == require_cards.name
            ]
