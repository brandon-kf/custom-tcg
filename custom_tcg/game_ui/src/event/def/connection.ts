import { ServerEvent } from "../event";
import type ServerEventMap from "../map/server";

export default class ConnectionEvent extends ServerEvent {
    name: keyof ServerEventMap = "connection"
}