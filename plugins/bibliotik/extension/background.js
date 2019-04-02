import {BibliotikHelper} from './bibliotik';

class BibliotikBackgroundHelper extends BibliotikHelper {
    init() {
        this.hookCookieSync(cookie => cookie.name === 'id' && cookie.domain === '.bibliotik.me');
    }
}

new BibliotikBackgroundHelper().init();
