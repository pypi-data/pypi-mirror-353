import abc


class ImageWorker(abc.ABC):
    @abc.abstractmethod
    def resize(self, new_size: tuple[int, int]):
        """
        new_size: (x, y) - image resize to {new_size}

        Resized images or image to new_size
        """