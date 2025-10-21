import Game from "../../data/game";
import { ServerEvent } from "../event";
import type ServerEventMap from "../map/server";

export default class HostConnectedEvent extends ServerEvent {
    name: keyof ServerEventMap = "host_connected"

    game?: Game

    copy(other: HostConnectedEvent) {
        super.copy(other)

        this.game = other.game
    }
}