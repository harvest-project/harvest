import {APIHelper} from 'home/assets/api/APIHelper';

export const MonitoringAPI = new class {
    async getComponentStatuses() {
        return await APIHelper.get('/api/monitoring/component-statuses');
    }

    async getLogEntries() {
        return await APIHelper.get('/api/monitoring/log-entries');
    }
};
