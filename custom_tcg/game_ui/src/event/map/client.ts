
export default interface ClientEventMap {
    event: (param: void) => void
    host_connect: (player_id: string) => void
    client_connect: (session_id: string, player_id: string) => void
    game_start: (session_id: string) => void
    choice_confirmed: (session_id: string, action_id: string) => void
}