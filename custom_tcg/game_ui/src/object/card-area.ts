import Card from "./card"
import Object from "./object"

export default class CardArea extends Object {
    cards: (Card | CardArea)[]

    constructor(cards: (Card | CardArea)[] | undefined = undefined) {
        super()

        this.cards = cards || []
    }

    addCard(card: Card) {
        this.cards.push(card)
        this.add(card)
    }

    addCardArea(cardArea: CardArea) {
        this.cards.push(cardArea)
        this.add(cardArea)
    }

    removeCard(card: string | Card) {
        const card_id = typeof card === "string" ? card : card.cardData.session_object_id

        this.cards.forEach((child, index) => {
            if (child instanceof Card && child.cardData.session_object_id === card_id) {
                this.cards.splice(index, 1)
                this.remove(child)
            }
            else if (child instanceof CardArea) {
                child.removeCard(card)
            }
        })
    }

    findCard(card: string | Card): Card | undefined {
        const card_id = typeof card === "string" ? card : card.cardData.session_object_id
        let foundCard: Card | undefined = undefined

        this.cards.forEach((child) => {
            if (child instanceof Card && child.cardData.session_object_id === card_id) {
                foundCard = child
            }
            else if (child instanceof CardArea) {
                const recursiveFind = child.findCard(card)
                if (recursiveFind) {
                    foundCard = recursiveFind
                }
            }
        })

        return foundCard
    }

    *findCards(): Generator<Card, undefined, void> {
        for (const child of this.cards) {
            if (child instanceof Card) {
                yield child
            }
            else if (child instanceof CardArea) {
                yield* child.findCards()
            }
        }
    }

    countCards(): number {
        return Array.from(this.findCards()).length
    }

    width(): number {
        return 0
    }

    height(): number {
        return 0
    }
}