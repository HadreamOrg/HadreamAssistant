# coding=utf-8
# settings.python_script
# author: Lan_zhijiang
# mail: lanzhijiang@foxmail.com
# date: 2022/12/16
# description: manage the settings include json/python_script format

import json


json_setting_path_basic = "./data/settings/json"
json_setting_path_skill = "./data/skill_config"
json_setting_path = {
    "overall": "%s/overall_setting.json" % json_setting_path_basic,
    "log": "%s/log_setting.json" % json_setting_path_basic,
    "awaken_engine": "%s/awaken_engine_setting.json" % json_setting_path_basic,
    "input": "%s/input_setting.json" % json_setting_path_basic,
    "output": "%s/output_setting.json" % json_setting_path_basic,
    "process": "%s/process_setting.json" % json_setting_path_basic,
    "turing": "%s/turing_setting.json" % json_setting_path_skill,
    "db_pre": "%s/db_pre_setting.json" % json_setting_path_basic
}

py_setting_path_basic = "data.settings.python_script"
py_setting_path = {
    "skill_table": "%s.skill_table" % py_setting_path_basic
}

file_path = {
    "white_remote": r"./data/json/white_remote_list.json"
}


class Settings:

    files = {}
    json_settings = {}
    py_settings = {}

    @classmethod
    def get_json_setting(cls, setting_id):
        try:
            return cls.json_settings[setting_id]
        except KeyError:
            return cls.load_json_setting(setting_id)

    @classmethod
    def get_py_setting(cls, setting_id):
        try:
            return cls.py_settings[setting_id]
        except KeyError:
            return cls.load_py_setting(setting_id)

    @classmethod
    def load_all_settings(cls):
        for k, v in json_setting_path:
            cls.json_settings[k] = json.load(open(v, "r", encoding="utf-8"))

    @classmethod
    def load_json_setting(cls, setting_id):
        json_setting = json.load(open(json_setting_path[setting_id], "r", encoding="utf-8"))
        cls.json_settings[setting_id] = json_setting
        return json_setting

    @classmethod
    def load_py_setting(cls, setting_id):
        path = py_setting_path[setting_id]
        py_setting = __import__(path, fromlist=["setting"])  # 这里删去的.setting
        cls.py_settings[setting_id] = py_setting
        return py_setting

    @classmethod
    def reload_py_setting(cls, setting_id):
        pass

    @classmethod
    def reload_json_setting(cls, setting_id):
        cls.json_settings[setting_id] = json.load(open(json_setting_path[setting_id], "r", encoding="utf-8"))

    @classmethod
    def rewrite_json_setting(cls, setting_id):
        json.dump(open(json_setting_path[setting_id], "r", encoding="utf-8"), cls.json_settings[setting_id])

    @classmethod
    def init_json_files(cls):
        for k, v in file_path:
            cls.json_settings[k] = json.load(open(v, "r", encoding="utf-8"))

    @classmethod
    def __get_fn_and_fp(cls, fn, fp):
        if fn is not None:
            fp = file_path[fn]
        if fn is None:
            fn = fp.split("/")[-1]
        return fn, fp

    @classmethod
    def get_file(cls, fn, fp=None, ft="json"):
        try:
            return cls.files[fn]
        except KeyError:
            return cls.read_file(fn, fp, ft)

    @classmethod
    def rewrite_file(cls, data, fn=None, fp=None, ft="json"):
        fn, fp = cls.__get_fn_and_fp(fn, fp)

        file = open(fp, "w", encoding="utf-8")
        if ft == "json":
            json.dump(data, file)
        else:
            file.write(data)
        file.close()

    @classmethod
    def read_file(cls, fn=None, fp=None, ft="json"):
        fn, fp = cls.__get_fn_and_fp(fn, fp)

        file = open(fp, "r", encoding="utf-8")
        if ft == "json":
            result = cls.files[fn] = json.load(file)
        else:
            result = cls.files[fn] = file.read()
        file.close()
        return result
