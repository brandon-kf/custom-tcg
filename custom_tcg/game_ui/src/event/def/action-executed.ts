import type ActionContext from "../../data/action-context"
import { ServerEvent } from "../event"
import type ServerEventMap from "../map/server"

export default class ActionExecutedEvent extends ServerEvent {
    name: keyof ServerEventMap = "action_executed"

    actionContext?: ActionContext

    copy(other: ActionExecutedEvent) {
        super.copy(other)

        this.actionContext = other.actionContext
    }
}
