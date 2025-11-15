import * as THREE from "three"

import type PlayerData from "../data/player"
import Card from "./card"
import CardArea from "./card-area"
import CardAreaHorizontal from "./card-area-horizontal"
import CardAreaOffset from "./card-area-offset"
import ObjectBase from "./object"

/**
 * Represents a player in the game.
 */
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

    /**
     * Creates a new Player instance.
     * @param playerData
     */
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

    /**
     * Sets up the player object.
     */
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

    /**
     * Updates the player object.
     */
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

    /**
     * Synchronizes the player's hand with the game data.
     */
    syncHand() {
        const handIds: string[] = []

        for (const cardData of this.playerData.hand) {
            const foundCard = this.hand.findCardOrArea(cardData.session_object_id)

            if (!foundCard) {
                const cardObject = new Card(cardData)

                this.hand.addCardOrArea(cardObject)
            }

            handIds.push(cardData.session_object_id)
        }

        for (const card of this.hand.findCards()) {
            if (!handIds.includes(card.cardData.session_object_id)) {
                this.hand.removeCardOrArea(card)
            }
        }
    }

    /**
     * Synchronizes the player's played cards with the game data.
     */
    syncPlayed() {
        const playedIds: string[] = []

        for (const cardData of this.playerData.played) {
            let card: Card | CardArea | undefined =
                this.playedRow1.findCard(cardData.session_object_id) ??
                this.playedRow2.findCard(cardData.session_object_id) ??
                this.playedRow3.findCard(cardData.session_object_id)
            const newCard: boolean = card === undefined

            card ??= new Card(cardData)

            if (newCard && card.isProcess()) {
                this.playedRow3.addCardOrArea(card)
            } else if (newCard && card.isBeing()) {
                this.playedRow2.addCardOrArea(card)
            } else if (newCard) {
                this.playedRow1.addCardOrArea(card)
            }

            playedIds.push(cardData.session_object_id)
        }

        for (const area of [this.playedRow1, this.playedRow2, this.playedRow3]) {
            for (const card of area.findCards()) {
                if (!playedIds.includes(card.cardData.session_object_id)) {
                    area.removeCardOrArea(card)
                }
            }
        }
    }

    /**
     * Restructures the played rows according to offset rules.
     */
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
            } else if (
                isBeing &&
                !isHolding &&
                !Object.prototype.hasOwnProperty.call(beingGroups, card.cardData.name)
            ) {
                console.log(`Restructure for being grouping includes card ${card.cardData.name}`)
                beingGroups[card.cardData.name] = [card]
            } else if (
                isBeing &&
                !isHolding &&
                Object.prototype.hasOwnProperty.call(beingGroups, card.cardData.name)
            ) {
                console.log(`Restructure for being grouping includes card ${card.cardData.name}`)
                beingGroups[card.cardData.name].push(card)
            } else if (
                isItem &&
                !isHeld &&
                !Object.prototype.hasOwnProperty.call(itemGroups, card.cardData.name)
            ) {
                console.log(`Restructure for item grouping includes card ${card.cardData.name}`)
                itemGroups[card.cardData.name] = [card]
            } else if (
                isItem &&
                !isHeld &&
                Object.prototype.hasOwnProperty.call(itemGroups, card.cardData.name)
            ) {
                console.log(`Restructure for item grouping includes card ${card.cardData.name}`)
                itemGroups[card.cardData.name].push(card)
            }
        }

        this.restructureForBeingGrouping(beingGroups)
        this.restructureForItemGrouping(itemGroups)
        this.restructureForEmptyAreas()
    }

    /**
     * Restructures the played rows for a being that is holding items.
     * @param card The being card that is holding items.
     */
    restructureForBeingHolding(card: Card) {
        let cardArea = card.parent instanceof CardAreaOffset ? card.parent : undefined
        let beingCount = 0

        if (cardArea) {
            for (const card of cardArea.findCards()) {
                if (card.isBeing()) {
                    beingCount += 1
                }
            }

            cardArea.removeCardOrArea(card)
        }

        if (!cardArea || beingCount > 1) {
            cardArea = new CardAreaOffset(150)

            this.playedRow2.removeCardOrArea(card)
            this.playedRow2.addCardOrArea(cardArea)
        }

        for (const cardId of card.isHolding()) {
            const inRow2 = this.playedRow2.findCard(cardId)
            const inRow1 = this.playedRow1.findCard(cardId)
            const held = inRow2 ?? inRow1!

            // Handle the case where this item changed hands from a different being holding area.
            if (held && inRow2 && inRow2.parent !== cardArea) {
                this.playedRow2.removeCardOrArea(inRow2)
            }

            // Handle the case where this item was in the item area.
            else if (held && inRow1) {
                this.playedRow1.removeCardOrArea(inRow1)
            }

            if (held && held.parent !== cardArea) {
                cardArea.addCardOrArea(held)
            }
        }

        cardArea.addCardOrArea(card)
    }

    /**
     * Restructures the played rows for being grouping.
     * @param beingGroups The groups of being cards to restructure.
     */
    restructureForBeingGrouping(beingGroups: Record<string, Card[]>) {
        for (const cards of Object.values(beingGroups)) {
            let cardArea: CardArea | undefined

            for (const card of cards) {
                if (card.parent instanceof CardAreaOffset && this.playedRow2.findCard(card)) {
                    cardArea = card.parent
                } else {
                    this.playedRow2.removeCardOrArea(card)
                }
            }

            if (!cardArea) {
                cardArea = new CardAreaOffset(150)
                this.playedRow2.addCardOrArea(cardArea)
            }

            for (const card of cards) {
                if (card.parent !== cardArea) {
                    cardArea.addCardOrArea(card)
                }
            }
        }
    }

    /**
     * Restructures the played rows for item grouping.
     * @param itemGroups The groups of item cards to restructure.
     */
    restructureForItemGrouping(itemGroups: Record<string, Card[]>) {
        for (const cards of Object.values(itemGroups)) {
            let cardArea: CardArea | undefined

            for (const card of cards) {
                if (card.parent instanceof CardAreaOffset && this.playedRow1.findCard(card)) {
                    cardArea = card.parent
                } else {
                    this.playedRow2.removeCardOrArea(card)
                    this.playedRow1.removeCardOrArea(card)
                }
            }

            if (!cardArea) {
                cardArea = new CardAreaOffset(150)
                this.playedRow1.addCardOrArea(cardArea)
            }

            for (const card of cards) {
                if (card.parent !== cardArea) {
                    cardArea.addCardOrArea(card)
                }
            }
        }
    }

    /**
     * Restructures the played rows to remove empty areas.
     */
    restructureForEmptyAreas() {
        for (const cardArea of [this.playedRow3, this.playedRow2, this.playedRow1]) {
            cardArea.traverse((parent, child) => {
                if (child instanceof CardAreaOffset && child.countCards() === 0) {
                    parent.removeCardOrArea(child)
                }
            })
        }
    }
}
