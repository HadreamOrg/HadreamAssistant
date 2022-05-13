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
        self.tts.start("请问你有什么需要吗？")
        nlu_result = self.conversation.skill_conversation("notion")
        self.start(nlu_result[1])

    def notion_date_convert(self, raw):

        """
        将notion使用的日期格式转换为YYYY-MM-DD/HH:MM:SS
        如: 2021-12-06T20:30:00.000+08:00 => 2021-12-06/20:30:00
        注意，该转换以东八区为准，忽略时区，如果raw表达的不是东八区，就危了
        :param raw:
        :return:
        """

    def is_date_conflict(self, a, b):

        """
        判断日期是否重合
        :param a: 已经有的日期
        :param b: 要加入的日期
        :return: bool
        """
        a_start = int(a[0].replace(":", ""))
        a_end = int(a[1].replace(":", ""))
        b_start = int(b[0].replace(":", ""))

        if a_start >= b_start and b_start < a_end:
            return True
        else:
            return False

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
            database_id = "977d17d7-d8b7-453d-bd98-9f5b222b2d6e"  # or try cache's database_id list
            try:
                meeting_arrangement = self.notion_base.query_database(database_id)["results"]
            except KeyError:
                self.log.add_log("HASkillNotion: meeting arrangement is empty, database error", 3)
                self.tts.start("数据库出现错误，请联系管理员")
                return False

            meeting_info_list = {}
            meeting_info_keys = ["meeting_name", "date", "place", "attender"]
            asking = ["请问会议名称是什么？", "请问你想在什么时候举办会议？", "请问你想在哪里举行会议？", "请问参会人员有？"]
            # 2.ask for basic meeting info(name place participation time host)
            self.log.add_log("HASkillNotion: get basic info for create a meeting", 1)
            for i in range(0, len(meeting_info_keys)):
                key = meeting_info_keys[i]
                try:
                    meeting_info_list[key] = self.slot[key]
                except KeyError:
                    ask_slot_result = self.nlu.ask_slots([(key,  "$%s" % key, asking[i])])
                    try:
                        meeting_info_list[key] = ask_slot_result[key]
                    except KeyError:
                        self.log.add_log("HASkillNotion: ask for %s fail, can't get the slot, skip" % key, 2)
                        continue
            # 3.verify the info
            self.log.add_log("HASkillNotion: verifying the info...", 1)
            try:
                meeting_info_list["meeting_name"]
            except KeyError:
                meeting_info_list["meeting_name"] = "NewMeeting"

            tmp = meeting_info_list["date"]
            meeting_info_list["date"] = tmp[0:2]
            date_nickname_mapping = {
                "电视时间": ["20:30", "21:00"],
                "大课间": ["10:10", "10:35"],
                "做操时": ["10:10", "10:35"]
            }
            try:
                meeting_info_list["date"] = date_nickname_mapping[meeting_info_list["date"][0]]
            except KeyError:
                pass

            attenders = []
            for attender in meeting_info_list["host"]:
                attenders.append({"name": attender, "color": "default"})

            hosts = []
            for host in meeting_info_list["attender"]:
                hosts.append({"name": host, "color": "default"})

            for meeting in meeting_arrangement:
                properties = meeting["properties"]
                status = properties["状态"]["select"]["name"]
                if status != "已结束" or status != "取消":
                    meeting_host = properties["主持人"]["multi_select"][0]["name"]
                    meeting_name = properties["Name"]["title"]["plain_text"]
                    meeting_date = [properties["会议时间"]["date"]["start"][0:16].replace("T", ""), properties["会议时间"]["date"]["end"][0:16].replace("T", "")]
                    meeting_attender = [meeting_host]
                    for i in properties["参会人"]["multi_select"]:
                        meeting_attender.append(i["name"])
                    meeting_place = properties["场所"]["select"]["name"]
                    if meeting_info_list["place"] == meeting_place and self.is_date_conflict(meeting_date, meeting_info_list["date"]):
                        # date conflict
                        self.log.add_log("HASkillNotion: meet a date conflict", 2)
                        self.tts.start("由%s主持的%s会议与您的会议在时间与场所上发生冲突，请换一个时间或者地点" % (meeting_host, meeting_name))
                        return False
                    try:
                        if meeting_info_list["attender"] in meeting_attender:
                            # attender conflict
                            self.log.add_log("HASkillNotion: meet an attender conflict", 2)
                            self.tts.start("由%s主持的%s会议与您的会议的参会者有冲突。会议依然会创建，但请您知悉该冲突的存在" % (meeting_host, meeting_name))
                    except KeyError:
                        pass

            # get host info
            # use face reg, if fail, try ask

            # 4.try to update the meeting arrangement database
            self.notion_base.create_page({"database_id": database_id},
                                         self.notion_base.create_property_value_object(
                                             ["会议时间", "参会人", "场所", "主持人", "状态"],
                                             ["date", "multi_select", "select", "multi_select", "select"],
                                             [{"start": meeting_info_list["date"][0], "end": meeting_info_list["date"][1]},
                                              attenders,
                                              {"name": meeting_info_list["place"], "color": "default"},
                                              hosts,
                                              {"name": "未开始"}]
                                         ),
                                         meeting_info_list["meeting_name"])

    def add_message(self):

        """
        留言
        :return:
        """

