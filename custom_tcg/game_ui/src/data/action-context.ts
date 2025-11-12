import Action from "./action"

/**
 * Holds context information about an action being performed in the game.
 */
export default class ActionContext {
    action: Action
    ready: Action[]
    choices: Action[]
    players: Action[]

    /**
     * Creates a new ActionContext.
     */
    constructor() {
        this.action = new Action()
        this.ready = []
        this.choices = []
        this.players = []
    }

    /**
     * Copies the data from another ActionContext into this one.
     * @param other - The ActionContext to copy from.
     */
    copy(other: ActionContext) {
        this.action = other.action
        this.ready = [...other.ready]
        this.choices = [...other.choices]
        this.players = [...other.players]
    }
}
