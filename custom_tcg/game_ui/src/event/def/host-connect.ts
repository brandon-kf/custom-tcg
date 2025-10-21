import { ClientEvent } from "../event";
import type ClientEventMap from "../map/client";

export default class HostConnectEvent extends ClientEvent {
    name: keyof ClientEventMap = "host_connect"

    player_id: string

    constructor(player_id: string) {
        super()

        this.player_id = player_id
    }
}