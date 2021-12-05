# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's maintainer
# date: 2021/11/20


class HAMaintainer:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.maintainer_setting = ba.setting["bot"]["maintain"]

    def run(self):

        """
        启动
        :return:
        """
        self.log.add_log("HAMaintainer: HAMaintainer is now running...", 1)

