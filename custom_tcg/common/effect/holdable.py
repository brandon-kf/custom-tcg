"""Signify something is burning."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.core.effect.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.core.interface import ICard


class Holdable(Effect):
    """An effect signifying that a card is holdable."""

    def __init__(
        self: Holdable,
        card: ICard,
    ) -> None:
        """Create a holdable effect."""
        super().__init__(
            name=f"'{card.name}' is holdable",
            card=card,
        )
