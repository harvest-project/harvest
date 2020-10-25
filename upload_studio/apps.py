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
        )
        ExecutorRegistry.register_executor(manual_edit.ManualEditExecutor)
        ExecutorRegistry.register_executor(lame_transcode.LAMETranscoderExecutor)
        ExecutorRegistry.register_executor(create_torrent_file.CreateTorrentFileExecutor)
        ExecutorRegistry.register_executor(finish_upload.FinishUploadExecutor)
        ExecutorRegistry.register_executor(sox_process.SoxProcessExecutor)
        ExecutorRegistry.register_executor(fix_filename_track_numbers.FixFilenameTrackNumbers)
        ExecutorRegistry.register_executor(strip_filename_spaces.StripFilenameSpaces)
        ExecutorRegistry.register_executor(rename_files_to_tags.RenameFilesToTags)

        from .receivers import on_torrent_finished
        signals.torrent_finished.connect(on_torrent_finished)
