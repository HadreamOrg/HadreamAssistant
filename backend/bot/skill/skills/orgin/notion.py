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
            ["message", self.message],
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
        # self.book_meeting()

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
        self.log.add_log("HASkillNotion: start intent_handler-book_meeting", 1)
        self.tts.start("好的，请说一下会议名称和参会人信息")
        self.player.start_recording()
        self.recorder.record()
        self.player.stop_recording()
        self.tts.start("主持人已经默认设置为你，李佩瑜同学。会议已预约")
        # self.tts.start("很遗憾，本周四晚的党员活动室已经被文体部的李佩瑜同学预定了，要召开名为合唱比赛的会议。是否要对他留言请求交换呢？")
        # self.player.start_recording()
        # self.recorder.record()
        # self.player.stop_recording()
        # self.tts.start("好的~不用谢，有需要再叫我哦~")

    def message(self):

        """
        留言
        :return:
        """

