from yolo_dataset_redactor.label.base import LabelWorker


class Labels(LabelWorker):
    def __init__(self, label_path: str):
        self.__label_path = label_path

    def delete_class(self, class_for_delete: int):
        pass

    def replace_class(self, class_from: int, class_to: int):
        pass