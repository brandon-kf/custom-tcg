import * as THREE from "three";

import ObjectBase from "./object";
import Player from "./player";

export default class Table extends ObjectBase {
    dimension: THREE.Vector3
    stretch: number
    topMesh: THREE.Mesh<THREE.BoxGeometry, THREE.MeshStandardMaterial, THREE.Object3DEventMap>

    constructor() {
        super()

        this.stretch = 0
        this.dimension = new THREE.Vector3(
            Player.dimension.x + 2 * Player.dimension.z,
            10,
            Player.dimension.x + 2 * Player.dimension.z + Player.dimension.x * this.stretch,
        )

        const tableGeometry = new THREE.BoxGeometry(this.dimension.x, this.dimension.y, this.dimension.z);
        const tableMaterial = new THREE.MeshStandardMaterial({ color: 0x4e3629 });

        this.topMesh = new THREE.Mesh(tableGeometry, tableMaterial);
        this.topMesh.receiveShadow = true
    }

    setup() {
        this.add(this.topMesh)
    }

    applyStretchForPlayerCount(playerCount: number) {
        this.stretch = Math.max(0, Math.floor((playerCount - 3) / 2))
    }

    update() {

    }
}