import * as THREE from "three";

import { Text } from "troika-three-text";
import type Action from "../data/action";
import Card from "../data/card";
import CardObject from "./card";
import ChoiceOption from "./choice-option";
import ObjectBase from "./object";

export default class ChoiceDialog extends ObjectBase {
    card: Card

    promptText: Text
    background: THREE.Mesh<THREE.BoxGeometry, THREE.MeshBasicMaterial, THREE.Object3DEventMap>
    choiceMap: Record<string, ChoiceOption>

    prompt?: string
    choices?: Action[]
    choiceMeshes?: THREE.Mesh<THREE.BoxGeometry, THREE.MeshBasicMaterial, THREE.Object3DEventMap>[]

    constructor(card: Card) {
        super()

        this.card = card

        this.translateX(-CardObject.dimension.x / 2).translateZ(100).rotateZ(Math.PI / 2).rotateX(Math.PI / 2)
        this.visible = false

        const backgroundGeometry = new THREE.BoxGeometry(CardObject.dimension.y, 110, 2)
        const backgroundMaterial = new THREE.MeshBasicMaterial({ color: 0x888888 })
        this.background = new THREE.Mesh(backgroundGeometry, backgroundMaterial)
        this.background.position.set(0, 0, -10)
        this.add(this.background)

        this.promptText = new Text()
        this.promptText.text = ""
        this.promptText.fontSize = 24;
        this.promptText.anchorX = 'center'
        this.promptText.anchorY = 'middle'
        this.promptText.sync()
        this.promptText.position.add(new THREE.Vector3(0, 0, 10))
        this.add(this.promptText)

        this.choiceMap = {}
    }

    update() {
        super.update()

        if (this.choices && this.choices.length > 1 && this.prompt && this.prompt !== this.promptText.text) {
            console.log(`Show choice dialog for card '${this.card.name}'`)

            const backgroundPadding = 40
            const backgroundTitleHeight = 100
            const choiceOptionPadding = 10

            this.background.geometry.dispose()
            this.background.geometry = new THREE.BoxGeometry(
                CardObject.dimension.y,
                this.choices.length * (ChoiceOption.height + choiceOptionPadding)
                + backgroundPadding + backgroundTitleHeight,
                2
            )

            this.background.position.set(
                0,
                ((this.choices.length + 1) * (ChoiceOption.height + choiceOptionPadding)) / 2
                - ((this.choices.length + 1) * choiceOptionPadding) / 2
                + backgroundPadding / 2 + backgroundTitleHeight / 2,
                0
            )

            this.promptText.text = this.prompt!
            this.promptText.position.y = (this.choices.length + 1) * (ChoiceOption.height + choiceOptionPadding)
            this.promptText.sync()

            this.choiceMeshes = []

            this.choices.forEach((choice, index) => {
                let dialogChoice = this.choiceMap[choice.session_object_id]

                if (!dialogChoice) {
                    dialogChoice = new ChoiceOption(choice)

                    this.choiceMap[choice.session_object_id] = dialogChoice
                }

                dialogChoice.position.set(0, (this.choices!.length - index) * 110, 0)
                this.add(dialogChoice)

                this.choiceMeshes!.push(dialogChoice.mesh)
            })

            this.visible = true
        }

        else if ((!this.choices || this.choices.length < 2) && this.choiceMeshes) {
            console.log(`Hide choice dialog for card '${this.card.name}'`)

            Object.values(this.choiceMeshes).forEach((dialogMesh) => {
                this.remove(dialogMesh.parent!)
            })

            this.choiceMeshes = undefined

            this.promptText.text = ""
            this.promptText.sync()

            this.visible = false
        }
    }
}