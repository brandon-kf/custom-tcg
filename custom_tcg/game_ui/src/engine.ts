import * as THREE from "three";
import { OrbitControls } from "three/examples/jsm/Addons.js";
import type EventQueue from "./event/event-queue";
import SocketIOEventQueue from "./event/event-queue-socket-io";
import Experience from "./experience/experience";

export type Renderer = THREE.WebGLRenderer

export default class Engine {
    experiences: Experience[]
    renderer: THREE.WebGLRenderer
    scene: THREE.Scene
    camera: THREE.PerspectiveCamera
    orbitControls: OrbitControls
    spotLight: THREE.SpotLight
    ambientLight: THREE.AmbientLight
    devAxes: THREE.Group
    eventQueue: EventQueue

    experience: Experience | null

    constructor({ experiences }: { experiences?: Experience[] }) {
        this.experiences = experiences || []
        this.renderer = new THREE.WebGLRenderer()
        this.scene = new THREE.Scene()
        this.camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 200000)
        this.orbitControls = new OrbitControls(this.camera, this.renderer.domElement);
        this.spotLight = new THREE.SpotLight(0xffffff, 1200000000)
        this.ambientLight = new THREE.AmbientLight(0xffffff, 1)

        const xGeometry = new THREE.BoxGeometry(1000, 50, 50);
        const redMaterial = new THREE.MeshBasicMaterial({ color: 0xff0000 });
        const xAxis = new THREE.Mesh(xGeometry, redMaterial);
        xAxis.position.set(500, 0, 0);

        const yGeometry = new THREE.BoxGeometry(50, 1000, 50);
        const greenMaterial = new THREE.MeshBasicMaterial({ color: 0x00ff00 });
        const yAxis = new THREE.Mesh(yGeometry, greenMaterial);
        yAxis.position.set(0, 500, 0);

        const zGeometry = new THREE.BoxGeometry(50, 50, 1000);
        const blueMaterial = new THREE.MeshBasicMaterial({ color: 0x0000ff });
        const zAxis = new THREE.Mesh(zGeometry, blueMaterial);
        zAxis.position.set(0, 0, 500);

        this.devAxes = new THREE.Group();
        this.devAxes.add(xAxis, yAxis, zAxis);

        this.eventQueue = new SocketIOEventQueue()

        this.experience = null
        if (this.experiences.length > 0) {
            this.setExperience(this.experiences[0])
        }
    }

    setExperience(experience: Experience) {
        if (this.experiences.indexOf(experience) == -1) {
            this.experiences.push(experience)
        }

        this.experience = experience
    }

    hasSetExperience(): this is Engine & { experience: Experience } {
        return typeof (this.experience) !== "undefined"
    }

    getRenderer(): THREE.WebGLRenderer {
        return this.renderer
    }

    start() {
        if (this.experience === null && !this.experiences) {
            throw new Error("No experiences available.")
        }

        if (this.experience == null) {
            this.experience = this.experiences[0]
        }

        this.renderer.setSize(window.innerWidth, window.innerHeight);
        document.body.appendChild(this.renderer.domElement);

        this.renderer.setAnimationLoop(this.update.bind(this));

        this.loadExperience()
    }

    update() {
        if (!this.hasSetExperience()) {
            throw new Error("Cannot run update loop when experience hasn't been set.")
        }

        if (!this.experience.hasLoaded()) {
            // There's a chance we switched to a new one, let's try loading it first.
            this.experience.load()
        }

        if (!this.experience.hasLoaded()) {
            // Now we have cause for alarm
            throw new Error("Experience failed to load.")
        }

        this.experience.update()
        this.renderer.shadowMap.enabled = true
        this.renderer.render(this.experience.scene, this.experience.camera);
    }

    loadExperience() {
        this.scene.add(this.spotLight, this.ambientLight, this.devAxes);

        if (!this.hasSetExperience()) {
            throw new Error("Cannot load experience that hasn't been set.")
        }

        this.experience.setEngine(this)
        this.experience.load()

        if (!this.experience.hasLoaded()) {
            throw new Error("Experience failed to load.")
        }

        this.experience.orbitControls.target.set(
            this.experience.camera.position.x,
            this.experience.camera.position.y,
            this.experience.camera.position.z - 100
        )
        this.experience.orbitControls.update()
    }
}