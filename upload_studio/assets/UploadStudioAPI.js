import {APIHelper} from 'home/assets/api/APIHelper';

export const UploadStudioAPI = new class {
    async getProjects() {
        return await APIHelper.get('/api/upload_studio/projects');
    }

    async getProject(projectId) {
        return await APIHelper.get(`/api/upload_studio/projects/${projectId}`);
    }
};
