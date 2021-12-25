# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's backend base
# date: 2021/11/4

import json
import os
import threading
import keyboard
import serial

from backend.data.log import HALog
from backend.bot.snowboy.snowboy import HASnowboy
from backend.bot.maintain.notion.notion_maintainer import HANotionMaintainer
from backend.bot.ai.face_reg import HAAiFaceReg
from backend.device.camera import HACamera
# from backend.bot.maintain.maintainer import HAMaintainer
from backend.bot.maintain.notion.personnel_manager import HAPersonnelManager
from backend.bot.skill.skill_manager import HASkillManager

from backend.bot.conversation.conversation import HAConversation
from backend.bot.conversation.stt import HAStt
from backend.bot.conversation.tts import HATts
from backend.bot.conversation.nlu import HANlu
from backend.bot.conversation.nlp import HANlp
from backend.bot.conversation.recorder import HARecorder
from backend.bot.conversation.player import HAPlayer


class HABaseAbilities:

    def __init__(self):

        self.setting = json.load(open("./backend/data/json/setting.json", "r", encoding="utf-8"))
        self.log = HALog("main")
        self.notion_maintainer_log = HALog("notion_maintainer")

        # self.serial = serial.Serial("/dev/ttyACM0", 9600, timeout=1)

        self.player = HAPlayer(self)
        self.recorder = HARecorder(self)
        self.skill_manager = HASkillManager(self)
        self.tts = HATts(self)
        self.nlp = HANlp(self)
        self.stt = HAStt(self)
        self.nlu = HANlu(self)
        self.camera = HACamera(self)
        self.face_reg = HAAiFaceReg(self)
        self.personnel_manager = HAPersonnelManager(self)

        self.snowboy = HASnowboy(self)
        self.conversation = HAConversation(self)
        # self.notion_maintainer = HANotionMaintainer(self)
        # self.maintainer = HAMaintainer(self)


class HAInit:

    def __init__(self):

        self.base_abilities = HABaseAbilities()
        self.setting = self.base_abilities.setting
        self.log = self.base_abilities.log

        self.snowboy = self.base_abilities.snowboy
        # self.notion_maintainer = self.base_abilities.notion_maintainer
        self.conversation = self.base_abilities.conversation
        self.player = self.base_abilities.player

        self.awake = False
        self.interface_mode = 1

    def run(self):

        """
        启动HadreamAssistant
        :return:
        """
        self.log.add_log("""

            ###########################################
                         HadreamAssistant
                   ---Customize Work Assistant---
              (c)2021 Lanzhijiang all rights reserved
                  Email: lanzhijiang@foxmail.com
            ###########################################

        """, 1)
        self.log.add_log("HABackendInit: HadreamAssistant start ", 1)
        self.log.add_log("HABackendInit: start self check", 1)

        self.log.add_log("HABackendInit: play the welcome speech(local play) ", 1)
        self.player.basic_play("./backend/data/audio/welcome.wav")

        self.log.add_log("HABackendInit: Start pulseaudio", 1)
        os.system("pulseaudio --start")

        self.log.add_log("HABackendInit: Start three threads", 1)

        keyboard_thread = threading.Thread(target=self.keyboard_awake, args=(self.callback,))
        snowboy_thread = threading.Thread(target=self.snowboy.run, args=(self.callback,))
        awake_detect_thread = threading.Thread(target=self.awaken_detect, args=())
        # notion_maintainer_thread = threading.Thread(target=self.notion_maintainer.start, args=())
        snowboy_thread.start()
        keyboard_thread.start()
        awake_detect_thread.start()
        # notion_maintainer_thread.start()

    def callback(self):

        """
        唤醒回调函数
        :return:
        """
        self.log.add_log("HAInit: Detected awaken from snowboy/keyboard, change self.awake to True", 1)
        self.awake = True

    def awaken_detect(self):

        """
        检测唤醒flag以开始对话
        :return:
        """
        self.log.add_log("HAInit: start detecting awake status", 1)
        while True:
            if self.awake:
                self.log.add_log("HAInit: self.awake is True, start conversation", 1)
                self.conversation.new_conversation(self.interface_mode)
                self.interface_mode = 1
                self.awake = False

    def keyboard_awake(self, callback):

        """
        键盘按键唤醒
        :callback: 回调函数
        :return:
        """
        while True:
            try:
                keyboard.wait("enter")
            except ImportError:
                self.log.add_log("HAInit: keyboard awaken engine need to be run as root, exit", 3)
                raise ImportError
            if not self.awake:
                self.log.add_log("HAInit: 'enter' was pressed, please mode: 1-voice, 0-text", 1)
                a = input("chose your interface mode")
                if a == "1":
                    self.interface_mode = 1
                    callback()
                elif a == "0":
                    self.interface_mode = 0
                    callback()
                else:
                    self.log.add_log("HAInit: wrong mode-%s chosen, you should chose between 0 and 1", 2)
            else:
                self.log.add_log("HAInit: keyboard awaken is now disabled, conversation is under process", 2)
