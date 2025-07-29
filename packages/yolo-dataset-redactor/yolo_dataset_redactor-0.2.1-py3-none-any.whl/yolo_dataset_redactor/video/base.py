import abc


class VideoWorker(abc.ABC):
    @abc.abstractmethod
    def split(self, path_to_images: str, period: int, image_prefix: str):
        """
        path_to_images: str - path for save images
        period: int >= 0 - every {period} frames save image
        image_prefix: str - prefix for save images, examples: "png", "jpeg"

        Split video file or files to image files.
        """