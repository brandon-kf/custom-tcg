"""A FastAPI implementation for the tcg game engine."""

from __future__ import annotations

import logging
from asyncio import sleep
from dataclasses import dataclass
from typing import Any, cast

import socketio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from custom_tcg.common.player import p1, p2
from custom_tcg.core.game import ActionStateDef
from custom_tcg.core.game import Game as CoreGame
from custom_tcg.core.interface import IAction, IActionContext, IPlayer
from custom_tcg.game_api.response.action_context import ActionContext
from custom_tcg.game_api.response.choice import Choice
from custom_tcg.game_api.response.game import Game
from custom_tcg.game_api.response.player import Player
from custom_tcg.game_api.socket_action_queue import SocketActionQueue
from custom_tcg.main import setup

setup()

app: FastAPI = FastAPI()

sio = socketio.AsyncServer(
    async_mode="asgi",
    cors_allowed_origins=[],
    engineio_logger=True,
)

origins: list[str] = ["http://localhost:5173"]

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=[
        "*",
    ],  # Allows all HTTP methods (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Allows all headers
)

logger: logging.Logger = logging.getLogger(name=__name__)


@dataclass
class SessionContext:
    players: list[IPlayer]
    game: CoreGame
    completed_queue_index: int


session_data: dict[str, SessionContext] = {}


@sio.event
async def connect(sid: str, environ: Any) -> None:  # noqa: ARG001, ANN401
    """Accept a new Socket IO connection."""
    logger.info("Connected to new socket with sid '%s'", sid)
    await sio.emit(event="connection")


@sio.event
async def disconnect(sid: str) -> None:
    """Disconnect a Socket IO connection."""
    logger.info("Disconnected from socket with sid '%s'", sid)


@sio.event
async def host_connect(sid: str, player_id: str) -> None:
    """Player joins a created game."""
    logger.info("Player connected.")

    player1: IPlayer = p1()  # Lookup from player_id.
    game: CoreGame = CoreGame(players=[player1])
    game.context.completed = SocketActionQueue(
        socket=sio,
        event_name="action_executed",
    )

    session_data[game.session_id] = SessionContext(
        players=[player1],
        game=game,
        completed_queue_index=-1,
    )

    session_data[game.session_id].players.append(player1)
    await sio.emit(
        to=sid,
        event="host_connected",
        data=Game(game=game).serialize(),
    )

    await sleep(delay=1)

    # Connect player 2, simulating join from elsewhere.
    await client_connect(
        sid=sid,
        session_id=game.session_id,
        player_id="<not used yet>",
    )


@sio.event
async def client_connect(sid: str, session_id: str, player_id: str) -> None:
    """Player joins a created game."""
    logger.info("Player connected.")
    session_context: SessionContext = session_data[session_id]

    player2: IPlayer = p2()  # Lookup from player_id.
    session_context.players.append(player2)
    session_context.game.add_player(player2)

    # This only gets emitted to other players. There should be a
    # "client_connected" event sent with all game data to the client connecting.
    await sio.emit(
        to=sid,
        event="player_connected",
        data=Player(player=player2).serialize(),
    )


@sio.event
async def game_start(
    sid: str,
    session_id: str,
) -> None:
    """Host player signals the game should start."""
    logger.info("Game started.")

    session_context: SessionContext = session_data[session_id]

    session_context.game.setup()
    session_context.game.start()

    await sio.emit(
        to=sid,
        event="game_started",
        data=Game(game=session_context.game).serialize(),
    )

    while True:
        await sleep(delay=1)
        await send_new_action_executions(
            sid=sid,
            session_context=session_context,
        )


async def send_new_action_executions(
    sid: str,
    session_context: SessionContext,
) -> None:
    logger.info("Searching for events.")

    new_actions: list[IActionContext] = cast(
        "list[IActionContext]",
        session_context.game.context.completed,
    )[session_context.completed_queue_index + 1 :]

    if len(new_actions) > 0:
        for action_context in new_actions:
            await sio.emit(
                to=sid,
                event="action_executed",
                data=ActionContext(
                    action_context=action_context,
                ).serialize(),
            )
        session_context.completed_queue_index += len(new_actions)

    elif (
        len(session_context.game.context.ready) > 0
        and session_context.game.context.ready[0].state
        == ActionStateDef.input_requested
    ):
        await sio.emit(
            to=sid,
            event="choice_requested",
            data=Choice(context=session_context.game.context).serialize(),
        )


@sio.event
async def choice_confirmed(sid: str, ids: tuple[str, str]) -> None:
    session_id: str
    action_id: str
    (session_id, action_id) = ids
    session_context: SessionContext = session_data[session_id]

    chosen_action: IAction = next(
        choice
        for choice in session_context.game.context.choices
        if choice.session_object_id == action_id
    )
    session_context.game.choose(action=chosen_action)


app.mount(path="/socket.io", app=socketio.ASGIApp(socketio_server=sio))
