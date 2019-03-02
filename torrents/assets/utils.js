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
