import {APIHelper} from 'home/assets/api/APIHelper';

export const UploadStudioAPI = new class {
    async getProjects() {
        return await APIHelper.get('/api/upload-studio/projects');
    }

    async getProject(projectId) {
        return await APIHelper.get(`/api/upload-studio/projects/${projectId}`);
    }

    async deleteProject(projectId) {
        return await APIHelper.delete(`/api/upload-studio/projects/${projectId}`);
    }

    async postProjectResetToStep(projectId, stepIndex) {
        return await APIHelper.post(`/api/upload-studio/projects/${projectId}/reset-to-step`, {
            jsonBody: {
                step_index: stepIndex,
            },
        });
    }

    async postProjectFinish(projectId) {
        return await APIHelper.post(`/api/upload-studio/projects/${projectId}/finish`);
    }

    async postProjectRunAll(projectId) {
        return await APIHelper.post(`/api/upload-studio/projects/${projectId}/run-all`);
    }

    async postProjectRunOne(projectId) {
        return await APIHelper.post(`/api/upload-studio/projects/${projectId}/run-one`);
    }

    async postProjectInsertStep(projectId, index, executorName) {
        return await APIHelper.post(`/api/upload-studio/projects/${projectId}/insert-step`, {
            jsonBody: {
                index: index,
                executor_name: executorName,
            },
        });
    }

    async postProjectWarningAck(projectId, warningId) {
        return await APIHelper.post(`/api/upload-studio/projects/${projectId}/warnings/${warningId}/ack`);
    }

    async getProjectStepFiles(projectId, stepId) {
        return await APIHelper.get(`/api/upload-studio/projects/${projectId}/steps/${stepId}/files`);
    }

    getProjectStepFileUrl(projectId, stepId, area, fileName) {
        return `/api/upload-studio/projects/${projectId}/steps/${stepId}/files/` +
            `${encodeURIComponent(area)}/${encodeURIComponent(fileName)}`;
    }

    async patchProjectStepExecutorKwargs(projectId, stepId, executorKwargs) {
        return await APIHelper.patch(
            `/api/upload-studio/projects/${projectId}/steps/${stepId}/executor-kwargs`,
            {
                jsonBody: executorKwargs,
            },
        );
    }
};
