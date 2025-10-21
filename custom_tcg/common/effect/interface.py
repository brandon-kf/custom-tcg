"""Interface definitions for common effects."""

from custom_tcg.core.interface import ICard, IEffect


class IHolding(IEffect):
    """An effect showing that a card is holding another."""

    card_holding: ICard


class IHeld(IEffect):
    """An effect showing that a card is held by another."""

    card_held_by: ICard
