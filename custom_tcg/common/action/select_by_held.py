"""Select held items."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.effect.interface import IHeld
from custom_tcg.core.card.select_by_choice import SelectByChoice

if TYPE_CHECKING:
    from collections.abc import Callable

    from custom_tcg.core.interface import IAction, ICard, IPlayer


class SelectByHeld(SelectByChoice):
    """Select held items."""

    def __init__(  # noqa: PLR0913
        self: SelectByHeld,
        name: str,
        card: ICard,
        player: IPlayer,
        held_type: type[ICard],
        require_n: bool,  # noqa: FBT001
        accept_n: int | list[int],
        auto_n: bool = False,  # noqa: FBT001, FBT002
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Construct a choice selector."""
        super().__init__(
            name=name,
            card=card,
            player=player,
            options=lambda context: [
                card
                for card in context.player.played
                for effect in card.effects
                if isinstance(card, held_type)
                and isinstance(effect, IHeld)
                and effect.card_held_by == self.card
            ],
            require_n=require_n,
            auto_n=auto_n,
            accept_n=accept_n,
            bind=bind,
        )
