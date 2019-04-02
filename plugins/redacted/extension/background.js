import {RedactedHelper} from './redacted';

class RedactedBackgroundHelper extends RedactedHelper {
    init() {
        this.hookTorrentStatuses();
    }
}

new RedactedBackgroundHelper().init();
