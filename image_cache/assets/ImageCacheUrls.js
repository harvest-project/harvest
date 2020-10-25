export const ImageCacheUrls = {
    image: '/api/image-cache/image',

    getCachedImageUrl(url) {
        return ImageCacheUrls.image + '?' + new URLSearchParams({url: url}).toString();
    },
};
