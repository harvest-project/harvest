export const ImageCacheAPI = {
    getCachedImageUrl(url) {
        return '/api/image-cache/image?' + new URLSearchParams({url: url}).toString();
    },
};
