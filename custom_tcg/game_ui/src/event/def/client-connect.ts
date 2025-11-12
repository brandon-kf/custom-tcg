import { ClientEvent } from "../event"
import type ClientEventMap from "../map/client"

/**
 * Represents a client connection event.
 */
export default class PlayerConnectEvent extends ClientEvent {
    name: keyof ClientEventMap = "client_connect"

    session_id: string

    /**
     * Creates a new PlayerConnectEvent.
     * @param session_id - The session ID of the connected client.
     */
    constructor(session_id: string) {
        super()

        this.session_id = session_id
    }

    /**
     * Returns the arguments for the event.
     * @return The session ID as a string.
     */
    args(): string {
        return this.session_id
    }
}
