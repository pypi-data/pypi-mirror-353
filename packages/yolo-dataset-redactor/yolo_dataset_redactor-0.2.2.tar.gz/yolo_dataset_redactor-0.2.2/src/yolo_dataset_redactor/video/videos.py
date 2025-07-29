import os

from yolo_dataset_redactor.base import FileFinder
from yolo_dataset_redactor.video.base import VideoWorker
from yolo_dataset_redactor.video.video import Video


class Videos(VideoWorker):
    def __init__(self, videos_path: str, video_suffixes: list = None):
        if video_suffixes is None:
            video_suffixes = ['mp4']
        self.__video_finder = FileFinder(video_suffixes)
        self.__videos_path = videos_path

    def split(self, images_path: str, period: int, prefix: str = "png"):
        for name in self.__video_finder.get_all_files_with_true_suffixes(self.__videos_path):
            video = Video(os.path.join(self.__videos_path, name))
            video.split(images_path, period, prefix)
