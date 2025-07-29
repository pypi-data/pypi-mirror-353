import os

from yolo_dataset_redactor.base import FileFinder
from yolo_dataset_redactor.image.base import ImageWorker
from yolo_dataset_redactor.image.image import Image


class Images(ImageWorker):
    def __init__(self, image_path: str, suffixes: list[str]):
        self.__file_finder = FileFinder(suffixes)
        self.__image_path = image_path

    def resize(self, new_size: tuple[int, int]):
        files = self.__file_finder.get_all_files_with_true_suffixes(self.__image_path)
        for image_name in files:
            image = Image(os.path.join(self.__image_path, image_name))
            image.resize(new_size)
