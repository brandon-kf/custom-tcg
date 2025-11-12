import * as THREE from "three"

import PlayerData from "../data/player"
import Card from "./card"
import CardArea from "./card-area"
import CardAreaHorizontal from "./card-area-horizontal"
import CardAreaOffset from "./card-area-offset"
import ObjectBase from "./object"

export default class Player extends ObjectBase {
    static dimension: THREE.Vector3 = new THREE.Vector3(6000, 1000, 5000)
    static hand_spacing = 100
    static played_spacing = 300

    playerData: PlayerData

    deck: CardArea
    hand: CardArea
    playedRow1: CardArea
    playedRow2: CardArea
    playedRow3: CardArea
    discard: CardArea

    positionBlock: THREE.Mesh
    playmat: THREE.Mesh

    updateAll: boolean

    constructor(playerData: PlayerData) {
        super()

        this.playerData = playerData

        this.deck = new CardArea()
        this.hand = new CardAreaHorizontal(Player.hand_spacing)
            .translateY(1600)
            .translateZ(450)
            .rotateX(Math.PI / 4)
        this.playedRow1 = new CardAreaHorizontal(Player.played_spacing).translateZ(2000)
        this.playedRow2 = new CardAreaHorizontal(Player.played_spacing).translateZ(3000)
        this.playedRow3 = new CardAreaHorizontal(Player.played_spacing).translateZ(4000)
        this.discard = new CardArea()
        ;[this.playedRow1, this.playedRow2, this.playedRow3].forEach((area) =>
            area.translateY(200).rotateX(Math.PI / 2),
        )

        const blockGeometry = new THREE.BoxGeometry(500, 500, 500)
        const greyMaterial = new THREE.MeshBasicMaterial({ color: 0x555555 })
        this.positionBlock = new THREE.Mesh(blockGeometry, greyMaterial)
            .translateY(3000)
            .translateZ(-1000)

        const playmatGeometry = new THREE.BoxGeometry(
            Player.dimension.x - 500,
            100,
            Player.dimension.z - 500,
        )
        this.playmat = new THREE.Mesh(playmatGeometry, greyMaterial)
            .translateY(100)
            .translateZ(Player.dimension.z / 2)

        this.updateAll = false
    }

    setup() {
        super.setup()

        this.add(
            this.deck,
            this.hand,
            this.playedRow1,
            this.playedRow2,
            this.playedRow3,
            this.discard,
            this.positionBlock,
            this.playmat,
        )
    }

    update() {
        super.update()

        if (
            this.updateAll ||
            Math.abs(this.playerData.hand.length - this.hand.countCards()) > 0.1
        ) {
            console.log(`Update cards in hand for player '${this.playerData.name}'`)
            this.syncHand()
        }

        if (
            this.updateAll ||
            Math.abs(
                this.playerData.played.length -
                    this.playedRow1.countCards() -
                    this.playedRow2.countCards() -
                    this.playedRow3.countCards(),
            ) > 0.1
        ) {
            console.log(`Update cards in play for player '${this.playerData.name}'`)

            this.syncPlayed()
            this.restructureRowsAccordingToOffsetRules()
        }

        for (const area of [this.hand, this.playedRow1, this.playedRow2, this.playedRow3]) {
            area.update()
        }

        this.updateAll = false
    }

    syncHand() {
        const handIds: string[] = []

        for (const cardData of this.playerData.hand) {
            const foundCard = this.hand.findCard(cardData.session_object_id)

            if (!foundCard) {
                const cardObject = new Card(cardData)

                this.hand.addCard(cardObject)
            }

            handIds.push(cardData.session_object_id)
        }

        for (const card of this.hand.findCards()) {
            if (!handIds.includes(card.cardData.session_object_id)) {
                this.hand.removeCard(card)
            }
        }
    }

    syncPlayed() {
        const playedIds: string[] = []

        for (const cardData of this.playerData.played) {
            let card: Card | undefined =
                this.playedRow1.findCard(cardData.session_object_id) ||
                this.playedRow2.findCard(cardData.session_object_id) ||
                this.playedRow3.findCard(cardData.session_object_id)
            let newCard: boolean = card === undefined

            if (!card) {
                card = new Card(cardData)
            }

            if (newCard && card.isProcess()) {
                this.playedRow3.addCard(card)
            } else if (newCard && card.isBeing()) {
                this.playedRow2.addCard(card)
            } else if (newCard) {
                this.playedRow1.addCard(card)
            }

            playedIds.push(cardData.session_object_id)
        }

        for (const area of [this.playedRow1, this.playedRow2, this.playedRow3]) {
            for (const card of area.findCards()) {
                if (!playedIds.includes(card.cardData.session_object_id)) {
                    area.removeCard(card)
                }
            }
        }
    }

    restructureRowsAccordingToOffsetRules() {
        const beingGroups: Record<string, Card[]> = {}
        const itemGroups: Record<string, Card[]> = {}

        for (const card of [...this.playedRow2.findCards(), ...this.playedRow1.findCards()]) {
            const isBeing = card.isBeing()
            const isItem = card.isItem()
            const isHolding = isBeing && card.isHolding().length > 0
            const isHeld = !isBeing && !!card.isHeld()

            if (isBeing && isHolding) {
                console.log(`Restructure for being holding on card ${card.cardData.name}`)
                this.restructureForBeingHolding(card)
            } else if (isBeing && !isHolding && !beingGroups.hasOwnProperty(card.cardData.name)) {
                console.log(`Restructure for being grouping includes card ${card.cardData.name}`)
                beingGroups[card.cardData.name] = [card]
            } else if (isBeing && !isHolding && beingGroups.hasOwnProperty(card.cardData.name)) {
                console.log(`Restructure for being grouping includes card ${card.cardData.name}`)
                beingGroups[card.cardData.name].push(card)
            } else if (isItem && !isHeld && !itemGroups.hasOwnProperty(card.cardData.name)) {
                console.log(`Restructure for item grouping includes card ${card.cardData.name}`)
                itemGroups[card.cardData.name] = [card]
            } else if (isItem && !isHeld && itemGroups.hasOwnProperty(card.cardData.name)) {
                console.log(`Restructure for item grouping includes card ${card.cardData.name}`)
                itemGroups[card.cardData.name].push(card)
            }
        }

        this.restructureForBeingGrouping(beingGroups)
        this.restructureForItemGrouping(itemGroups)
    }

    restructureForBeingHolding(card: Card) {
        let cardArea = card.parent instanceof CardAreaOffset ? card.parent : undefined
        let beingCount = 0

        if (cardArea) {
            for (const card of cardArea.findCards()) {
                if (card.isBeing()) {
                    beingCount += 1
                }
            }
        }

        if (cardArea) {
            cardArea.removeCard(card)
        }

        if (!cardArea || beingCount > 1) {
            cardArea = new CardAreaOffset(150)

            this.playedRow2.removeCard(card)
            this.playedRow2.addCardArea(cardArea)
        }

        for (const cardId of card.isHolding()) {
            const inRow2 = this.playedRow2.findCard(cardId)
            const inRow1 = this.playedRow1.findCard(cardId)
            const held = inRow2 || inRow1!

            // Handle the case where this item changed hands from a different being holding area.
            if (held && inRow2 && inRow2.parent !== cardArea) {
                this.playedRow2.removeCard(inRow2)
            }

            // Handle the case where this item was in the item area.
            else if (held && inRow1) {
                this.playedRow1.removeCard(inRow1)
            }

            if (held && held.parent !== cardArea) {
                cardArea.addCard(held)
            }
        }

        cardArea.addCard(card)
    }

    restructureForBeingGrouping(beingGroups: Record<string, Card[]>) {
        for (const cards of Object.values(beingGroups)) {
            let cardArea: CardArea | undefined

            for (const card of cards) {
                if (card.parent instanceof CardAreaOffset && this.playedRow2.findCard(card)) {
                    cardArea = card.parent
                } else {
                    this.playedRow2.removeCard(card)
                }
            }

            if (!cardArea) {
                cardArea = new CardAreaOffset(150)
                this.playedRow2.addCardArea(cardArea)
            }

            for (const card of cards) {
                if (card.parent !== cardArea) {
                    cardArea.addCard(card)
                }
            }
        }
    }

    restructureForItemGrouping(itemGroups: Record<string, Card[]>) {
        for (const cards of Object.values(itemGroups)) {
            let cardArea: CardArea | undefined

            for (const card of cards) {
                if (card.parent instanceof CardAreaOffset && this.playedRow1.findCard(card)) {
                    cardArea = card.parent
                } else {
                    this.playedRow2.removeCard(card)
                    this.playedRow1.removeCard(card)
                }
            }

            if (!cardArea) {
                cardArea = new CardAreaOffset(150)
                this.playedRow1.addCardArea(cardArea)
            }

            for (const card of cards) {
                if (card.parent !== cardArea) {
                    cardArea.addCard(card)
                }
            }
        }
    }
}
