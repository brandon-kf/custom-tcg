import Card from "./card";
import CardArea from "./card-area";


export default class CardAreaOffset extends CardArea {
    spacing: number
    lastCalculatedWidth: number
    lastCalculatedHeight: number

    constructor(spacing: number, cards: Card[] | undefined = undefined) {
        super(cards)

        this.spacing = spacing
        this.lastCalculatedWidth = 0
        this.lastCalculatedHeight = 0
    }

    width(): number {
        return this.lastCalculatedWidth
    }

    height(): number {
        return this.lastCalculatedHeight
    }

    update() {
        super.update()

        this.cards.forEach((card) => card.update())

        const nCards = this.cards.length
        const totalWidth = this.spacing * (nCards - 1) + Card.dimension.x
        const totalHeight = this.spacing * (nCards - 1) + Card.dimension.y

        this.cards.forEach((card, index) => {
            card.position.x = -index * this.spacing - Card.dimension.x / 2 + totalWidth / 2
            card.position.y = -index * this.spacing - Card.dimension.y / 2 + totalHeight / 2
        })

        this.lastCalculatedWidth = totalWidth
        this.lastCalculatedHeight = totalHeight
    }
}