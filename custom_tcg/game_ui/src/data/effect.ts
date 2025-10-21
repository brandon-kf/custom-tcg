export default class Effect {
    session_object_id: string
    name: string
    type: string
    held_id?: string
    holding_id?: string

    constructor() {
        this.session_object_id = ""
        this.name = ""
        this.type = ""
    }
}