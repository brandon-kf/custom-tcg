import { Text } from "troika-three-text";
import type CardData from "../data/card";
import ObjectBase from "./object";

import * as THREE from "three";
import ChoiceDialog from "./choice-dialog";

export default class Card extends ObjectBase {
    static readonly dimension = new THREE.Vector3(400, 600, 2)

    cardData: CardData

    cardboard: THREE.Mesh<THREE.BoxGeometry, THREE.MeshBasicMaterial, THREE.Object3DEventMap>
    indicator: THREE.Mesh<THREE.BoxGeometry, THREE.MeshBasicMaterial, THREE.Object3DEventMap>
    nameText: Text

    isActivated: boolean
    choiceDialog: ChoiceDialog

    constructor(cardData: CardData) {
        super()

        this.cardData = cardData

        const cardboardGeometry = new THREE.BoxGeometry(Card.dimension.x, Card.dimension.y, Card.dimension.z)
        const cardboardMaterial = new THREE.MeshBasicMaterial({ color: 0x999999 })
        this.cardboard = new THREE.Mesh(cardboardGeometry, cardboardMaterial)
        this.add(this.cardboard)

        const indicatorGeometry = new THREE.BoxGeometry(20, 20, 20)
        const indicatorMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 })
        this.indicator = new THREE.Mesh(indicatorGeometry, indicatorMaterial)
        this.indicator.visible = false
        this.add(this.indicator)

        this.nameText = new Text()
        this.nameText.text = this.cardData.name
        this.nameText.fontSize = 28;
        this.nameText.anchorX = 'left'
        this.nameText.anchorY = 'top'
        this.nameText.sync()
        this.nameText.position.add(
            new THREE.Vector3(20 - Card.dimension.x / 2, Card.dimension.y / 2 - 20, 10)
        )
        this.add(this.nameText)

        this.choiceDialog = new ChoiceDialog(cardData)
        this.add(this.choiceDialog)

        this.rotateY(Math.PI)

        this.isActivated = false
    }

    update() {
        super.update()

        let activated_effect: boolean = false

        this.cardData.effects.forEach((effect) => {
            if (effect.name == "Activated") {
                activated_effect = true
            }
        })

        if (activated_effect && !this.isActivated) {
            console.log(`Update activated state for card '${this.cardData.name}'`)
            this.isActivated = true
            this.rotateZ(-Math.PI / 2)
        }
        else if (!activated_effect && this.isActivated) {
            console.log(`Update activated state for card '${this.cardData.name}'`)
            this.isActivated = false
            this.rotateZ(Math.PI / 2)
        }

        this.indicator.visible = !!this.cardData.choices && this.cardData.choices.length == 1

        this.choiceDialog.prompt = this.cardData.prompt
        this.choiceDialog.choices = this.cardData.choices
        this.choiceDialog.update()
    }

    isProcess(): boolean {
        return this.cardData.types.indexOf("Process") !== -1
    }

    isBeing(): boolean {
        return this.cardData.types.indexOf("Being") !== -1
    }

    isItem(): boolean {
        return this.cardData.types.indexOf("Item") !== -1
    }

    isHolding(): string[] {
        return this.cardData.effects.filter((v) => v.type == "Holding").map((v) => v.held_id!)
    }

    isHeld(): string | undefined {
        const heldEffect = this.cardData.effects.find((v) => v.type == "Held")

        return heldEffect?.holding_id
    }
}