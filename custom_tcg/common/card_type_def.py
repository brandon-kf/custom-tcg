"""Common card definitions."""

from __future__ import annotations

from custom_tcg.core.dimension import CardType


class CardTypeDef:
    """Dimensions of card types."""

    item = CardType(name="Item")
