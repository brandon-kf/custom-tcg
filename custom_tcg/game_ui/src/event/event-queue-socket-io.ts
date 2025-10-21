import { io, type Socket } from "socket.io-client";
import type ActionContext from "../data/action-context";
import type Choice from "../data/choice";
import Game from "../data/game";
import type Player from "../data/player";
import ActionExecutedEvent from "./def/action-executed";
import ChoiceRequestedEvent from "./def/choice-requested";
import ConnectionEvent from "./def/connection";
import GameStartedEvent from "./def/game-started";
import GameCreatedEvent from "./def/host-connected";
import PlayerConnectedEvent from "./def/player-connected";
import { ClientEvent, type Event } from "./event";
import EventQueue from "./event-queue";
import type ClientEventMap from "./map/client";
import type ServerEventMap from "./map/server";

export default class SocketIOEventQueue extends EventQueue {
    socket: Socket<ServerEventMap, ClientEventMap>

    constructor() {
        super()

        this.socket = io("http://localhost:8000");

        const connection = new ConnectionEvent()

        this.socket.on(connection.name, () => {
            this.queue.push(new ConnectionEvent())
        })

        const gameCreated = new GameCreatedEvent()

        this.socket.on(gameCreated.name, (game: Game) => {
            const event = new GameCreatedEvent()
            event.game = game
            this.queue.push(event)
        })

        const gameStarted = new GameStartedEvent()

        this.socket.on(gameStarted.name, (game: Game) => {
            const event = new GameStartedEvent()
            event.game = game
            this.queue.push(event)
        })

        const playerConnected = new PlayerConnectedEvent()

        this.socket.on(playerConnected.name, (player: Player) => {
            const event = new PlayerConnectedEvent()
            event.player = player
            this.queue.push(event)
        })

        const actionExecuted = new ActionExecutedEvent()

        this.socket.on(actionExecuted.name, (actionContext: ActionContext) => {
            const event = new ActionExecutedEvent()
            event.actionContext = actionContext
            this.queue.push(event)
        })

        const choiceRequested = new ChoiceRequestedEvent()

        this.socket.on(choiceRequested.name, (choice: Choice) => {
            const event = new ChoiceRequestedEvent()
            event.choice = choice
            this.queue.push(event)
        })
    }

    send(e: Event) {
        if (!(e instanceof ClientEvent)) {
            throw new Error(
                `
                Cannot send an event from the Socket IO queue without defining
                it as a 'ServerEvent' and adding it to the 'ServerEventMap'
                `
            )
        }

        this.socket.emit(e.name, e.args())
        console.log(`Sending event '${e.name}'`)
    }
}