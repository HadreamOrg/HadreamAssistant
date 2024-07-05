# coding=utf-8
# author: Lan_zhijiang
# description: Log class. include RunningLog OrderLog
# date: 2022/10/16

from copy import deepcopy
import datetime
import threading
import time
import os
import queue

from lib.settings import Settings

log_setting = Settings.get_json_setting("log")
log_level_list = ["DEBUG", "INFO", "WARNING", "ERROR", "FATAL"]
print_log_level_list = [
    "DEBUG", "INFO", "\033WARNING\033", "\031ERROR\031", "\035FATAL\035"
]


def reload_log_setting():

    Settings.reload_json_setting("log")


def get_date():

    return str(datetime.date.today())


def get_formatted_time(format_string=None):

    if format_string is None:
        format_string = "%H:%M:%S"
    return time.strftime(format_string)


class RunningLog:
    """ 运行log记录 """
    log_queue = queue.Queue()

    @classmethod
    def get_log_file_path(cls):

        """
        获取log文件路径
        :return:
        """
        basic_path = log_setting["logPath"]
        log_file_name = "%s.log" % get_date()
        if os.path.exists(basic_path + log_file_name) is False:
            create_log_file = open(basic_path + log_file_name, "w")
            create_log_file.close()
        return "%s%s" % (basic_path, log_file_name)

    @classmethod
    def get_formatted_log(cls, log_func, content_fstr, fnum=1):

        def wrapped_formatted_log(*args, logger="undefined", **kwargs):

            fargs = list(args)
            for v in list(kwargs.values()):
                fargs.append(v)
            log_func(content_fstr % tuple(fargs[0:fnum]), logger)

        return wrapped_formatted_log

    @classmethod
    def add_log(cls, content, level=1, logger="undefined", is_print=False, **sth):

        """
        添加log
            先添加到队列里面，超过一定数量再写入
            大于等于等级3的log会被同步写入
        :param logger: 记录者名称
        :param level: log级别  0: DEBUG 1: INFO 2: WARNING 3: EXCEPTION(当前任务可能停止) 4: FATAL: 主线程退出
        :param content: log内容
        :param is_print: 是否打印(为False时优先级高于设置)
        :return:
        """
        log_after_half = "%s %s: %s" % (get_formatted_time(), logger, content)

        if is_print or log_setting["isDebug"]:
            print("[%s] %s" % (print_log_level_list[level], log_after_half))
        else:
            if level >= log_setting["displayLevel"]:
                print("[%s] %s" % (print_log_level_list[level], log_after_half))

        cls.log_queue.put("[%s] %s" % (log_level_list[level], log_after_half))
        if cls.log_queue.qsize() >= log_setting["writeThreshold"]:
            cls.start_write_log_thread()
            return

        if level >= 3:
            cls.start_write_log_thread()
            return

    @classmethod
    def start_write_log_thread(cls):

        """
        启动写入守护线程
        :return:
        """
        write_thread = threading.Thread(target=cls.write_log, args=())
        write_thread.start()

    @classmethod
    def write_log(cls):

        log_file = open(cls.get_log_file_path(), "a")
        for i in range(cls.log_queue.qsize()):
            try:
                log = cls.log_queue.get()
            except IndexError:
                break

            try:
                log_file.write('%s\n' % log)
            except IOError:
                print("[WARNING] %s Log:"
                      "Can't write into the log file, please check the permission or is the path correct!"
                      % get_formatted_time())
                raise IOError("file write failed")
        log_file.close()


class HALog:

    def __init__(self, logger):

        self.logger = logger

    def add_log(self, content, level, is_print=True):
        
        return RunningLog.add_log(content, level, self.logger, is_print)
