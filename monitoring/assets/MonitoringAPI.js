import {APIHelper} from 'home/assets/api/APIHelper';

export const MonitoringAPI = new class {
    async getMonitoringData() {
        return await APIHelper.get('/api/monitoring/data');
    }
};
