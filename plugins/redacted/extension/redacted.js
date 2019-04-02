import {PluginHelper} from 'home/extensions/common';

export class RedactedHelper extends PluginHelper {
    static cookieUrl = 'https://redacted.ch/';
    static cookiesEndpoint = '/api/plugins/redacted/cookies';
}
