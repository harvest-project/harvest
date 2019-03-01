import {APIHelper} from 'home/assets/api/APIHelper';

export const TrackersAPI = new class {
    async getTrackers() {
        return await APIHelper.get('/api/trackers/');
    }
};
