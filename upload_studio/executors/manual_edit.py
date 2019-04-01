from upload_studio.step_executor import StepExecutor


class ManualEditExecutor(StepExecutor):
    name = 'manual_edit'
    description = 'Manually edit files / metadata.'

    def handle_run(self):
        if self.prev_step:
            self.copy_prev_step_files()
        self.add_warning('Execution paused for manual editing. Ack to continue.')
        self.raise_warnings()
