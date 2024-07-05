# coding=utf-8
# author: Lan_zhijiang
# description: snowboy engine
# date: 2021/11/20
# last_edit: 2023/06/27

from lib.snowboy import snowboydecoder
from lib.settings import Settings
from lib.log import HALog


log = HALog("SnowboyAwakenEngine")
setting = Settings.get_json_setting("awaken_engine")["snowboy"]


def get_callback(pipe):
    
    def callback():
        pipe[0].send("SnowboyAwakenEngine")
        if pipe[1].recv() == "start_conversation":
            if pipe[1].recv() == "end_conversation":
                pass

        return

    return callback


def generate_interupt_check(state: list):

    def interupt_check():
        return state[0]

    return interupt_check

def run_in_process(pipe):

    """
    启动snowboy
    :param callback: 回调函数
    :return:
    """
    log.add_log("现在启动...", 1)

    detector = snowboydecoder.HotwordDetector(
        setting["hotword"],
        sensitivity=setting["sensitivity"]
    )

    detector.start(
        detected_callback=get_callback(pipe),
        sleep_time=setting["sleepTime"],
        interrupt_check=lambda : False)

    detector.terminate()


def run_in_thread(callback, interupt_check):

    """
    启动snowboy
    :param callback: 回调函数
    :return:
    """
    log.add_log("现在启动...", 1)

    detector = snowboydecoder.HotwordDetector(
        setting["hotword"],
        sensitivity=setting["sensitivity"]
    )

    detector.start(
        detected_callback=callback,
        sleep_time=setting["sleepTime"],
        interrupt_check=interupt_check)
    

