import type Action from "./action"
import type Effect from "./effect"

export default class Card {
    session_object_id: string
    name: string
    types: string[]
    effects: Effect[]
    prompt?: string
    choices?: Action[]

    constructor() {
        this.session_object_id = ""
        this.name = ""
        this.types = []
        this.effects = []
    }
}
