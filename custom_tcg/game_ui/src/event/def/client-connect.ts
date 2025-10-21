import { ClientEvent } from "../event";
import type ClientEventMap from "../map/client";

export default class PlayerConnectEvent extends ClientEvent {
    name: keyof ClientEventMap = "client_connect"

    session_id: string

    constructor(session_id: string) {
        super()

        this.session_id = session_id
    }

    args(): string {
        return this.session_id
    }
}