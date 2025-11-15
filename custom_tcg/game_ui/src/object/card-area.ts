import Card from "./card"
import Object from "./object"

/**
 * Represents an area where cards can be placed.
 */
export default class CardArea extends Object {
    cards: (Card | CardArea)[]

    /**
     * Creates a new CardArea.
     * @param cards The initial cards or card areas in the area.
     */
    constructor(cards: (Card | CardArea)[] | undefined = undefined) {
        super()

        this.cards = cards ?? []
    }

    /**
     * Adds a card or card area to the card area.
     * @param cardOrArea The card or card area to add.
     */
    addCardOrArea(cardOrArea: Card | CardArea) {
        this.cards.push(cardOrArea)
        this.add(cardOrArea)
    }

    /**
     * Traverses all cards and card areas in the card area, applying a callback function to each.
     * @param callback The callback function to apply to each card or card area.
     */
    traverse(callback: (parent: CardArea, child: Card | CardArea) => void) {
        this.cards.forEach((child) => {
            callback(this, child)
            if (child instanceof CardArea) {
                child.traverse(callback)
            }
        })
    }

    /**
     * Removes a card or card area from the card area.
     * @param card The card or card area to remove.
     */
    removeCardOrArea(card: string | Card | CardArea) {
        let id: string | CardArea
        if (card instanceof Card) {
            id = card.cardData.session_object_id
        } else if (card instanceof CardArea) {
            id = card
        } else if (typeof card === "string") {
            id = card
        } else {
            throw new Error("Invalid card or card area to remove.")
        }

        this.traverse((parent, child) => {
            if (
                (child instanceof Card &&
                    typeof id === "string" &&
                    child.cardData.session_object_id === id) ||
                (child instanceof CardArea && id instanceof CardArea && child === id)
            ) {
                parent.cards.splice(parent.cards.indexOf(child), 1)
                parent.remove(child)
            }
        })
    }

    /**
     * Finds a card in the card area or its sub-areas.
     * @param card The card or card ID to find.
     * @return The found card, or undefined if not found.
     */
    findCardOrArea(card: string | Card | CardArea): Card | CardArea | undefined {
        let id: string | CardArea
        if (card instanceof Card) {
            id = card.cardData.session_object_id
        } else if (card instanceof CardArea) {
            id = card
        } else if (typeof card === "string") {
            id = card
        } else {
            throw new Error("Invalid card or card area to find.")
        }

        let foundCard: Card | CardArea | undefined = undefined

        this.traverse((_parent, child) => {
            if (
                (child instanceof Card &&
                    typeof id === "string" &&
                    child.cardData.session_object_id === id) ||
                (child instanceof CardArea && id instanceof CardArea && child === id)
            ) {
                foundCard = child
            }
        })

        return foundCard
    }

    /**
     * Finds a card in the card area or its sub-areas.
     * @param card The card or card ID to find.
     * @return The found card, or undefined if not found.
     */
    findCard(card: string | Card): Card | undefined {
        let id: string

        if (card instanceof Card) {
            id = card.cardData.session_object_id
        } else if (typeof card === "string") {
            id = card
        } else {
            throw new Error("Invalid card or card area to find.")
        }

        let foundCard: Card | undefined = undefined

        this.traverse((_parent, child) => {
            if (child instanceof Card && child.cardData.session_object_id === id) {
                foundCard = child
            }
        })

        return foundCard
    }

    /**
     * Finds a card area in the card area or its sub-areas.
     * @param area The card area to find.
     * @return The found card area, or undefined if not found.
     */
    findCardArea(area: CardArea): CardArea | undefined {
        let foundArea: CardArea | undefined = undefined

        this.traverse((_parent, child) => {
            if (child instanceof CardArea && child === area) {
                foundArea = child
            }
        })

        return foundArea
    }

    /**
     * Finds all cards in the card area and its sub-areas.
     * @return A generator yielding all found cards.
     */
    *findCards(): Generator<Card, undefined, void> {
        for (const child of this.cards) {
            if (child instanceof Card) {
                yield child
            } else if (child instanceof CardArea) {
                yield* child.findCards()
            }
        }
    }

    /**
     * Counts the number of cards in the card area and its sub-areas.
     * @return The number of cards.
     */
    countCards(): number {
        return Array.from(this.findCards()).length
    }

    /**
     * Returns the width of the card area.
     * @return The width of the card area.
     */
    width(): number {
        return 0
    }

    /**
     * Returns the height of the card area.
     * @return The height of the card area.
     */
    height(): number {
        return 0
    }
}
