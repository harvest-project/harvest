import {APIHelper} from 'home/assets/api/APIHelper';

export const TorrentsAPI = new class {
    async getRealms() {
        return await APIHelper.get('/api/torrents/realms');
    }

    async getAlcazarClientConfig() {
        return await APIHelper.get('/api/torrents/alcazar-client/config');
    }

    async saveAlcazarClientConfig(base_url, token) {
        return await APIHelper.put('/api/torrents/alcazar-client/config', {
            jsonBody: {base_url, token},
        });
    }

    async testAlcazarConnection() {
        return await APIHelper.post('/api/torrents/alcazar-client/connection-test');
    }

    async getAlcazarConfig() {
        return await APIHelper.get('/api/torrents/alcazar/config');
    }

    async saveAlcazarConfig(config) {
        return await APIHelper.put('/api/torrents/alcazar/config', {
            jsonBody: config,
        });
    }

    async getAlcazarClients() {
        return await APIHelper.get('/api/torrents/alcazar/clients');
    }

    async addAlcazarClient(realm, instanceType) {
        return await APIHelper.post('/api/torrents/alcazar/clients', {
            jsonBody: {
                realm: realm,
                instance_type: instanceType,
            },
        });
    }

    async getTorrents() {
        return await APIHelper.get('/api/torrents/');
    }

    async deleteTorrentById(torrentId) {
        return await APIHelper.delete('/api/torrents/by-id/' + torrentId);
    }
};
