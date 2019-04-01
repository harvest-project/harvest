import {APIHelper} from 'home/assets/api/APIHelper';

export const UploadStudioAPI = new class {
    async getProjects() {
        return await APIHelper.get('/api/upload_studio/projects');
    }

    async getProject(projectId) {
        return await APIHelper.get(`/api/upload_studio/projects/${projectId}`);
    }

    async deleteProject(projectId) {
        return await APIHelper.delete(`/api/upload_studio/projects/${projectId}`);
    }

    async postProjectResetToStep(projectId, step) {
        return await APIHelper.post(`/api/upload_studio/projects/${projectId}/reset-to-step`, {
            jsonBody: {step},
        });
    }

    async postProjectRunAll(projectId, step) {
        return await APIHelper.post(`/api/upload_studio/projects/${projectId}/run-all`);
    }

    async postProjectRunOne(projectId, step) {
        return await APIHelper.post(`/api/upload_studio/projects/${projectId}/run-one`);
    }

    async postProjectWarningAck(projectId, warningId) {
        return await APIHelper.post(`/api/upload_studio/projects/${projectId}/warnings/${warningId}/ack`);
    }
};
