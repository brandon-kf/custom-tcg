import type Player from "./player"

export default class Game {
    session_id: string
    players: Player[]
    prompt?: string

    constructor() {
        this.session_id = ""
        this.players = []
    }
}