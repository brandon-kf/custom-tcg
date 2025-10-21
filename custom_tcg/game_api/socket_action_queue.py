"""Define an event queue to interface the core engine with socket io."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from custom_tcg.core.interface import IActionContext, IActionQueue

if TYPE_CHECKING:
    import socketio

logger: logging.Logger = logging.getLogger(name=__name__)


class SocketActionQueue(list[IActionContext], IActionQueue):
    """An event queue to interface the core engine with socket io."""

    socket: socketio.AsyncServer
    event_name: str

    def __init__(
        self: SocketActionQueue,
        socket: socketio.AsyncServer,
        event_name: str | None = None,
    ) -> None:
        """Create an event queue instance."""
        self.socket = socket
        self.event_name = event_name or "new_event"
