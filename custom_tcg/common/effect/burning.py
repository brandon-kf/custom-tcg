"""Signify something is burning."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.core.effect.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard


class Burning(Effect):
    """An effect signifying that a card is burning."""

    def __init__(
        self: Burning,
        card: ICard,
    ) -> None:
        """Create a burning effect."""
        super().__init__(
            name=f"'{card.name}' is burning",
            card=card,
        )
