import {APIHelper} from 'home/assets/api/APIHelper';

export const SettingsAPI = new class {
    async getToken() {
        return await APIHelper.get('/api/settings/token');
    }

    async generateToken() {
        return await APIHelper.post('/api/settings/token');
    }
};
