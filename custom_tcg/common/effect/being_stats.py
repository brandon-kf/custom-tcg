"""An effect changing card stats of `being` type cards."""

from __future__ import annotations

from typing import TYPE_CHECKING

from custom_tcg.core.effect.effect import Effect

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, ICard


class BeingStats(Effect):
    """An effect changing card stats of `being` type cards."""

    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int

    encumberance: int

    def __init__(  # noqa: PLR0913
        self: BeingStats,
        name: str,
        card: ICard,
        strength: int = 0,
        dexterity: int = 0,
        constitution: int = 0,
        intelligence: int = 0,
        wisdom: int = 0,
        charisma: int = 0,
        encumberance: int = 0,
        actions: list[IAction] | None = None,
    ) -> None:
        """Create a being stats effect."""
        super().__init__(
            name=name,
            card=card,
            actions=actions,
        )
        self.strength = strength
        self.dexterity = dexterity
        self.constitution = constitution
        self.intelligence = intelligence
        self.wisdom = wisdom
        self.charisma = charisma

        self.encumberance = encumberance
