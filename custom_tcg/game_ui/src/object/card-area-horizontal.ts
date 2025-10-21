import Card from "./card";
import CardArea from "./card-area";

export default class CardAreaHorizontal extends CardArea {
    spacing: number
    lastCalculatedWidth: number

    constructor(spacing: number, cards: (Card | CardArea)[] | undefined = undefined) {
        super(cards)

        this.spacing = spacing
        this.lastCalculatedWidth = 0
    }

    width(): number {
        return this.lastCalculatedWidth
    }

    height(): number {
        return this.cards.length > 0 ? Card.dimension.y : 0
    }

    update() {
        super.update()

        this.cards.forEach((card) => card.update())

        const unspacedWidth = this.cards.reduce(
            (sum, child) => sum + (
                child instanceof Card ? Card.dimension.x : child.width()
            ),
            0
        )
        const totalWidth = unspacedWidth + this.spacing * (this.cards.length - 1)
        let cumulativeOffset = -this.spacing

        this.cards.forEach((card) => {
            const childWidth = (
                card instanceof Card ? Card.dimension.x : card.width()
            )

            card.position.x = (
                totalWidth / 2 - (cumulativeOffset + this.spacing + childWidth / 2)
            )

            cumulativeOffset += childWidth + this.spacing
        })

        this.lastCalculatedWidth = totalWidth
    }
}