from django.apps import AppConfig

from torrents import signals
from upload_studio.executor_registry import ExecutorRegistry


class UploadStudioConfig(AppConfig):
    name = 'upload_studio'

    def ready(self):
        from .executors import (
            manual_edit,
            lame_transcode,
            create_torrent_file,
            finish_upload,
            sox_process,
            fix_filename_track_numbers,
            strip_filename_spaces,
            rename_files_to_tags,
            generate_spectrals,
            confirm_spectrals,
            verify_audio_files_integrity,
            upload_cover_to_imgur,
            upload_spectrals_to_imgur,
            reencode_flacs,
        )
        ExecutorRegistry.register_executor(manual_edit.ManualEditExecutor)
        ExecutorRegistry.register_executor(lame_transcode.LAMETranscoderExecutor)
        ExecutorRegistry.register_executor(create_torrent_file.CreateTorrentFileExecutor)
        ExecutorRegistry.register_executor(finish_upload.FinishUploadExecutor)
        ExecutorRegistry.register_executor(sox_process.SoxProcessExecutor)
        ExecutorRegistry.register_executor(
            fix_filename_track_numbers.FixFilenameTrackNumbersExecutor)
        ExecutorRegistry.register_executor(strip_filename_spaces.StripFilenameSpacesExecutor)
        ExecutorRegistry.register_executor(rename_files_to_tags.RenameFilesToTagsExecutor)
        ExecutorRegistry.register_executor(generate_spectrals.GenerateSpectralsExecutor)
        ExecutorRegistry.register_executor(confirm_spectrals.ConfirmSpectralsExecutor)
        ExecutorRegistry.register_executor(
            verify_audio_files_integrity.VerifyAudioFilesIntegrityExecutor)
        ExecutorRegistry.register_executor(upload_cover_to_imgur.UploadCoverToImgurExecutor)
        ExecutorRegistry.register_executor(upload_spectrals_to_imgur.UploadSpectralsImgurExecutor)
        ExecutorRegistry.register_executor(reencode_flacs.ReencodeFLACsExecutor)

        from .receivers import on_torrent_finished
        signals.torrent_finished.connect(on_torrent_finished)
