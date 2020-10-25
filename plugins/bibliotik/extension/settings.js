import $ from 'jquery';
import 'noty/lib/noty.css';
import 'noty/lib/themes/mint.css';

import {BibliotikHelper} from './bibliotik';
import 'home/extensions/settings.css';
import {NotyHelper} from 'home/extensions/common';

class BibliotikSettingsHelper extends BibliotikHelper {
    async init() {
        $('#save').click(() => this.saveOptions());
        $('#test_connection').click(() => this.testConnectionHandler());

        const {url, token, autoLogin} = await this.fetchConfig(true);
        $('#url').val(url);
        $('#token').val(token);
        $('#auto_login').prop('checked', autoLogin);
    }

    saveOptions() {
        chrome.storage.local.set({
            url: $('#url').val(),
            token: $('#token').val(),
            autoLogin: $('#auto_login').prop('checked'),
        }, function () {
            NotyHelper.success('Connection settings saved.');
        });
    }

    async testConnectionHandler() {
        NotyHelper.info('Testing connection, please wait...');
        try {
            NotyHelper.success(await this.testConnection(true));
        } catch (message) {
            NotyHelper.error(message);
        }
    }
}

new BibliotikSettingsHelper().init();
