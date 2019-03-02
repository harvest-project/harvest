import {observable} from 'mobx';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {TrackersAPI} from 'trackers/assets/TrackersAPI';

class _DataStore {
    @observable user = null;
    @observable realms = null;
    @observable trackers = null;

    async fetchInitial() {
        this.realms = await TorrentsAPI.getRealms();
        this.trackers = await TrackersAPI.getTrackers();
    }
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
