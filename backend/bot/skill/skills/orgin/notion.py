# coding=utf-8
# author: Lan_zhijiang
# description: skill: notion_helper
# date: 2021/12/7

from backend.bot.maintain.notion.notion_base import HANotionBase
import json


class HASkillNotion:

    def __init__(self, ba, text, nlu_result):

        self.log = ba.log
        self.setting = ba.setting
        self.tts = ba.tts
        self.stt = ba.stt
        self.recorder = ba.recorder
        self.player = ba.player
        self.nlu = ba.nlu
        self.conversation = ba.conversation

        self.text = text
        self.nlu_result = nlu_result
        self.intent = nlu_result[1]
        self.slot = nlu_result[3]

        self.notion_base = HANotionBase(ba)
        self.notion_cache = json.load(open("./backend/data/json/notion/cache.json", "r", encoding="utf-8"))

    def start(self, intent=None):

        """
        启动技能
        :param intent
        :return:
        """
        if intent is None:
            intent = self.intent
        self.log.add_log("HASkillNotion: start search handle_func, intent-%s" % intent, 1)
        intent_mapping_list = {
            "book_meeting": self.book_meeting,
            "cancel_meeting": self.cancel_meeting,
            "edit_meeting": self.edit_meeting,
            "add_message": self.add_message,
            "discard_message": self.discard_message,
            "edit_message": self.edit_message,
            "review_message": self.review_message,
            "add_task": self.add_task,
            "delete_task": self.delete_task,
            "edit_task": self.edit_task,
            "add_project": self.add_project
        }

        try:
            intent_mapping_list[intent]()
            return True
        except KeyError:
            self.log.add_log("HASkillNotion: intent-%s was not supported!" % intent, 3)
            # self.player.play("./backend/data/audio/skill_intent_not_found.wav")
            self.tts.start("抱歉，技能无法处理意图：%s, 无对应的处理函数。请联系管理员" % intent)
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

    def book_meeting(self, boot_way="normal"):

        """
        预定会议
        :param boot_way: 启动方式 normal/func
        STEPS:
            1.fetch the meeting arrangement
            2.ask for basic meeting info
              name place participation time host
            3.verify the info
                is the info correct
                is the info conflict
            4.try to update the meeting arrangement database
            5.report the update status->success then continue
            6.ask for release announcement(message) or not
              if true: call up self.add_message
        :return:
        """
        if boot_way == "normal":
            self.log.add_log("HASkillNotion: start intent_handler-book_meeting", 1)
            # 1.fetch the meeting arrangement
            # try cache's database_id list
            database_id = "977d17d7-d8b7-453d-bd98-9f5b222b2d6e"
            try:
                meeting_arrangement = self.notion_base.query_database(database_id)["results"]
            except KeyError:
                self.log.add_log("HASkillNotion: meeting arrangement is empty, database error", 3)
                self.tts.start("数据库出现错误，请联系管理员")

            # 2.ask for basic meeting info(name place participation time host)
            meeting_info_list = {}
            keys = ["meeting_name", "date", "place", "attender"]
            keys_asking = ["请问会议名称是什么？", "请问你想在什么时候举办会议？", "请问你想在哪里举行会议？", "请问参会人员有？"]
            for i in range(0, len(keys)):
                key = keys[i]
                try:
                    meeting_info_list[key] = self.slot[key]
                except KeyError:
                    ask_slot_result = self.nlu.ask_slots([(key,  "$%s" % key, keys_asking[i])])
                    try:
                        meeting_info_list[key] = ask_slot_result[key]
                    except KeyError:
                        self.log.add_log("HASkillNotion: ask for %s fail, can't get the slot, skip" % key, 2)
                        continue


    def add_message(self):

        """
        留言
        :return:
        """

