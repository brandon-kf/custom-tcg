import Game from "../../data/game";
import { ServerEvent } from "../event";
import type ServerEventMap from "../map/server";

export default class GameStartedEvent extends ServerEvent {
    name: keyof ServerEventMap = "game_started"

    game?: Game

    copy(other: GameStartedEvent) {
        super.copy(other)

        this.game = other.game
    }
}