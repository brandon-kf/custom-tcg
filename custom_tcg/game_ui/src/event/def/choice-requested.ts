import type Choice from "../../data/choice";
import { ServerEvent } from "../event";
import type ServerEventMap from "../map/server";

export default class ChoiceRequestedEvent extends ServerEvent {
    name: keyof ServerEventMap = "choice_requested"

    choice?: Choice

    copy(other: ChoiceRequestedEvent) {
        super.copy(other)

        this.choice = other.choice
    }
}