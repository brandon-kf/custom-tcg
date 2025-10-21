import { ClientEvent } from "../event";
import type ClientEventMap from "../map/client";

export default class GameStartEvent extends ClientEvent {
    name: keyof ClientEventMap = "game_start"

    session_id: string

    constructor(session_id: string) {
        super()

        this.session_id = session_id
    }

    args(): string {
        return this.session_id
    }
}