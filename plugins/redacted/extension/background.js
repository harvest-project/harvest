import {RedactedHelper, redactedMessages} from 'plugins/redacted/extension/redacted';
import {hookChromeMessage} from 'home/extensions/common';

class RedactedBackgroundHelper extends RedactedHelper {
    postWhatifyMessage(message) {
        const {url} = this.fetchConfig();

        return new Promise((resolve, reject) => {
            chrome.tabs.query({url: `http://localhost:8000/whatify`}, tabs => {
                for (const tab of tabs) {
                    chrome.tabs.executeScript(tab.id, {
                        code: `window.postMessage(${JSON.stringify(message)}, "*");`,
                    });
                }
                resolve();
            });
        });
    }

    async onTranscodeTorrent(request) {
        return await this.performPOST('/api/plugins/redacted-uploader/transcode', {
            body: JSON.stringify({
                tracker_id: request.trackerId,
                transcode_type: request.transcodeType,
            }),
        });
    }

    async onSendWhatifyMessage(request) {
        await this.postWhatifyMessage(request.message);
        return {};
    }

    init() {
        this.hookTorrents();
        hookChromeMessage(redactedMessages.transcodeTorrent, this.onTranscodeTorrent.bind(this));
        hookChromeMessage(redactedMessages.sendWhatifyMessage, this.onSendWhatifyMessage.bind(this));
    }
}

new RedactedBackgroundHelper().init();
