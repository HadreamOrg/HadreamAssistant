# coding=utf-8
# author: Lan_zhijiang
# description: snowboy engine
# date: 2021/11/20

from backend.bot.snowboy import snowboydecoder


class HASnowboy:

    def __init__(self, ba):

        self.ba = ba
        self.setting = ba.setting

    def run(self, callback):

        """
        启动snowboy
        :param callback: 回调函数
        :return:
        """
        detector = snowboydecoder.HotwordDetector(
            self.setting["conversation"]["bot"]["snowboy"]["hotword"],
            sensitivity=self.setting["conversation"]["bot"]["snowboy"]["sensitivity"],
            audio_gain=1)
        detector.start(callback)

# awaken()
