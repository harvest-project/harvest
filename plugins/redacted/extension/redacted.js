import {PluginHelper} from 'home/extensions/common';

export const redactedMessages = {
    transcodeTorrent: 'transcodeTorrent',
    sendWhatifyMessage: 'sendWhatifyMessage',
};

export class RedactedHelper extends PluginHelper {
    static realmName = 'redacted';
    static cookieUrl = 'https://redacted.ch/';
    static cookiesEndpoint = '/api/plugins/redacted/cookies';
}
