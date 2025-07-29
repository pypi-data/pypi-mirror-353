import glob
import json
import os
from zipfile import ZipFile

import pandas as pd


class FileUtil:
    @staticmethod
    def read_file(file_path, **kwargs):
        if file_path.endswith('.csv'):
            return FileUtil.read_csv(file_path, **kwargs)
        if file_path.endswith('.xlsx'):
            return FileUtil.read_excel(file_path, **kwargs)
        if file_path.endswith('.zip'):
            return FileUtil.parse_zip_file(file_path, **kwargs)
        if file_path.endswith('.txt'):
            with open(file_path, 'r', encoding='utf-8-sig') as file:
                content = file.read()
                if 'json' in kwargs:
                    return json.loads(content) if len(content) else {}
                return content
        raise ValueError(f"Invalid file path: {file_path}")

    @staticmethod
    def read_csv(file_path, encoding='gbk', **kwargs):
        return pd.read_csv(file_path, **{'encoding': encoding, **kwargs})

    @staticmethod
    def read_excel(file_path, engine='openpyxl', **kwargs):
        return pd.read_excel(file_path, **{'engine': engine, **kwargs})

    @staticmethod
    def parse_zip_file(file_path, **kwargs):
        dfs = []
        with ZipFile(file_path, 'r') as zip_ref:
            # 获取ZIP档案中的所有文件和目录的名称列表
            filelist = zip_ref.namelist()
            # 按需解压文件
            for filename in filelist:
                print('===========zip file: ' + filename + ' ' + file_path + '============')
                if filename.endswith('.csv'):
                    dfs.append(FileUtil.read_csv(zip_ref.open(filename), **kwargs))
                elif filename.endswith('.xlsx'):
                    dfs.append(FileUtil.read_excel(zip_ref.open(filename), **kwargs))
        return dfs

    @staticmethod
    def write_file(file_path, content):
        FileUtil.make_dirs(os.path.dirname(file_path))
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(content)

    @staticmethod
    def write_csv(file_path, data_list, df_callback=None, **kwargs):
        FileUtil.write_csv_excel(file_path, data_list, df_callback, **kwargs)

    @staticmethod
    def write_excel(file_path, data_list, df_callback=None, **kwargs):
        FileUtil.write_csv_excel(file_path, data_list, df_callback, **kwargs)

    @staticmethod
    def write_csv_excel(file_path, data_list, df_callback=None, **kwargs):
        FileUtil.make_dirs(os.path.dirname(file_path))
        df = pd.DataFrame(data_list)
        if df_callback:
            df_callback(df)
        if file_path.endswith('.csv'):
            df.to_csv(file_path, **{'index': False, **kwargs})
        elif file_path.endswith('.xlsx'):
            df.to_excel(file_path, **{'index': False, **kwargs})

    @staticmethod
    def make_dirs(path):
        if not os.path.exists(path):
            try:
                os.makedirs(path, exist_ok=True)
            except Exception as e:
                print(f"Error Creating Directory: {path}, {e}")

    @staticmethod
    def rename_file(old_name, new_name):
        _file_path = os.path.dirname(old_name)
        if not os.path.isabs(new_name):
            new_name = os.path.sep.join([_file_path, new_name])
        if not os.path.exists(old_name):
            raise FileNotFoundError(f"File Not Found: {old_name}")
        if os.path.exists(new_name):
            raise FileExistsError(f"File Already Exists: {new_name}")
        FileUtil.make_dirs(os.path.dirname(new_name))
        os.rename(old_name, new_name)
        return new_name

    @staticmethod
    def file_has_extension(file_name, extension=None):
        if extension is not None:
            return file_name.endswith(extension)
        elif '.' in file_name and len(file_name.split('.')[-1]) > 0:
            return True
        else:
            return False

    @staticmethod
    def list_files_with_pattern(file_path, pattern):
        # 构造搜索模式，'*'表示任意数量的任意字符
        search_pattern = os.path.sep.join([file_path, pattern + '*'])
        # 使用glob.glob来查找所有匹配的文件
        matching_files = glob.glob(search_pattern)
        return matching_files

    @staticmethod
    def find_file(file_path, file_name, is_pattern=False, ctime=False):
        _files_with_ctime = []
        if is_pattern:
            matching_files = FileUtil.list_files_with_pattern(file_path, file_name)
            if len(matching_files) > 0:
                # print(f"File Found: {matching_files}")
                for item in matching_files:
                    _files_with_ctime.append((item, os.path.getctime(item)))
                    # _files_with_ctime.append((os.path.sep.join([file_path, item]), os.path.getctime(item)))
                    # print(item, os.path.getctime(item))
        else:
            _file_path = os.path.sep.join([file_path, file_name])
            if os.path.exists(_file_path):
                _files_with_ctime.append((f"{_file_path}", os.path.getctime(f"{_file_path}")))

        if len(_files_with_ctime) > 0:
            sorted_files = sorted(_files_with_ctime, key=lambda x: x[1])
            _file_name = sorted_files[-1][0]
            _file_ctime = sorted_files[-1][1]

            if not ctime:
                return _file_name
            elif _file_ctime > ctime or _file_ctime + 5 > ctime:
                return _file_name
        return None
