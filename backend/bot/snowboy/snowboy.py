# coding=utf-8
# author: Lan_zhijiang
# description: snowboy engine
# date: 2021/11/20

from backend.bot.snowboy import snowboydecoder


class HASnowboy:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.snowboy_setting = ba.setting["bot"]["snowboy"]

    def run(self, callback):

        """
        启动snowboy
        :param callback: 回调函数
        :return:
        """
        self.log.add_log("HASnowboy: snowboy is now running...", 1)
        detector = snowboydecoder.HotwordDetector(self.snowboy_setting["hotword"],
                                                  sensitivity=self.snowboy_setting["sensitivity"])

        detector.start(
            detected_callback=callback,
            sleep_time=0.03)
        # detector.start(callback)

        # detector.terminate()


# awaken()
