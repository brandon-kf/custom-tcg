import type Action from "./action"
import Player from "./player"

export default class Choice {
    prompt: string
    actions: Action[]
    player: Player
    choiceMap: Record<string, Action[]>

    constructor() {
        this.prompt = ""
        this.actions = []
        this.player = new Player()
        this.choiceMap = {}
    }
}
