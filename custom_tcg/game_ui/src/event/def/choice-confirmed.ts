import { ClientEvent } from "../event"
import type ClientEventMap from "../map/client"

export default class ChoiceConfirmedEvent extends ClientEvent {
    name: keyof ClientEventMap = "choice_confirmed"

    session_id: string
    action_id: string

    constructor(session_id: string, action_id: string) {
        super()

        this.session_id = session_id
        this.action_id = action_id
    }

    args(): [string, string] {
        return [this.session_id, this.action_id]
    }
}
