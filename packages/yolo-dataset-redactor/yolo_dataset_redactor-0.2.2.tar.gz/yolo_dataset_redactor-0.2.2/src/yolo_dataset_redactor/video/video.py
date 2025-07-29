import os

import cv2

from yolo_dataset_redactor.video.base import VideoWorker


class Video(VideoWorker):
    def __init__(self, video_path: str):
        self.__video_path = video_path

    def split(self, images_path: str, period: int, prefix: str = "png"):
        video = cv2.VideoCapture(self.__video_path)
        video_name = os.path.basename(self.__video_path)
        frame_checker = 0
        _, image = video.read()
        while image is not None:
            _, image = video.read()
            if frame_checker % period == 0:
                path = f"{images_path}/{video_name}_{frame_checker}.{prefix}"
                is_good, image = cv2.imencode(os.path.splitext(path)[1], image)
                if not is_good:
                    raise Exception("Could not encode image")
                image.tofile(path)
            frame_checker += 1
