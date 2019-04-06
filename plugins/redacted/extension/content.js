import $ from 'jquery';
import 'noty/lib/noty.css';
import 'noty/lib/themes/mint.css';

import {RedactedHelper, redactedMessages} from './redacted';
import {messages, NotyHelper, sendChromeMessage} from 'home/extensions/common';

const loadingImg = '<img src="data:image/gif;base64,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" width="12" height="12" valign="middle" />';
const linkRegexps = [
    /torrents\.php\?action=download&id=(\d+)/,
    /torrents\.php\?.*torrentid=(\d+)/,
];

function getTorrentId(link) {
    for (const regex of linkRegexps) {
        const m = link.match(regex);
        if (m !== null) {
            return m[1];
        }
    }
}

class TorrentRow {
    static TRACKER_NAME = 'redacted';

    static STATUS_NOT_DOWNLOADED = 0;
    static STATUS_DOWNLOADING = 1;
    static STATUS_DOWNLOADED = 2;
    static STATUS_WORKING = 3;

    constructor(helper, elem) {
        this.helper = helper;
        this.jq = $(elem);
        const link = this.jq.find('a:contains(\'DL\')');
        if (!link.length) return;
        this.actions = $('<span>').css('float', 'none');
        link.parent()
            .before(
                $('<span>')
                    .css('float', 'right')
                    .css('margin-left', '4px')
                    .append(' [ ')
                    .append(this.actions)
                    .append(' ]'),
            );
        this.torrentId = getTorrentId(link.attr('href'));
        this.status = null;
        this.torrent = null;
        this.statusUpdated();
    }

    setItems(items) {
        let needsSeparator = false;
        this.actions.empty();
        for (const item of items) {
            if (needsSeparator) {
                this.actions.append(' | ');
            } else {
                needsSeparator = true;
            }
            this.actions.append(item);
        }
    }

    async addTorrent() {
        this.status = this.constructor.STATUS_WORKING;
        this.statusUpdated();
        try {
            const resp = await sendChromeMessage({
                type: messages.addTorrent,
                trackerName: this.helper.constructor.TRACKER_NAME,
                trackerId: this.torrentId,
                downloadPath: null,
            });
            NotyHelper.success(`Added torrent ${this.torrentId} - ${resp.torrent_info.metadata.group.name}`);
        } catch (exception) {
            console.log('Error downloading torrent', exception);
            NotyHelper.error(`Error adding torrent: ${exception}`);
        }
        this.status = null;
        this.statusUpdated();

        await this.helper.refreshStatuses();
    }

    async _transcodeTorrent() {
        try {
            const existingProjects = await sendChromeMessage({
                type: messages.getUploadStudioProjects,
                queryParams: {source_tracker_id: this.torrentId},
            });
            if (existingProjects.active.length || existingProjects.history.length) {
                if (!confirm('There is already an upload project from this torrent. Continue?')) {
                    return;
                }
            }
            await sendChromeMessage({
                type: redactedMessages.transcodeTorrent,
                trackerId: this.torrentId,
            });
            NotyHelper.success(`Sent torrent ${this.torrentId} for transcoding.`);
        } catch (exception) {
            console.log('Error transcoding torrent', exception);
            NotyHelper.error(`Error transcoding torrent: ${exception}`);
        }
    }

    async transcodeTorrent() {
        this.status = this.constructor.STATUS_WORKING;
        this.statusUpdated();

        await this._transcodeTorrent();

        this.status = null;
        this.statusUpdated();
        await this.helper.refreshStatuses();
    }

    async downloadTorrent() {
        const response = await sendChromeMessage({
            type: messages.getDownloadTorrentUrl,
            trackerId: this.torrent.id,
        });
        window.location = response.downloadUrl;
    }

    statusUpdated() {
        const items = [];
        if (this.status === null || this.status === this.constructor.STATUS_WORKING) {
            items.push(loadingImg);
        } else {
            if (this.status === this.constructor.STATUS_NOT_DOWNLOADED) {
                items.push($('<a href="#">GET</a>').click(e => {
                    e.preventDefault();
                    this.addTorrent();
                }));
            } else if (this.status === this.constructor.STATUS_DOWNLOADING) {
                items.push(Math.floor(this.torrent.progress * 100) + '%');
            } else if (this.status === this.constructor.STATUS_DOWNLOADED) {
                items.push($('<a href="#">ZIP</a>').click(e => {
                    e.preventDefault();
                    this.downloadTorrent();
                }));
            }
            items.push($('<a href="#">TC</a>').click(e => {
                e.preventDefault();
                this.transcodeTorrent();
            }));
        }
        this.setItems(items);
    }

    receiveTorrent(torrent) {
        const changedProgress = this.torrent && this.torrent.progress !== torrent.progress;
        this.torrent = torrent;
        if (this.status === this.constructor.STATUS_WORKING) {
            return;
        }

        let status = null;
        if (torrent && torrent.progress === 1) {
            status = this.constructor.STATUS_DOWNLOADED;
        } else if (torrent) {
            status = this.constructor.STATUS_DOWNLOADING;
        } else {
            status = this.constructor.STATUS_NOT_DOWNLOADED;
        }
        if (changedProgress || status !== this.status) {
            this.status = status;
            this.statusUpdated();
        }
    }
}

class RedactedContentHelper extends RedactedHelper {
    static TRACKER_NAME = 'redacted';

    init() {
        const rowsArray = $('tr:has(span.torrent_action_buttons), tr:has(span.torrent_links_block)').toArray();
        rowsArray.splice(1000); // Max number of rows to process
        this.rows = rowsArray.map(r => new TorrentRow(this, r));

        if (this.rows.length) {
            const runAndSchedule = async () => {
                try {
                    await this.refreshStatuses();
                } catch (exception) {
                    console.log('Error refreshing statuses', exception);
                }

                // 3s for up to 60 torrents, linear increase afterwards
                const timeout = Math.max(3000, this.rows.length * 60);
                setTimeout(() => runAndSchedule(), timeout);
            };
            setTimeout(() => runAndSchedule(), 50);
        }
    }

    async refreshStatuses() {
        try {
            const response = await sendChromeMessage({
                type: messages.getTorrentStatuses,
                realmName: this.constructor.TRACKER_NAME,
                torrentIds: this.rows.map(r => r.torrentId),
            });
            const responses = {};
            for (const torrent of response.torrents.results) {
                responses[torrent.torrent_info.tracker_id] = torrent;
            }
            for (const row of this.rows) {
                row.receiveTorrent(responses[row.torrentId]);
            }
        } catch (exception) {
            NotyHelper.error(`Failed getting Harvest torrent statuses: ${exception}`);
        }
    }
}

const contentHelper = new RedactedContentHelper();
contentHelper.init();
