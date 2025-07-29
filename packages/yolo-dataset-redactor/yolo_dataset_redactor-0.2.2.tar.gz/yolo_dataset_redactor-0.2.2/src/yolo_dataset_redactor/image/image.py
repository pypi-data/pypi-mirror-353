import os

import cv2
import numpy as np

from yolo_dataset_redactor.image.base import ImageWorker


class Image(ImageWorker):
    def __init__(self, image_path: str):
        self.__image_path = image_path

    def resize(self, new_size: tuple[int, int]):
        image = cv2.imdecode(np.fromfile(self.__image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
        image = cv2.resize(image, new_size)
        is_good, image = cv2.imencode(os.path.splitext(self.__image_path)[1], image)
        if not is_good:
            raise Exception("Could not encode image")
        image.tofile(self.__image_path)
