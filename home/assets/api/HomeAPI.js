import {APIHelper} from 'home/assets/api/APIHelper';

export const HomeAPI = new class {
    async getDashboardData() {
        return await APIHelper.get('/api/home/dashboard-data');
    }
};
