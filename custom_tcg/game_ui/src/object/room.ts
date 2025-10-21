import * as THREE from "three";

import ObjectBase from "./object";

export default class Room extends ObjectBase {
    meshes: THREE.Mesh<THREE.BoxGeometry, THREE.MeshStandardMaterial, THREE.Object3DEventMap>[]

    constructor() {
        super()

        this.meshes = []

        const xWallGeometry = new THREE.BoxGeometry(10, 200000, 200000);
        const yWallGeometry = new THREE.BoxGeometry(200000, 10, 200000);
        const zWallGeometry = new THREE.BoxGeometry(200000, 200000, 10);
        const wallMaterial = new THREE.MeshStandardMaterial({ color: 0xdddddd });

        const xWall1 = new THREE.Mesh(xWallGeometry, wallMaterial)
        const xWall2 = new THREE.Mesh(xWallGeometry, wallMaterial)
        const yWall1 = new THREE.Mesh(yWallGeometry, wallMaterial)
        const yWall2 = new THREE.Mesh(yWallGeometry, wallMaterial)
        const zWall1 = new THREE.Mesh(zWallGeometry, wallMaterial)
        const zWall2 = new THREE.Mesh(zWallGeometry, wallMaterial)

        xWall1.position.set(-100000, 0, 0)
        xWall2.position.set(100000, 0, 0)
        yWall1.position.set(0, -100000, 0)
        yWall2.position.set(0, 100000, 0)
        zWall1.position.set(0, 0, -100000)
        zWall2.position.set(0, 0, 100000)

        this.meshes.push(xWall1, xWall2, yWall1, yWall2, zWall1, zWall2)
    }

    setup() {
        this.add(...this.meshes)
    }

    update() { }
}