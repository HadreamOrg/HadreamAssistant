# coding=utf-8
# author: Lan_zhijiang
# description: 键盘唤醒
# date: 2023/06/27

import sys
from lib.exceptions import RequireLostFatal
from lib.log import HALog
from lib.settings import Settings


log = HALog("KeyboardAwakenEngine")
setting = Settings.get_json_setting("awaken_engine")["keyboard"]


def run_in_process(pipe):

    """
    键盘按键唤醒
    :callback: 回调函数
    :return:
    """
    log.add_log("现在启动...", 1)

    while True:
        # keyboard.wait(setting["key"])
        # time.sleep(5)
        # input(">")

        # if input() == '=':
        if sys.stdin.readline() == '\n':
            print("read")
            # log.add_log("Enter被按下, 通过键盘唤醒唤醒系统", 1)
            pipe[1].send("KeyboardAwakenEngine")
        
        # 在完成对话之前，不能够再被唤醒
        if pipe[0].recv() == "start_conversation":
            if pipe[0].recv() == "end_conversation":
                pass


def run_in_thread(callback):

    log.add_log("现在启动...", 1)
    for line in sys.stdin:
        if (line == '\n'):
            callback()
