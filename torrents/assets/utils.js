export function fileToBase64(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = function(evt) {
            const url = evt.target.result;
            resolve(url.split(',', 2)[1]);
        };
        reader.readAsDataURL(file);
    });
}

export const TorrentStatus = {
    CHECK_WAITING: 0,
    CHECKING: 1,
    DOWNLOADING: 2,
    SEEDING: 3,
    STOPPED: 4,
};

export function getTorrentStatusDisplay(torrentStatus) {
    return {
        0: 'Check Waiting',
        1: 'Checking',
        2: 'Downloading',
        3: 'Seeding',
        4: 'Stopped',
    }[torrentStatus];
}

export function shortenInfoHash(infoHash) {
    return infoHash.substring(0, 5) + '...' + infoHash.substring(35, 40);
}
