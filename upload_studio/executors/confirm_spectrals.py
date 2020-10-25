from upload_studio.step_executor import StepExecutor


class ConfirmSpectralsExecutor(StepExecutor):
    name = 'confirm_spectrals'
    description = 'Ask for confirmation on the spectral files.'

    def __init__(self, *args, spectrals_confirmed=None, **kwargs):
        super().__init__(*args, **kwargs)

        self.spectrals_confirmed = spectrals_confirmed

    def record_additional_metadata(self):
        self.metadata.processing_steps.append('Confirmed spectral images manually.')

    def handle_run(self):
        # Copy just the spectrals for viewing
        self.copy_prev_step_area_files('spectrals')

        if self.spectrals_confirmed is None:
            self.raise_error('Spectrals are unconfirmed.')
        elif self.spectrals_confirmed is False:
            self.raise_error('Spectrals are rejected.')

        # Spectrals were already copied, copy everything else
        self.copy_prev_step_files(('spectrals',))
        self.record_additional_metadata()
