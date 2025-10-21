import type Engine from "../engine";

declare global {
    interface Window {
        engine: Engine;
    }
}

export { };

