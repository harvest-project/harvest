import 'noty/lib/noty.css';
import 'noty/lib/themes/mint.css';

import {messages, NotyHelper} from 'home/extensions/common';
import {BibliotikHelper} from './bibliotik';

class BibliotikLoginHelper extends BibliotikHelper {
    handleResponse(response) {
        console.log('Get response from background script: ' + response.type);
        if (response.type === messages.loginSucceeded) {
            NotyHelper.success('Login successful, please wait...');
            window.location.reload();
        } else if (response.type === messages.loginDisabled) {
            NotyHelper.info('Harvest login is disabled from options.');
        } else if (response.type === messages.loginFailed) {
            NotyHelper.error(`Unable to login using Harvest: ${response.detail}.`);
        }
    }

    init() {
        if (document.title === 'Bibliotik / Login') {
            console.log('Detected login page. Requesting login from background script...');
            NotyHelper.info('Trying Harvest login, please hold...');
            chrome.runtime.sendMessage(
                {type: messages.requestLogin},
                response => this.handleResponse(response),
            );
        }
    }
}

new BibliotikLoginHelper().init();
