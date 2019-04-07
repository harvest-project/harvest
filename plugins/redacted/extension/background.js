import {RedactedHelper, redactedMessages} from './redacted';
import {hookChromeMessage} from 'home/extensions/common';

class RedactedBackgroundHelper extends RedactedHelper {
    async onTranscodeTorrent(request) {
        return await this.performPOST('/api/plugins/redacted-uploader/transcode', {
            body: JSON.stringify({
                tracker_id: request.trackerId,
                transcode_type: request.transcodeType,
            }),
        });
    }

    init() {
        this.hookTorrents();
        hookChromeMessage(redactedMessages.transcodeTorrent, this.onTranscodeTorrent.bind(this));
    }
}

new RedactedBackgroundHelper().init();
