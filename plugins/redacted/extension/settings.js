import $ from 'jquery';
import 'noty/lib/noty.css';
import 'noty/lib/themes/mint.css';

import {RedactedHelper} from './redacted';
import 'home/extensions/settings.css';
import {NotyHelper} from 'home/extensions/common';

class RedactedSettingsHelper extends RedactedHelper {
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
            // Strip trailing slashes
            url: $('#url').val().replace(/\/$/, ''),
            token: $('#token').val(),
            autoLogin: $('#auto_login').prop('checked'),
        }, function () {
            NotyHelper.success('Connection settings saved.');
        });
    }

    async testConnectionHandler() {
        NotyHelper.info('Testing connection, please wait...');
        try {
            NotyHelper.success(await this.testConnection());
        } catch (message) {
            NotyHelper.error(message);
        }
    }
}

new RedactedSettingsHelper().init();
