"""Dimensions used to define core objects."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class CardType:
    """Dimensions for card type."""

    name: str


class CardTypeDef:
    """Core dimensions for card type."""

    process = CardType(name="Process")
    being = CardType(name="Being")


@dataclass
class CardClass:
    """Dimensions for card class, in hierarchy under types and classes."""

    name: str
    type_parents: list[CardType]
    class_parents: list[CardClass]


class CardClassDef:
    """Core dimensions for card class."""

    play = CardClass(
        name="Play",
        type_parents=[CardTypeDef.process],
        class_parents=[],
    )
    rest = CardClass(
        name="Rest",
        type_parents=[CardTypeDef.process],
        class_parents=[],
    )


@dataclass
class ActionState:
    """Dimensions for the status of an action."""

    name: str


class ActionStateDef:
    """Common dimensions for action state."""

    not_started = ActionState(name="Not started")
    queued = ActionState(name="Queued")
    entered = ActionState(name="Entered")
    input_requested = ActionState(name="Input requested")
    input_received = ActionState(name="Input received")
    completed = ActionState(name="Completed")
    cancelled = ActionState(name="Cancelled")
    stateless = ActionState(name="Stateless")


@dataclass
class EffectState:
    """Dimensions for the status of an effect."""

    name: str


class EffectStateDef:
    """Common dimensions for effect state."""

    inactive = EffectState(name="Inactive")
    active = EffectState(name="Active")
