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
        card: ICard,
        name: str | None = None,
        actions: list[IAction] | None = None,
        card_affected: ICard | None = None,
        card_affecting: ICard | None = None,
    ) -> None:
        """Create an effect."""
        self.session_object_id = uuid4().hex
        self.name = name or self.__class__.__name__
        self.card = card
        self.player = card.player
        self.state = EffectStateDef.inactive
        self.actions = actions or []
        self.card_affected = card_affected or card
        self.card_affecting = card_affecting or card

    @classmethod
    def create(cls: type[Effect], card: ICard) -> IEffect:
        """Create an instance of this effect."""
        return cls(card=card)

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
            card_affected=self.card_affected,
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

        if self not in self.card_affected.effects:
            self.card_affected.effects.append(self)

    @override
    def deactivate(self: Effect, context: IExecutionContext) -> None:
        logger.info(
            "Effect '%s' changed state (%s -> %s)",
            self.name,
            self.state.name,
            EffectStateDef.inactive.name,
        )

        self.state = EffectStateDef.inactive

        if self in self.card_affected.effects:
            self.card_affected.effects.remove(self)

    @override
    def bind_deactivation(self: Effect, context: IExecutionContext) -> bool:
        return False
