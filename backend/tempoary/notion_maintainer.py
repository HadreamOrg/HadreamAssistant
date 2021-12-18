# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: Notion Base Maintainer
# date: 2021/12/11

import threading
import time


class HANotionMaintainer:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.serial = ba.serial
        self.face_reg = ba.face_reg
        self.camera = ba.camera
        self.player = ba.player
        self.personnel_manager = ba.personnel_manager

        self.remind_set = {}

    def start(self):

        """
        开始maintain
        """
        self.log.add_log("HANotionMaintainer: start the notion maintainer", 1)

        human_activation_thread = threading.Thread(target=self.human_activation_thread, args=())
        data_monitor_thread = threading.Thread(target=self.data_monitor_thread, args=())

    def human_activation_thread(self):

        """
        提醒线程
        """
        self.log.add_log("HANotionMaintainer: start the reminding thread", 1)
        while True:
            time.sleep(0.1)
            serial_read = str(self.serial.readline(), "utf-8").replace("\r\n", "")
            if serial_read == "on":
                self.log.add_log("HANotionMaintainer: got 'on' from Arduino PRI, start face recognization", 1)
                person_info = self.person_identity()
                if person_info is False:
                    pass
                else:
                    person_id = person_info["id"]
                    try: 
                        remind_list = self.remind_set[person_id]
                        self.tts.start("%s同学，你有%s条留言、%s个任务等待被通知，请听————" % (person_info["name"], len(remind_list["message"]), len(remind_list["task"])))
                        messgaes = remind_list["message"]
                        tasks = remind_list["task"]
                        for i in range(0, len(messgaes)):
                            remind_type = messgaes[i]["type"]
                            remind_content = messgaes[i]["content"]
                            remind_from = messgaes[i]["from"]
                            self.tts.start("第%s条留言，%s类型，来自%s" % (i, remind_type, remind_from))
                            if remind_type == "voice":
                                self.player.basic_play(remind_content)
                            elif remind_type == "text":
                                self.tts.start(remind_content)
                            time.sleep(0.5)
                        for i in range(0, len(tasks)):
                            self.tts.start("第%s条任务" % i)
                            self.tts.start("%s在%s给您布置了任务，%s，请尽快登录Notion在任务板上查看")
                            time.sleep(0.3)
                    except KeyError:
                        pass

    def data_monitor_thread(self):

        """
        数据变动监视线程
        """
        self.log.add_log("HANotionMaintainer: start the data monitoring thread", 1)

    def add_remind_item(self, item):

        """
        添加提醒项目
        """

    def remind(self, source):

        """
        执行提醒
        :param source 提醒来源
        """

    def person_identity(self):

        """
        身份认证
        """
        tried = 1
        while tried < 4:
            if tried != 1:
                time.sleep(0.5)
            if self.face_reg.detect_face:
                self.log.add_log("HANotionMaintainer: face was detected, start identiting", 1)
                tried = 4
                self.camera.capture_image_fswebcam()
                img_data = self.face_reg.read_img("./backend/data/image/capture.jpg")
                person_id = self.face_reg.face_identity(img_data)
                person_info = self.personnel_manager.get_person_info(person_id)
                if not person_info:
                    self.log.add_log("HANotionMaintainer: the face is not found in database", 1)
                else:
                    self.log.add_log("HANotionMaintainer: the face is compared, id-%s" % person_id)
                return person_info
            else:
                self.log.add_log("HANotionMaintainer: no face detected, retry for the %s times" % tried, 1)
                tried+= 1

        return False
