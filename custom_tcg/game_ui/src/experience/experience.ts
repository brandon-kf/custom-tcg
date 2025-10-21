
import * as THREE from "three";
import type { OrbitControls } from "three/examples/jsm/Addons.js";
import type Engine from "../engine";
import ConnectionEvent from "../event/def/connection";
import type { Event } from "../event/event";
import type EventQueue from "../event/event-queue";

export default class Experience {
    loaded: boolean
    engine?: Engine
    scene?: THREE.Scene
    camera?: THREE.PerspectiveCamera
    orbitControls?: OrbitControls
    spotLight?: THREE.SpotLight
    ambientLight?: THREE.AmbientLight
    eventQueue?: EventQueue

    constructor() {
        this.loaded = false
    }

    hasLoaded(): this is Experience & {
        scene: THREE.Scene,
        camera: THREE.PerspectiveCamera,
        orbitControls: OrbitControls,
        spotLight: THREE.SpotLight,
        ambientLight: THREE.AmbientLight
    } {
        return this.loaded
    }

    load() {
        if (!this.hasEngine())
            throw new Error("Cannot load an experience without a reference to the engine.")

        this.loaded = true
    }

    update() {
        this.checkEvents()
    }

    hasEngine(): this is Experience & {
        engine: Engine,
        scene: THREE.Scene,
        camera: THREE.PerspectiveCamera,
        orbitControls: OrbitControls,
        spotLight: THREE.SpotLight,
        ambientLight: THREE.AmbientLight,
        eventQueue: EventQueue
    } {
        return typeof (this.engine) !== "undefined"
    }

    setEngine(engine: Engine) {
        this.engine = engine
        this.scene = this.engine.scene
        this.camera = this.engine.camera
        this.orbitControls = this.engine.orbitControls
        this.spotLight = this.engine.spotLight
        this.ambientLight = this.engine.ambientLight
        this.eventQueue = this.engine.eventQueue
    }

    checkEvents(): Event[] {
        if (!this.hasEngine()) {
            throw new Error("Cannot check events if not connected to engine.")
        }

        const eventsFound: Event[] = []

        // Check connection event.
        const connection = new ConnectionEvent()

        if (this.eventQueue.next(connection, true)) {
            console.log("Event queue connected.")
            eventsFound.push(connection)
        }

        return eventsFound
    }
}