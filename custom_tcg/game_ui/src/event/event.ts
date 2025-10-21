import type ClientEventMap from "./map/client"
import type ServerEventMap from "./map/server"

export class Event {
    name: string = "event"

    copy(other: Event) {
        if (other.name !== this.name) {
            throw new Error("Can't copy an event of a different type.")
        }
    }
}

export class ClientEvent extends Event {
    name: keyof ClientEventMap = "event"

    args() { }
}

export class ServerEvent extends Event {
    name: keyof ServerEventMap = "event"
}
