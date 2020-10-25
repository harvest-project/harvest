import {observable} from 'mobx';
import {TorrentsAPI} from 'torrents/assets/TorrentsAPI';
import {TrackersAPI} from 'trackers/assets/TrackersAPI';

export const HarvestStore = new class HarvestStore {
    /******** Model State ********/

    @observable user = null;
    @observable realms = null;
    @observable trackers = null;
    @observable downloadLocations = null;
    @observable pluginStores = {};

    async fetchInitial() {
        this.realms = await TorrentsAPI.getRealms();
        this.trackers = await TrackersAPI.getTrackers();
        this.downloadLocations = await TorrentsAPI.getDownloadLocations();
    }

    getTrackerByName(name) {
        return this.trackers.find(t => t.name === name) || null;
    }

    getRealmById(realmId) {
        return this.realms.find(r => r.id === realmId) || null;
    }

    getRealmByName(realmId) {
        return this.realms.find(r => r.name === realmId) || null;
    }

    getDownloadLocationsForRealm(realmId) {
        return this.downloadLocations.filter(l => l.realm === realmId);
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

    registerPluginStore(pluginName, store) {
        this.pluginStores[pluginName] = store;
    }
};
