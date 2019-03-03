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
