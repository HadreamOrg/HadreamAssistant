# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: Notion Base Maintainer
# date: 2021/12/11

import threading
import time
import json


class HANotionMaintainer:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.notion_maintainer_log
        self.setting = ba.setting

        self.serial = ba.serial
        self.face_reg = ba.face_reg
        self.camera = ba.camera
        self.tts = ba.tts
        self.player = ba.player
        self.personnel_manager = ba.personnel_manager

        self.remind_set = json.load(open("./backend/data/json/notion_remind_set.json", "r", encoding="utf-8"))

    def start(self):

        """
        开始maintain
        """
        self.log.add_log("HANotionMaintainer: start the notion maintainer", 1)

        human_activation_thread = threading.Thread(target=self.human_activation_thread, args=())
        data_monitor_thread = threading.Thread(target=self.data_monitor_thread, args=())

        human_activation_thread.start()
        data_monitor_thread.start()

    def human_activation_thread(self):

        """
        人体活动检测线程
        """
        self.log.add_log("HANotionMaintainer: start the human activation detecting for reminding thread", 1)
        while True:
            time.sleep(0.1)
            serial_read = str(self.serial.readline(), "utf-8").replace("\r\n", "")
            # print(serial_read)
            if serial_read != "0":
                self.log.add_log("HANotionMaintainer: Arduino PRI detected people, start person identity", 1)
                person_info = self.person_identity()
                if person_info is False:
                    self.log.add_log("HANotionMaintainer: person identity failed", 2)
                    # time.sleep(2)
                else:
                    self.log.add_log("HANotionMaintainer: person identity success", 1)
                    person_id = person_info["id"]
                    self.remind("detecter", person_id, person_info)
                    # print("--------------------------------------------")
                    # time.sleep(1.5)

    def data_monitor_thread(self):

        """
        数据变动监视线程
        """
        self.log.add_log("HANotionMaintainer: start the data monitoring thread", 1)

    def person_identity(self):

        """
        身份认证
        """
        # {'error_code': 0, 'error_msg': 'SUCCESS', 'log_id': 7535790505997, 'timestamp': 1639477383, 'cached': 0, 'result': {'face_token': '6758ddef2ff7ef04b210808705009786', 'user_list': [{'group_id': 'all', 'user_id': 'hyl', 'user_info': '', 'score': 25.866611480713}]}}
        tried = 1
        while tried < 3:
            if tried != 1:
                time.sleep(1)
            self.log.add_log("HANotionMaintainer: start person identifying, tried-%s" % tried, 1)
            tried += 1
            self.camera.capture_image_cv()
            img_data = self.face_reg.read_img("./backend/data/image/capture.jpg", "file_path")
            face_iden_result = self.face_reg.face_identify(img_data)

            try:
                if int(face_iden_result["result"]["user_list"][0]["score"]) > 70:
                    person_id = face_iden_result["result"]["user_list"][0]["user_id"]
                else:
                    self.log.add_log("HANotionMaintainer: un-trust person, score is too low")
                    continue
            except TypeError:
                self.log.add_log("HANotionMaintainer: picture don't have a face", 2)
                continue
            person_info = self.personnel_manager.get_person_info(person_id)
            if not person_info:
                self.log.add_log("HANotionMaintainer: the person-%s is not found" % person_id, 1)
                continue
            else:
                self.log.add_log("HANotionMaintainer: the person-%s's info is found" % person_id, 1)
                return person_info

        return False

    def add_remind_item(self, target_id, remind_type, remind_from, remind_content, remind_time=None, message_type="text"):

        """
        添加提醒项目
        :param target_id: 人员id
        :param remind_type: 提醒类型
        :param remind_from: 提醒来源
        :param remind_content: 提醒内容
        :param remind_time: 提醒发起时间
        :param message_type: 消息类型
        :return:
        """
        self.log.add_log("HANotionManager: add a %s remind item to %s remind list" % (remind_type, target_id), 1)

        try:
            remind_list = self.remind_set[target_id]
            new = False
        except KeyError:
            new = True
            remind_list = {
                "message": [],
                "task": []
            }
        if remind_type == "message":
            remind_list["message"].append({
                "type": message_type,
                "content": remind_content,
                "from": remind_from
            })
        elif remind_type == "task":
            if remind_time is None:
                remind_time = self.log.get_date()
            remind_list["task"].append({
                "name": remind_content,
                "from": remind_from,
                "time": remind_time
            })

        if new:
            self.remind_set[target_id] = remind_list

        self.save_remind_set()

    def save_remind_set(self):

        """
        保存remind_set
        :return:
        """
        self.log.add_log("HANotionMaintainer: saving the remind set to local", 1)
        json.dump(self.remind_set, open("./backend/data/json/notion_remind_set.json", "w", encoding="utf-8"))

    def remind(self, source, person_id, person_info):

        """
        执行提醒
        :param source 提醒来源
        :param person_id 人员id
        :param person_info 人员信息
        """
        department = person_info["department"]
        if department == "teacher":
            department = "老师"
        else:
            department = "同学"
        call = person_info["name"] + department
        try:
            remind_list = self.remind_set[person_id]
            self.tts.start("%s，你有%s条留言、%s个任务等待被通知，请听————" % (call, len(remind_list["message"]), len(remind_list["task"])))
            messgaes = remind_list["message"]
            tasks = remind_list["task"]
            for i in range(0, len(messgaes)):
                message_type = messgaes[i]["type"]
                message_content = messgaes[i]["content"]
                message_from = messgaes[i]["from"]
                self.tts.start("第%s条留言，%s类型，来自%s" % (i+1, message_type, message_from))
                if message_type == "voice":
                    self.player.basic_play(message_content)
                elif message_type == "text":
                    self.tts.start(message_content)
                time.sleep(0.5)
            for i in range(0, len(tasks)):
                task_name = tasks[i]["name"]
                task_from = tasks[i]["from"]
                task_time = tasks[i]["time"]
                self.tts.start("第%s条任务" % str(i+1))
                self.tts.start("%s在%s给您布置了任务，%s，请尽快登录Notion在任务板上查看" % (task_from, task_time, task_name))
                time.sleep(0.5)
            del self.remind_set[person_id]
            self.save_remind_set()
        except KeyError:
            if source == "skill":
                self.tts.start("%s，您暂时没有任何提醒哦~" % call)
            elif source == "detecter":
                self.tts.start("Test success, person identity success, welcome，-%s，你好！" % call)
