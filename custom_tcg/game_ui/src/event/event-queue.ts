import { Event } from "./event"

export default class EventQueue {
    queue: Event[]

    constructor() {
        this.queue = []
    }

    send(e: Event) { }

    peek(e: Event): boolean {
        let found = false

        if (this.queue.length > 0 && this.queue[0].name == e.name) {
            found = true
            e.copy(this.queue[0])
        }

        return found
    }

    pop(e: Event): boolean {
        let found = false

        if (this.queue.length > 0 && this.queue[0].name == e.name) {
            found = true
            const popped = this.queue.shift()
            e.copy(popped!)
        }

        return found
    }

    next(e: Event, remove: boolean): boolean {
        let found = false

        for (let i = 0; i < this.queue.length && !found; i++) {
            found = this.queue[i].name == e.name

            if (found) {
                e.copy(this.queue[i])
            }

            if (found && remove) {
                this.queue.splice(i, 1)
            }
        }

        return found
    }
}