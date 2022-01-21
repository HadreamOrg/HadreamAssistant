# coding=utf-8
# author: Lan_zhijiang
# description: skill: notion_helper
# date: 2021/12/7

from backend.bot.maintain.notion.notion_base import HANotionBase


class HASkillNotion:

    def __init__(self, ba, text, nlu_result):

        self.log = ba.log
        self.setting = ba.setting
        self.tts = ba.tts
        # self.stt = ba.stt
        # self.recorder = ba.recorder
        self.player = ba.player
        self.conversation = ba.conversation

        self.text = text
        self.nlu_result = nlu_result
        self.intent = nlu_result[1]
        self.slot = nlu_result[3]

        self.notion_op_base = HANotionBase(ba)

    def start(self, intent=None):

        """
        启动技能
        :param intent
        :return:
        """
        if intent is None:
            intent = self.intent
        self.log.add_log("HASkillNotion: start search handle_func, intent-%s" % intent, 1)
        intent_mapping_list = [
            ["book_meeting", self.book_meeting],
            ["cancel_meeting", self.cancel_meeting],
            ["edit_meeting", self.edit_meeting],
            ["add_message", self.add_message],
            ["discard_message", self.discard_message],
            ["edit_message", self.edit_message],
            ["review_message", self.review_message],
            ["add_task", self.add_task],
            ["delete_task", self.delete_task],
            ["edit_task", self.edit_task],
            ["add_project", self.add_project]
        ]

        intent_found = False
        for intent_func in intent_mapping_list:
            if intent_func[0] == intent:
                intent_found = True
                intent_func[1]()

        if not intent_found:
            self.log.add_log("HASkillNotion: intent-%s was not found!" % intent, 3)
            # self.player.play("./backend/data/audio/skill_intent_not_found.wav")
            self.tts.start("抱歉，技能无法解析该意图——找不到该意图-%s，请联系管理员" % intent)
            return False

    def launch(self):

        """
        欢迎(默认意图)
        介绍本技能的使用方法
        :return:
        """
        self.log.add_log("HASkillNotion: start intent_handler-launch", 1)

        # welcome
        self.tts.start("你好啊，欢迎使用由蓝之酱开发的Notion助手，你可以在这里留言、查看任务或者发布会议等等")
        self.tts.start("请问您有什么需要帮助的吗？")
        nlu_result = self.conversation.skill_conversation("notion")
        self.start(nlu_result[1])

    def book_meeting(self):

        """
        预定会议
        STEPS:
            1.get the meeting arrangement
            2.ask basic meeting info
              name place participation time host
            3.verify the info
                is the info correct
                is the info conflict
            4.try to update the meeting arrangement database
            5.report the status
            6.ask for release announcement(message) or not
        :return:
        """
        self.log.add_log("HASkillNotion: start intent_handler-book_meeting", 1)

    def add_message(self):

        """
        留言
        :return:
        """

