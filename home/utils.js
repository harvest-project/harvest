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
    return prettysize(bytes);
}

// The static fields are hoisted and due to a bug, the context shows up in the HOC. This works around it.
// https://github.com/facebook/react/issues/14061#issuecomment-435443838
export function clearContextType(cls) {
    delete cls.contextType;
    return cls;
}
