import Card from "./card"
import CardArea from "./card-area"

export default class CardAreaStack extends CardArea {
    spacing: number
    lastCalculatedDepth: number

    constructor(spacing: number, cards: Card[] | undefined = undefined) {
        super(cards)

        this.spacing = spacing
        this.lastCalculatedDepth = 0
    }

    width(): number {
        return this.cards.length > 0 ? Card.dimension.x : 0
    }

    height(): number {
        return this.cards.length > 0 ? Card.dimension.y : 0
    }

    depth(): number {
        return this.cards.length > 0 ? this.lastCalculatedDepth : 0
    }

    update() {
        super.update()

        this.cards.forEach((card) => card.update())

        const unspacedDepth = this.cards.reduce(
            (sum, child) => sum + (child instanceof Card ? Card.dimension.z : 0),
            0,
        )
        const totalDepth = unspacedDepth + this.spacing * (this.cards.length - 1)
        let cumulativeOffset = -this.spacing

        this.cards.forEach((card) => {
            card.position.z = cumulativeOffset + this.spacing + Card.dimension.z

            cumulativeOffset += this.spacing + Card.dimension.z
        })

        this.lastCalculatedDepth = totalDepth
    }
}
