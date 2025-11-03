"""Effects used in core functionality."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, override
from uuid import uuid4

from custom_tcg.core.dimension import EffectStateDef
from custom_tcg.core.interface import IEffect, IExecutionContext

if TYPE_CHECKING:
    from custom_tcg.core.interface import IAction, ICard


logger: logging.Logger = logging.getLogger(name=__name__)


class Effect(IEffect):
    """An effect applied to a card."""

    def __init__(
        self: Effect,
        name: str,
        card: ICard,
        actions: list[IAction] | None = None,
    ) -> None:
        """Create an effect."""
        self.session_object_id = uuid4().hex
        self.name = name
        self.card = card
        self.player = card.player
        self.state = EffectStateDef.inactive
        self.actions = actions or []

    @override
    def copy(
        self: Effect,
        card: ICard,
    ) -> Effect:
        """Create an instance of this effect."""
        return self.__class__(
            name=self.name,
            card=card,
            actions=self.actions,
        )

    @override
    def activate(self: Effect, context: IExecutionContext) -> None:
        logger.info(
            "Effect '%s' changed state (%s -> %s)",
            self.name,
            self.state.name,
            EffectStateDef.active.name,
        )
        self.state = EffectStateDef.active

    @override
    def deactivate(self: Effect, context: IExecutionContext) -> None:
        logger.info(
            "Effect '%s' changed state (%s -> %s)",
            self.name,
            self.state.name,
            EffectStateDef.inactive.name,
        )
        self.state = EffectStateDef.inactive

    @override
    def bind_deactivation(self: Effect, context: IExecutionContext) -> bool:
        return False


class Activated(Effect):
    """The card has been activated."""

    def __init__(
        self: Activated,
        card: ICard,
    ) -> None:
        """Create an activated effect."""
        super().__init__(
            name="Activated",
            card=card,
        )

    @classmethod
    def create(cls: type[Activated], card: ICard) -> Activated:
        """Create an instance of this effect."""
        return cls(card=card)

    def copy(self: Activated, card: ICard) -> Activated:
        """Create an instance of this effect."""
        return self.__class__(card=card)
