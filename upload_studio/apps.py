from django.apps import AppConfig

from torrents import signals
from upload_studio.executor_registry import ExecutorRegistry


class UploadStudioConfig(AppConfig):
    name = 'upload_studio'

    def ready(self):
        from .executors import manual_edit, lame_transcode, create_torrent_file, finish_upload
        ExecutorRegistry.register_executor(manual_edit.ManualEditExecutor)
        ExecutorRegistry.register_executor(lame_transcode.LAMETranscoderExecutor)
        ExecutorRegistry.register_executor(create_torrent_file.CreateTorrentFileExecutor)
        ExecutorRegistry.register_executor(finish_upload.FinishUploadExecutor)

        from .receivers import on_torrent_finished
        signals.torrent_finished.connect(on_torrent_finished)
