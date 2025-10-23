"""A generic selector that provides selected objects."""

from __future__ import annotations

import logging
import sys
from collections.abc import Callable
from typing import TYPE_CHECKING, override

from custom_tcg.core.action import Action
from custom_tcg.core.dimension import ActionStateDef
from custom_tcg.core.interface import IExecutionContext
from custom_tcg.core.util import list_randomize

if TYPE_CHECKING:
    from custom_tcg.core.interface import (
        IAction,
        ICard,
        IExecutionContext,
        INamed,
        IPlayer,
    )


logger: logging.Logger = logging.getLogger(name=__name__)


class Select(Action):
    """A generic selector that provides selected objects."""

    options: list[INamed]
    selected: list[INamed]
    n: int
    require_n: bool
    randomize: bool

    create_options: Callable[[IExecutionContext], list]

    def __init__(  # noqa: PLR0913
        self: Select,
        name: str,
        card: ICard,
        player: IPlayer,
        options: list | Callable[[IExecutionContext], list],
        n: int = sys.maxsize,
        require_n: bool = False,  # noqa: FBT001, FBT002
        randomize: bool = False,  # noqa: FBT001, FBT002
        bind: Callable[[IAction, ICard, IPlayer], bool] | None = None,
    ) -> None:
        """Construct a selector."""
        super().__init__(
            name=name,
            card=card,
            player=player,
            bind=bind,
        )

        self.n = n
        self.require_n = require_n
        self.randomize = randomize

        # Unify option typing for simplicity sake.
        self.create_options = (
            options
            if isinstance(options, Callable)
            else (lambda context: list(options))  # noqa: ARG005
        )

        self._init_state()

    def _init_state(self: Select) -> None:
        self.reset_state()

    @override
    def reset_state(self: Select) -> None:
        """Get this selector ready for its next use."""
        super().reset_state()
        self.options = []
        self.selected = []

    @override
    def queue(self: Select, context: IExecutionContext) -> None:
        super().queue(context=context)

        self.options = self.create_options(context)

        if not self.speculate():
            logger.info("Select '%s' speculatively cancelled", self.name)
            logger.info(
                "Select required n of %d failed with options [%s]",
                self.n,
                ",".join(option.name for option in self.options),
            )
            self.state = ActionStateDef.cancelled

    @override
    def enter(self: Select, context: IExecutionContext) -> None:
        """Create selector choices."""
        super().enter(context=context)

        self.options = self.create_options(context)

        if self.randomize:
            self.options = list_randomize(ordered=self.options)

        self.selected = self.options[: self.n]

    def speculate(self: Select) -> bool:
        """Decide if this selection is even possible."""
        return (
            self.require_n and len(self.options) > self.n
        ) or not self.require_n
