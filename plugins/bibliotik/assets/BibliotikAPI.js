import {APIHelper} from 'home/assets/api/APIHelper';

export const BibliotikAPI = new class {
    async getConfig() {
        return await APIHelper.get('/api/plugins/bibliotik/config');
    }

    async saveConfig(username, password, isServerSideLoginEnabled) {
        return await APIHelper.put('/api/plugins/bibliotik/config', {
            jsonBody: {
                username,
                password,
                is_server_side_login_enabled: isServerSideLoginEnabled,
            },
        });
    }

    async testConnection() {
        return await APIHelper.post('/api/plugins/bibliotik/connection-test');
    }

    async clearLoginData() {
        return await APIHelper.post('/api/plugins/bibliotik/clear-login-data');
    }
};
