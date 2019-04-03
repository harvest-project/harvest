import {PluginHelper} from 'home/extensions/common';

export const redactedMessages = {
    transcodeTorrent: 'transcodeTorrent',
};

export class RedactedHelper extends PluginHelper {
    static cookieUrl = 'https://redacted.ch/';
    static cookiesEndpoint = '/api/plugins/redacted/cookies';
}
