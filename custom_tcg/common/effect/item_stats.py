"""An item stats effect."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.common.effect.being_stats import BeingStats
from custom_tcg.core.effect.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, ICard


class ItemStats(Effect):
    """An effect changing card stats of `item` type cards."""

    heft: int
    utility: int
    uniquity: int
    antiquity: int

    def __init__(  # noqa: PLR0913
        self: ItemStats,
        name: str,
        card: ICard,
        heft: int = 0,
        utility: int = 0,
        uniquity: int = 0,
        antiquity: int = 0,
        actions: list[IAction] | None = None,
    ) -> None:
        """Create an item stats effect."""
        super().__init__(
            name=name,
            card=card,
            actions=actions,
        )
        self.heft = heft
        self.utility = utility
        self.uniquity = uniquity
        self.antiquity = antiquity

    def calculate_being_stats(self: ItemStats) -> BeingStats:
        """If this item should affect a being, it should have this effect."""
        return BeingStats(
            name=(
                f"Stats from item '{self.name}' "
                f"applied to card '{self.card.name}'"
            ),
            card=self.card,
            dexterity=self.utility,
            wisdom=self.antiquity,
            charisma=self.uniquity,
            encumberance=self.heft,
        )
