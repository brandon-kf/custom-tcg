import Action from "./action"

export default class ActionContext {
    action: Action
    ready: Action[]
    choices: Action[]
    players: Action[]

    constructor() {
        this.action = new Action()
        this.ready = []
        this.choices = []
        this.players = []
    }

    copy(other: ActionContext) {
        this.action = other.action
        this.ready = [...other.ready]
        this.choices = [...other.choices]
        this.players = [...other.players]
    }
}