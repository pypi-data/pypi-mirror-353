import os


class FileFinder:
    def __init__(self, suffixes: list[str]):
        self.__suffixes = suffixes

    def __is_true_suffix(self, file_name):
        file_name_in_list = file_name.split(".")
        suffix = file_name_in_list[len(file_name_in_list) - 1]
        return suffix in self.__suffixes

    def get_all_files_with_true_suffixes(self, path: str) -> list[str]:
        all_file_names = os.listdir(path)
        files = [i for i in all_file_names if self.__is_true_suffix(i)]
        return files
