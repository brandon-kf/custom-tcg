import type Card from "./card"
import type Player from "./player"

export default class Action {
    session_object_id: string
    name: string
    type: string
    state: string

    card?: Card
    player?: Player

    constructor() {
        this.session_object_id = ""
        this.name = ""
        this.state = ""
        this.type = ""
    }
}
