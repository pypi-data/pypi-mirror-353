from io import TextIOWrapper


class FileEditor:
    def __init__(self, file_path: str):
        self.__file_path = file_path
        self.__file: TextIOWrapper | None = None
        self.__file_text = ""

    def open_file(self):
        self.__file = open(self.__file_path, "r+")

    def close_file(self):
        self.__file.close()

    def read_file(self):
        self.__file_text = self.__file.read()

    def replace_data_in_file(self, string_for_replace: str, new_string: str):
        new_text = self.__file_text.replace(string_for_replace, new_string)
        self.__file.write(new_text)
        self.__file_text = new_text
