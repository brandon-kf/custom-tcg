import * as THREE from "three";
import type Action from "../data/action";
import type Card from "../data/card";
import type Choice from "../data/choice";
import type Game from "../data/game";
import type Player from "../data/player";
import ActionExecutedEvent from "../event/def/action-executed";
import ChoiceConfirmedEvent from "../event/def/choice-confirmed";
import ChoiceRequestedEvent from "../event/def/choice-requested";
import ConnectionEvent from "../event/def/connection";
import GameStartEvent from "../event/def/game-start";
import GameStartedEvent from "../event/def/game-started";
import HostConnectEvent from "../event/def/host-connect";
import HostConnectedEvent from "../event/def/host-connected";
import PlayerConnectedEvent from "../event/def/player-connected";
import type { Event } from "../event/event";
import CardObject from "../object/card";
import type ChoiceDialog from "../object/choice-dialog";
import type ChoiceOption from "../object/choice-option";
import PlayerObject from "../object/player";
import Room from "../object/room";
import Table from "../object/table";
import Experience from "./experience";

export default class Match extends Experience {
    // Tools to run the experience.
    raycaster: THREE.Raycaster
    pointer: THREE.Vector2

    // State tracked from the API.
    game?: Game
    playerOrder: string[]
    self?: string
    activePlayer?: string
    choiceCardId?: string

    // 3D objects managed by the experience.
    room: Room
    table: Table
    players: Record<string, PlayerObject>

    // 3D objects tracked by the experience each update cycle.
    click: boolean
    raycastCard?: CardObject
    raycastChoice?: ChoiceOption

    constructor() {
        super()

        this.raycaster = new THREE.Raycaster()
        this.pointer = new THREE.Vector2()

        this.playerOrder = []

        this.room = new Room()
        this.table = new Table()
        this.players = {}

        this.click = false
    }

    hasInitiatedGame(): this is Match & { game: Game, self: string } {
        return !!this.game
    }

    hasStartedGame(): this is Match & { game: Game, self: string, activePlayer: string } {
        return this.hasInitiatedGame() && !!this.game.prompt
    }

    load() {
        super.load()

        if (!this.hasEngine())
            throw new Error("Cannot load this experience without a reference to the engine.")

        this.orbitControls.enableZoom = false

        this.setupLighting()

        this.room.setup()
        this.table.setup()

        this.scene.add(this.room, this.table)

        window.addEventListener("keyup", this.listenToKeyEvents.bind(this))
        window.addEventListener("mousedown", this.listenToPointerClickEvents.bind(this))
        window.addEventListener("pointermove", this.listenToPointerMoveEvents.bind(this));

        this.loaded = true
    }

    checkEvents(): Event[] {
        if (!this.hasEngine())
            throw new Error("Cannot check event queue a reference to the engine.")

        const eventLog: Event[] = super.checkEvents()

        this.checkConnectionEvents(eventLog)
        this.checkGameEvents(eventLog)

        return eventLog
    }

    update() {
        super.update() // Check events gets called here.

        if (!this.hasEngine())
            throw new Error("Cannot update this experience without a reference to the engine.")

        if (this.hasInitiatedGame() && !this.hasStartedGame() && this.createNewPlayers() > 0) {
            this.table.applyStretchForPlayerCount(this.playerOrder.length)
            this.table.update()
            this.seatPlayersAtTable()
        }

        Object.values(this.players).forEach((player) => player.update())

        if (this.hasStartedGame()) {
            this.raycast()
            this.highlightPlayableCards()
            this.highlightChoices()
        }

        if (this.hasStartedGame() && this.click && (this.raycastCard || this.raycastChoice)) {
            this.chooseAction()
        }

        if (this.hasStartedGame() && this.choiceCardId) {
            this.scene.updateMatrixWorld()
            this.moveToChoice()
        }

        this.choiceCardId = undefined
        this.raycastCard = undefined
        this.raycastChoice = undefined
        this.click = false
    }

    checkConnectionEvents(eventLog: Event[]) {
        if (!this.hasEngine())
            throw new Error("Cannot check event queue a reference to the engine.")

        if (eventLog.find((v) => v instanceof ConnectionEvent)) {
            this.eventQueue.send(new HostConnectEvent("<not in use yet>"))
            console.log("Host connect initiated.")
        }

        const hostConnectedEvent = new HostConnectedEvent()

        if (this.eventQueue.next(hostConnectedEvent, true)) {
            eventLog.push(hostConnectedEvent)

            this.game = hostConnectedEvent.game!
            this.self = this.game.players[0].session_object_id
            this.playerOrder.push(this.self)

            console.log("Host connected, new game created.")
        }

        const playerConnectedEvent = new PlayerConnectedEvent()

        if (this.eventQueue.next(playerConnectedEvent, true)) {
            eventLog.push(playerConnectedEvent)

            const newPlayer = playerConnectedEvent!.player!
            this.game!.players.push(newPlayer)
            this.playerOrder.push(newPlayer.session_object_id)

            console.log(`New player connected '${newPlayer.name}'`)
        }

        const gameStarted = new GameStartedEvent()

        if (this.eventQueue.next(gameStarted, true)) {
            eventLog.push(gameStarted)
            console.log("Game started.")

            for (const player of gameStarted.game!.players) {
                this.updatePlayer(player)
            }
        }
    }

    checkGameEvents(eventLog: Event[]) {
        if (!this.hasEngine())
            throw new Error("Cannot check event queue without a reference to the engine.")

        const actionExecuted = new ActionExecutedEvent()

        if (this.eventQueue.peek(actionExecuted)) {
            this.eventQueue.pop(actionExecuted)
            eventLog.push(actionExecuted)

            const actionData = actionExecuted.actionContext!.action
            console.log(`Action '%s' from '%s' executed.`, actionData.type, actionData.card!.name)
        }

        const choiceRequested = new ChoiceRequestedEvent()

        if (this.hasInitiatedGame() && this.eventQueue.peek(choiceRequested)) {
            this.eventQueue.pop(choiceRequested)
            eventLog.push(choiceRequested)

            const choiceData = choiceRequested!.choice!
            console.log(`Choice requested, from options ${choiceData.actions.map((a) => a.name).join(", ")}`)

            if (!this.game.prompt) {
                this.game.prompt = choiceData.prompt
                this.updatePlayer(choiceData.player, choiceData)

                if (this.hasStartedGame()) {
                    this.players[this.activePlayer].updateAll = true
                }
            }
        }
    }

    updatePlayer(playerData: Player, choiceData: Choice | undefined = undefined) {
        if (!this.hasInitiatedGame())
            throw new Error("Game hasn't started yet.")

        const gamePlayer = this.game.players.find((v) => v.session_object_id == playerData.session_object_id)!
        let choiceMap: Record<string, Action[]> | undefined

        if (choiceData) {
            choiceMap = choiceData.actions.reduce((r, i) => {
                if (!r.hasOwnProperty(i.card!.session_object_id)) {
                    r[i.card!.session_object_id] = []
                }
                r[i.card!.session_object_id].push(i)
                return r
            }, {} as Record<string, Action[]>)

            const choiceCardIds = Object.keys(choiceMap)

            if (choiceCardIds.length == 1 && choiceMap[choiceCardIds[0]].length > 1) {
                this.choiceCardId = choiceCardIds[0]
            }
        }

        this.updateCardList(gamePlayer.hand, playerData.hand, choiceMap)
        this.updateCardList(gamePlayer.played, playerData.played, choiceMap)

        this.activePlayer = gamePlayer.session_object_id
        this.setPlayerPerspective(this.activePlayer)
    }

    updateCardList(gameCards: Card[], apiCards: Card[], choiceMap: Record<string, Action[]> | undefined) {
        if (!this.hasInitiatedGame())
            throw new Error("Game hasn't started yet.")

        const apiIds: string[] = []

        for (const card of apiCards) {
            let gameCard = gameCards.find((v) => v.session_object_id == card.session_object_id)

            if (gameCard) {
                gameCard.effects = [...card.effects]
            }
            else {
                gameCard = card
                gameCards.push(card)
            }

            apiIds.push(gameCard.session_object_id)

            if (choiceMap && choiceMap.hasOwnProperty(gameCard.session_object_id)) {
                gameCard.prompt = this.game.prompt
                gameCard.choices = choiceMap[gameCard.session_object_id]
            }
        }

        for (let i = 0; i < gameCards.length; i++) {
            if (!apiIds.includes(gameCards[i].session_object_id)) {
                gameCards.splice(i, 1)
                i -= 1
            }
        }
    }

    createNewPlayers(): number {
        if (!this.hasEngine())
            throw new Error("Cannot create player objects without a reference to the engine.")

        if (!this.hasInitiatedGame())
            throw new Error("Game hasn't started yet.")

        const registeredPlayers = Object.keys(this.players)
        let newPlayers = 0

        for (const player of this.game.players) {
            if (!registeredPlayers.includes(player.session_object_id)) {
                const newPlayerObject = new PlayerObject(player)

                newPlayerObject.setup()
                this.scene.add(newPlayerObject)
                this.players[player.session_object_id] = newPlayerObject
                newPlayers += 1
            }
        }

        if (this.playerOrder.length == 1) {
            this.setPlayerPerspective(this.self!)
        }

        if (this.playerOrder.length == 2 && newPlayers > 0) {
            this.eventQueue.send(new GameStartEvent(this.game!.session_id))
        }

        return newPlayers
    }

    seatPlayersAtTable() {
        if (!this.hasInitiatedGame())
            throw new Error("Game hasn't started yet.")

        const nPlayers = this.playerOrder.length

        let directOpposingObserved = false

        this.playerOrder.forEach((playerId, index) => {
            const player = this.players[playerId]
            player.position.set(0, 0, 0)
            player.rotation.set(0, 0, 0)

            if (index == 0) {
                player.translateZ(this.table.dimension.z / 2).rotateY(Math.PI);
            }
            else if (Math.abs(index - nPlayers / 2) < 0.01) {
                directOpposingObserved = true;
                player.translateZ(-this.table.dimension.z / 2)
            }
            else if (index < nPlayers / 2) {
                const playerOffset = this.table.stretch + 1 - index;
                player
                    .translateX(-this.table.dimension.x / 2)
                    .translateZ(
                        (PlayerObject.dimension.x + 2 * PlayerObject.dimension.z) / 2
                        + playerOffset * PlayerObject.dimension.x - this.table.dimension.z / 2
                    )
                    .rotateY(Math.PI / 2)
            }
            else if (index > nPlayers / 2) {
                const playerOffset = index - this.table.stretch - 2 - (directOpposingObserved ? 1 : 0);
                player
                    .translateX(this.table.dimension.x / 2)
                    .translateZ(
                        (PlayerObject.dimension.x + 2 * PlayerObject.dimension.z) / 2
                        + playerOffset * PlayerObject.dimension.x - this.table.dimension.z / 2
                    )
                    .rotateY(-Math.PI / 2)
            }
        })
    }

    raycast() {
        if (!this.hasEngine())
            throw new Error("Cannot cast rays to playable cards without engine-provided camera.")

        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const player = this.players[this.activePlayer]
        this.raycaster.setFromCamera(this.pointer, this.camera)

        const cardMeshes: THREE.Mesh[] = []
        const choiceMeshes: THREE.Mesh[] = []

        Array.from(player.hand.findCards()).reduce(
            (r, i) => { r.push(i.cardboard); return r; },
            cardMeshes,
        )

        for (const card of player.playedRow1.findCards()) {
            if (card.indicator.visible)
                cardMeshes.push(card.cardboard)

            if (card.choiceDialog.choiceMeshes) {
                choiceMeshes.push(...card.choiceDialog.choiceMeshes)
            }
        }

        for (const card of player.playedRow2.findCards()) {
            if (card.indicator.visible)
                cardMeshes.push(card.cardboard)

            if (card.choiceDialog.choiceMeshes) {
                choiceMeshes.push(...card.choiceDialog.choiceMeshes)
            }
        }

        for (const card of player.playedRow3.findCards()) {
            if (card.indicator.visible)
                cardMeshes.push(card.cardboard)

            if (card.choiceDialog.choiceMeshes) {
                choiceMeshes.push(...card.choiceDialog.choiceMeshes)
            }
        }

        const cardIntersections = this.raycaster.intersectObjects(cardMeshes, false)

        if (cardIntersections.length > 0) {
            this.raycastCard = cardIntersections[0].object.parent as CardObject
        }

        const choiceIntersections = this.raycaster.intersectObjects(choiceMeshes, false)

        if (choiceIntersections.length > 0) {
            this.raycastChoice = choiceIntersections[0].object.parent as ChoiceOption
        }
    }

    highlightPlayableCards() {
        if (!this.hasEngine())
            throw new Error("Cannot cast rays to playable cards without engine-provided camera.")

        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const player = this.players[this.activePlayer]

        for (const cardArea of [player.hand, player.playedRow1, player.playedRow2, player.playedRow3]) {
            for (const card of cardArea.findCards()) {
                card.cardboard.material.color.setHex(0x999999)
            }
        }

        if (this.raycastCard) {
            this.raycastCard.cardboard.material.color.setHex(0x888888)
        }
    }

    highlightChoices() {
        if (!this.hasEngine())
            throw new Error("Cannot cast rays to playable cards without engine-provided camera.")

        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const player = this.players[this.activePlayer]

        for (const cardArea of [player.hand, player.playedRow1, player.playedRow2, player.playedRow3]) {
            for (const card of cardArea.findCards()) {
                if (card.choiceDialog.choiceMeshes) {
                    for (const choiceMesh of card.choiceDialog.choiceMeshes) {
                        choiceMesh.material.color.setHex(0x999999)
                    }
                }
            }
        }

        if (this.raycastChoice) {
            this.raycastChoice.mesh.material.color.setHex(0x888888)
        }
    }

    chooseAction() {
        if (!this.hasEngine())
            throw new Error("Cannot cast rays to playable cards without engine-provided camera.")

        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        let chosenAction: Action | undefined = undefined

        if (this.raycastCard && this.raycastCard.cardData.choices && this.click) {
            chosenAction = this.raycastCard.cardData.choices[0]
        }

        if (this.raycastChoice && this.click) {
            chosenAction = this.raycastChoice.action
            this.setPlayerPerspective(this.activePlayer)
        }

        if (chosenAction) {
            this.eventQueue.send(new ChoiceConfirmedEvent(this.game!.session_id, chosenAction.session_object_id))

            this.game.prompt = undefined

            for (const player of this.game.players) {
                for (const card of [...player.hand, ...player.played]) {
                    if (card.prompt) {
                        card.prompt = undefined
                        card.choices = []
                    }
                }
            }
        }

        if (this.raycastChoice && this.click) {
            (this.raycastChoice.parent! as ChoiceDialog).update()
        }
    }

    setPlayerPerspective(playerId: string) {
        if (!this.hasEngine())
            throw new Error(
                "Cannot set player perspective to match camera without a reference to the engine."
            )

        if (!this.hasInitiatedGame())
            throw new Error("Game hasn't started yet.")

        const player = this.players[playerId]

        this.orbitControls.reset()

        this.camera.position.copy(player.position)
        this.camera.position.add(new THREE.Vector3(0, 3000, 0))

        const cameraRotation = new THREE.Quaternion()
        player.getWorldQuaternion(cameraRotation)
        const newTarget = (
            new THREE.Vector3(0, -100, 100)
                .applyQuaternion(cameraRotation)
                .add(this.camera.position)
        )
        this.orbitControls.target.copy(newTarget)

        this.orbitControls.enableRotate = true

        this.orbitControls.update()

        if (this.activePlayer)
            this.players[this.activePlayer].positionBlock.visible = true
        player.positionBlock.visible = false

        this.activePlayer = playerId
    }

    moveLeft() {
        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const currentPlayerIndex = this.playerOrder.indexOf(
            this.activePlayer
        )
        const nextPlayer = this.playerOrder[
            this.mod(currentPlayerIndex + 1, this.playerOrder.length)
        ]

        this.setPlayerPerspective(nextPlayer)
    }

    moveRight() {
        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const currentPlayerIndex = this.playerOrder.indexOf(this.activePlayer)
        const nextPlayer = this.playerOrder[this.mod(currentPlayerIndex - 1, this.playerOrder.length)]

        this.setPlayerPerspective(nextPlayer)
    }

    moveOver() {
        if (!this.hasEngine())
            throw new Error("Cannot set player perspective to match camera without a reference to the engine.")

        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const player = this.players[this.activePlayer]

        this.orbitControls.reset()

        this.camera.position.copy(player.position)
        const elevatedTranslation = player.localToWorld(new THREE.Vector3(0, 2600, 11000))
        this.camera.position.add(elevatedTranslation)

        const playerRotation = new THREE.Quaternion()
        player.getWorldQuaternion(playerRotation)
        const newTarget = new THREE.Vector3(0, -200, 5).applyQuaternion(playerRotation).add(this.camera.position)
        this.orbitControls.target.copy(newTarget)

        this.orbitControls.enableRotate = false

        this.orbitControls.update()
    }

    moveBack() {
        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        this.setPlayerPerspective(this.activePlayer)
    }

    moveToChoice() {
        if (!this.hasEngine())
            throw new Error("Cannot set player perspective to match camera without a reference to the engine.")

        if (!this.hasStartedGame())
            throw new Error("Game hasn't started yet.")

        const player = this.players[this.activePlayer]

        const choiceCard = (
            player.hand.findCard(this.choiceCardId!)
            || player.playedRow1.findCard(this.choiceCardId!)
            || player.playedRow2.findCard(this.choiceCardId!)
            || player.playedRow3.findCard(this.choiceCardId!)!
        )

        this.orbitControls.reset()

        const cardRotation = new THREE.Quaternion()
        choiceCard.getWorldQuaternion(cardRotation)

        const cardWorldPosition = new THREE.Vector3()
        choiceCard.getWorldPosition(cardWorldPosition)

        const backedAwayTranslation = new THREE.Vector3(800, 0, 200).applyQuaternion(cardRotation)
        const targetCameraPosition = cardWorldPosition.clone().add(backedAwayTranslation)

        const newCameraTarget = new THREE.Vector3(-100, 0, 0).applyQuaternion(cardRotation).add(targetCameraPosition.clone())

        this.camera.position.copy(targetCameraPosition.clone())
        this.orbitControls.target.copy(newCameraTarget.clone())

        this.orbitControls.enableRotate = true

        this.orbitControls.update()
    }

    setupLighting() {
        if (!this.hasEngine())
            throw new Error("Lighting depends on the instance provided by the engine.")

        this.spotLight.castShadow = true
        this.spotLight.position.set(0, 10000, 0);
        this.spotLight.target.position.set(0, 0, 0);
    }

    listenToPointerMoveEvents(event: MouseEvent) {
        this.pointer.x = (event.clientX / window.innerWidth) * 2 - 1
        this.pointer.y = -(event.clientY / window.innerHeight) * 2 + 1
    }

    listenToPointerClickEvents(event: MouseEvent) {
        this.listenToPointerMoveEvents(event)
        this.click = true
    }

    listenToKeyEvents(event: KeyboardEvent) {
        let keyCode = event.code;

        if (keyCode == "ArrowLeft" || keyCode == "KeyA") {
            // Left
            this.moveLeft()
        }

        else if (keyCode == "ArrowRight" || keyCode == "KeyD") {
            // Right
            this.moveRight()
        }

        else if (keyCode == "ArrowUp" || keyCode == "KeyW") {
            this.moveOver()
        }

        else if (keyCode == "ArrowDown" || keyCode == "KeyS") {
            this.moveBack()
        }
    }

    mod(n: number, m: number): number {
        // This is needed since JS has a dumb implementation for negatives.
        return ((n % m) + m) % m;
    }
}