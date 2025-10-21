import type Player from "../../data/player";
import { ServerEvent } from "../event";
import type ServerEventMap from "../map/server";

export default class PlayerConnectedEvent extends ServerEvent {
    name: keyof ServerEventMap = "player_connected"

    player?: Player

    copy(other: PlayerConnectedEvent) {
        super.copy(other)

        this.player = other.player
    }
}