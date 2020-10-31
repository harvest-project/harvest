const blankValue = '–'; // n dash character

export function formatDateTimeStringHuman(dateTimeString) {
    if (!dateTimeString) {
        return blankValue;
    }
    return new Intl.DateTimeFormat('en', {
        year: 'numeric',
        month: 'numeric',
        day: 'numeric',
        hour: 'numeric',
        minute: 'numeric',
        second: 'numeric',
    }).format(new Date(dateTimeString));
}

export function formatDateStringHuman(dateTimeString) {
    if (!dateTimeString) {
        return blankValue;
    }
    return new Intl.DateTimeFormat('en', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    }).format(new Date(dateTimeString));
}

export function formatDateTimeStringISO(dateTimeString) {
    if (!dateTimeString) {
        return blankValue;
    }
    const parts = new Intl.DateTimeFormat('en', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false,
    }).formatToParts(new Date(dateTimeString));
    const keys = {};
    for (const {type, value} of parts) {
        keys[type] = value;
    }
    return `${keys.year}-${keys.month}-${keys.day} ${keys.hour}:${keys.minute}:${keys.second}`;
}

const bytesSuffixes = ['B', 'KB', 'MB', 'GB', 'TB', 'PB'];

export function formatBytes(bytes) {
    if (bytes < 1000) {
        return Math.round(bytes) + ' B';
    }

    let suffix = 0;
    while (bytes >= 1000) {
        suffix++;
        bytes /= 1000;
    }
    let decimals;
    if (bytes < 10) {
        decimals = 2;
    } else if (bytes < 100) {
        decimals = 1;
    } else {
        decimals = 0;
    }
    return `${bytes.toFixed(decimals)} ${bytesSuffixes[suffix]}`;
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

export class HarvestEvent {
    constructor() {
        this.callbacks = [];
    }

    subscribe(fn) {
        this.callbacks.push(fn);
    }

    unsubscribe(fn) {
        const index = this.callbacks.indexOf(fn);
        if (index === -1) {
            return false;
        }
        this.callbacks.splice(index, 1);
        return true;
    }

    fire(...args) {
        for (const fn of this.callbacks) {
            fn(...args);
        }
    }
}
