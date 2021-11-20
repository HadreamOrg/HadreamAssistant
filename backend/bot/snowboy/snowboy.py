# coding=utf-8
# author: Lan_zhijiang
# description: snowboy engine
# date: 2020/10/3

import backend.bot.snowboy.snowboydecoder


class HASnowboy:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

    def run(self, callback):

        """
        启动snowboy
        :param callback: 回调函数
        :return:
        """
        detector = snowboy.snowboydecoder.HotwordDetector(
            self.setting["snowboySettings"]["hotword"],
            sensitivity=self.setting["snowboySettings"]["sensitivity"],
            audio_gain=1)
        detector.start(callback)

# awaken()
