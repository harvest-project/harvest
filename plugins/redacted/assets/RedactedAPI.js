import {APIHelper} from 'home/assets/api/APIHelper';

export const RedactedAPI = new class {
    async getConfig() {
        return await APIHelper.get('/api/plugins/redacted/config');
    }

    async saveConfig(apiKey, announceUrl) {
        return await APIHelper.put('/api/plugins/redacted/config', {
            jsonBody: {
                api_key: apiKey,
                announce_url: announceUrl,
            },
        });
    }

    async testConnection() {
        return await APIHelper.post('/api/plugins/redacted/connection-test');
    }

    async clearLoginData() {
        return await APIHelper.post('/api/plugins/redacted/clear-login-data');
    }
};
