"""Feast or famine effects."""

from __future__ import annotations

from custom_tcg.core.effect.effect import Effect


class HungerEffect(Effect):
    """A hunger effect."""


class FedEffect(Effect):
    """A lack of hunger effect."""
