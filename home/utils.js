import prettysize from 'prettysize';

export function formatDateTimeString(dateTimeString) {
    return new Intl.DateTimeFormat(undefined, {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
    }).format(new Date(dateTimeString));
}

export function formatBytes(bytes) {
    return prettysize(bytes, {places: 2});
}

// The static fields are hoisted and due to a bug, the context shows up in the HOC. This works around it.
// https://github.com/facebook/react/issues/14061#issuecomment-435443838
export function clearContextType(cls) {
    delete cls.contextType;
    return cls;
}

export function capitalizeWord(word) {
    return word.substring(0, 1).toUpperCase() + word.substring(1).toLowerCase();
}

export function toJSONPretty(data) {
    return JSON.stringify(data, null, 4);
}
