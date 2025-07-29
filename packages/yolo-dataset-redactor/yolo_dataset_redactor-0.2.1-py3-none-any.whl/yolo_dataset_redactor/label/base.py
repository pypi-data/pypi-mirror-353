import abc


class LabelWorker(abc.ABC):
    @abc.abstractmethod
    def replace_class(self, class_from: int, class_to: int):
        """
        class_from: int >= 0 - class to be replaced
        class_to: int >= 0 - class to replace

        replace class in files
        """

    @abc.abstractmethod
    def delete_class(self, class_for_delete: int):
        """
        class_for_delete: int >= 0 - class to be removed

        replace class in files
        """