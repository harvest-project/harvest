export class StepSettingsRegistry {
    static components = {};

    static register(executorName, settingsHandler) {
        this.components[executorName] = settingsHandler;
    }
}
