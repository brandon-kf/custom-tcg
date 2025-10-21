import * as THREE from "three";

import { Text } from "troika-three-text";
import type Action from "../data/action";
import Card from "./card";
import ObjectBase from "./object";

export default class ChoiceOption extends ObjectBase {
    static height: number = 100
    action: Action
    mesh: THREE.Mesh<THREE.BoxGeometry, THREE.MeshBasicMaterial, THREE.Object3DEventMap>

    constructor(action: Action) {
        super()

        this.action = action

        const choiceGeometry = new THREE.BoxGeometry(Card.dimension.y - 40, ChoiceOption.height, Card.dimension.z)
        const choiceMaterial = new THREE.MeshBasicMaterial({ color: 0x999999 })
        this.mesh = new THREE.Mesh(choiceGeometry, choiceMaterial)
        choiceMaterial.depthTest = false
        this.add(this.mesh)

        const choiceText = new Text()
        choiceText.text = this.action.name
        choiceText.fontSize = 24;
        choiceText.anchorX = 'center'
        choiceText.anchorY = 'middle'
        choiceText.sync()
        choiceText.position.add(new THREE.Vector3(0, 0, 10))
        this.add(choiceText)
    }
}