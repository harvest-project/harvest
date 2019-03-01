import {APIHelper} from 'home/assets/api/APIHelper';

export const AuthAPI = new class {
    async getUser() {
        return await APIHelper.get('/api/user');
    }

    async login(username, password) {
        return await APIHelper.post('/api/login', {
            jsonBody: {username, password},
        });
    }

    async logout(username, password) {
        return await APIHelper.post('/api/logout', {
            jsonBody: {username, password},
        });
    }
};
