from upload_studio.step_executor import StepExecutor


class ManualEditExecutor(StepExecutor):
    name = 'manual_edit'

    def handle_run(self):
        if self.prev_step:
            self.copy_prev_step_files()
        self.add_warning('Execution paused for manual editing. Ack to continue.')
        self.raise_warnings()


class LAMETranscoderExecutor(StepExecutor):
    name = 'lame_transcode'

    def handle_run(self):
        self.clean_work_area()
        raise NotImplementedError()
