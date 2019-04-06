import 'noty/lib/noty.css';
import 'noty/lib/themes/mint.css';

import {messages, NotyHelper, sendChromeMessage} from 'home/extensions/common';
import {BibliotikHelper} from './bibliotik';

class BibliotikLoginHelper extends BibliotikHelper {
    async handleLoginPage() {
        NotyHelper.info('Contacting Harvest for login data...');
        try {
            await sendChromeMessage({type: messages.requestLogin});
            NotyHelper.success('Login successful, please wait...');
            window.location.reload();
        } catch (response) {
            console.error('Got response from background script: ' + JSON.stringify(response));
            if (response.detail === 'disabled') {
                NotyHelper.info('Harvest login is disabled from options.');
            } else {
                NotyHelper.error(`Unable to login using Harvest: ${response.detail}.`);
            }
        }
    }

    init() {
        if (document.title === 'Bibliotik / Login') {
            console.log('Detected login page. Requesting login from background script...');
            this.handleLoginPage();
        }
    }
}

new BibliotikLoginHelper().init();
