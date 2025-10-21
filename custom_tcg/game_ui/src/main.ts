import Engine from './engine';
import Match from './experience/match';
import './style.scss';

window.engine = new Engine({ experiences: [new Match()] })

window.engine.start()
