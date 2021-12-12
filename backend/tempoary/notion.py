# coding=utf-8
# author: Lan_zhijiang
# description: skill: notion_helper
# date: 2021/12/7

import json
import requests


class HASkillNotion:

    def __init__(self, ba, text, nlu_result):

        self.log = ba.log
        self.setting = ba.setting
        self.tts = ba.tts
        self.stt = ba.stt
        self.recorder = ba.recorder
        self.player = ba.player

        self.text = text
        self.nlu_result = nlu_result
        self.intent = nlu_result[1]
        self.slot = nlu_result[3]

    def start(self):

        """
        启动技能
        :return:
        """
        self.log.add_log("HASkillNotion: start search handle_func, intent-%s" % self.intent, 1)
        intent_mapping_list = [
            ["book_meeting", self.book_meeting],
            ["message", self.message]
        ]
        intent_found = False
        for intent_func in intent_mapping_list:
            if intent_func[0] == self.intent:
                intent_found = True
                intent_func[1]()

        if not intent_found:
            self.log.add_log("HASkillNotion: intent-%s was not found!" % self.intent, 3)
            self.player.play("./backend/data/audio/skill_intent_not_found.wav")
            return False

    def launch(self):

        """
        欢迎(默认意图)
        :return:
        """

    def book_meeting(self):

        """
        预定会议
        :return:
        """

    def message(self):

        """
        留言
        :return:
        """

