import {observable} from 'mobx';

class _DataStore {
    @observable user = null;
}

class _UIStore {
    @observable numLoading = 0;

    async trackLoadingAsync(fn) {
        this.numLoading++;
        try {
            await fn();
        } finally {
            this.numLoading--;
        }
    }

    trackLoading(fn) {
        this.numLoading++;
        try {
            fn();
        } finally {
            this.numLoading--;
        }
    }
}

export const DataStore = new _DataStore();
export const UIStore = new _UIStore();
