import type ActionContext from "../../data/action-context"
import type Choice from "../../data/choice"
import type Game from "../../data/game"
import type Player from "../../data/player"

export default interface ServerEventMap {
    event: () => void
    connection: () => void
    host_connected: (game: Game) => void
    client_connected: (game: Game) => void
    player_connected: (player: Player) => void
    game_started: (game: Game) => void
    action_executed: (actionContext: ActionContext) => void
    choice_requested: (choice: Choice) => void
}