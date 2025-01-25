import json
import os
import pickle
from datetime import datetime


# datetime无法写入json文件，用这个处理一下
from tqdm import tqdm
import subprocess


class CJsonEncoder(json.JSONEncoder):
    def default(self, obj):
        # convert the ISO8601 string to a datetime object
        converted = datetime.datetime.strptime(obj.value, "%Y%m%dT%H:%M:%S")
        if isinstance(converted, datetime.datetime):
            return converted.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(converted, datetime.date):
            return converted.strftime("%Y-%m-%d")
        else:
            return json.JSONEncoder.default(self, converted)


class FileUtil:
    @staticmethod
    def load_json(filepath):
        """
        从文件中取数据
        :param filepath:
        :return:
        """
        with open(filepath, 'r') as load_f:
            data_list = json.load(load_f)
        return data_list

    @staticmethod
    def dump_json(filepath, data_list):
        with open(filepath, 'w') as f:
            json.dump(data_list, f)

    @staticmethod
    def load_pickle(filepath):
        """
        load 从数据文件中读取数据（object）
        :param filepath:
        :return:
        """
        with open(filepath, 'rb') as f:
            data = pickle.load(f)
        return data

    @staticmethod
    def dump_pickle(filepath, data):
        """
        dump 将数据（object）写入文件
        :param filepath:
        :param data:
        :return:
        """
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)

    @staticmethod
    def load_txt(filepath):
        with open(filepath) as f:
            lines = f.readlines()
        return lines

    @staticmethod
    def dump_txt(filepath, items):

        with open(filepath, 'w') as f:
            f.write(items)

    @staticmethod
    def dump_list_to_txt(filepath, items):
        """
        write items (list) into filepath (txt file): one item a line
        Args:
            filepath (): .txt file
            items (): list [, , , ...]

        Returns: write list into txt file: one item a line

        """
        with open(filepath, 'w') as tfile:
            tfile.write('\n'.join(items))

    @staticmethod
    def get_file_names_in_directory(directory, file_type="*"):
        """
        get '.file_type' file_names (paths) in directory
        @param directory: the path of directory
        @type directory: Path("", "", "")
        @param file_type: file type, such as ftl, html, xhtml
        @type file_type: string
        @return: file_names
        @rtype: [string, string, ...]
        """
        file_names = []
        for file_name in directory.glob(f"*.{file_type}"):
            file_names.append(str(file_name))
        return file_names

    @staticmethod
    def create_directory_if_not_exists(base_path, dir_name, with_current_time=True):
        current_time = None
        if with_current_time:
            current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            dir_name = f"{dir_name}_{current_time}"
        dir_path = os.path.join(base_path, dir_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        if with_current_time:
            return dir_path, current_time
        else:
            return dir_path
        # print(f"Directory created: {dir_path}")
        # else:
        #     print(f"Directory already exists: {dir_path}")

    @staticmethod
    def merge_files_under_directory(diretory_filepath, file_type='json'):
        filenames = FileUtil.get_file_names_in_directory(diretory_filepath, file_type)
        filenames = sorted(filenames, key=lambda x: (len(x), x))
        all_data_list = []
        for filename in tqdm(filenames, ascii=True):
            one_data = FileUtil.load_json(filename)
            all_data_list.extend(one_data)
        return all_data_list

    @staticmethod
    def find_files_by_extension(directory, extension):
        matching_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(f".{extension}"):
                    matching_files.append(os.path.join(root, file))
        return matching_files

    @staticmethod
    def open_pdf(file_path):
        """
        Opens a PDF file with the system's default viewer on macOS.

        Parameters:
        file_path (str): The path to the PDF file.
        """
        subprocess.run(['open', file_path])