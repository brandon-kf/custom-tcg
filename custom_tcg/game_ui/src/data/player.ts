import type Card from "./card"

export default class Player {
    session_object_id: string
    name: string
    deck_size: number
    deck: Card[]
    hand: Card[]
    played: Card[]
    discard: Card[]

    constructor() {
        this.session_object_id = ""
        this.name = ""
        this.deck_size = 0
        this.deck = []
        this.hand = []
        this.played = []
        this.discard = []
    }
}
