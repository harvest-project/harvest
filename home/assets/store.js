import {observable} from 'mobx';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {TrackersAPI} from 'trackers/assets/TrackersAPI';

export const HarvestStore = new class HarvestStore {
    /******** Model State ********/

    @observable user = null;
    @observable realms = null;
    @observable trackers = null;
    @observable downloadLocations = null;

    async fetchInitial() {
        this.realms = await TorrentsAPI.getRealms();
        this.trackers = await TrackersAPI.getTrackers();
        this.downloadLocations = await TorrentsAPI.getDownloadLocations();
    }

    getTrackerForRealm(realmName) {
        for (const tracker of this.trackers) {
            if (tracker.name === realmName) {
                return tracker;
            }
        }
        return null;
    }

    /******** UI State ********/

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
};
