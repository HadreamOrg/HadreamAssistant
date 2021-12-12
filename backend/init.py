# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's backend base
# date: 2021/11/4

import json
import os
import threading
import keyboard

from backend.data.log import HALog
from backend.bot.snowboy.snowboy import HASnowboy
from backend.bot.maintain.maintainer import HAMaintainer
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
        self.log = HALog()
        self.skill_manager = HASkillManager(self)
        self.player = HAPlayer(self)
        self.recorder = HARecorder(self)
        self.nlp = HANlp(self)
        self.nlu = HANlu(self)
        self.stt = HAStt(self)
        self.tts = HATts(self)
        self.snowboy = HASnowboy(self)
        self.conversation = HAConversation(self)
        self.maintainer = HAMaintainer


class HAInit:

    def __init__(self):

        self.base_abilities = HABaseAbilities()
        self.setting = self.base_abilities.setting
        self.log = self.base_abilities.log

        self.snowboy = self.base_abilities.snowboy
        self.maintainer = self.base_abilities.maintainer
        self.conversation = self.base_abilities.conversation
        self.tts = self.base_abilities.tts

        self.awake = False
        self.interface_mode = 1

    def run(self):

        """
        启动HadreamAssistant
        :return:
        """
        print("""

            ##########################################
                        HadreamAssistant
             (c)2021 Lanzhijiang all rights reserved
                 Email: lanzhijiang@foxmail.com
            ##########################################

        """)
        self.log.add_log("HABackendInit: HadreamAssistant start ", 1)
        self.log.add_log("HABackendInit: start self check", 1)

        self.log.add_log("HABackendInit: play the welcome speech(online tts) ", 1)
        self.tts.start("你好啊!~ 这里是小蓝，你可以叫我小蓝同学~")

        self.log.add_log("HABackendInit: Start pulseaudio", 1)
        os.system("pulseaudio --start")

        self.log.add_log("HABackendInit: Run snowboy awaken engine in a thread", 1)

        keyboard_thread = threading.Thread(target=self.keyboard_awake, args=())
        snowboy_thread = threading.Thread(target=self.snowboy.run, args=(self.callback,))
        maintainer_thread = threading.Thread(target=self.maintainer.run, args=())
        snowboy_thread.run()
        maintainer_thread.run()
        # self.snowboy.run(self.callback)

    def callback(self):

        """
        唤醒回调函数
        :return:
        """
        self.log.add_log("HAInit: Detected awaken from snowboy/keyboard", 1)
        if not self.awake:
            self.awake = True
            self.conversation.new_conversation(self.interface_mode)
            self.awake = False
        else:
            self.log.add_log("HAInit: conversation is under process, awaken was locked, miss the awaken", 1)

    def keyboard_awake(self):

        """
        键盘按键唤醒
        :return:
        """
        while True:
            keyboard.wait("enter")
            self.log.add_log("HAInit: 'enter' was pressed, please mode: 1-voice, 0-text", 1)
            a = input("chose your interface mode")
            if a == "1":
                self.interface_mode = 1
                self.callback()
            elif a == "0":
                self.interface_mode = 0
                self.callback()
            else:
                self.log.add_log("HAInit: wrong mode-%s chosen, you should chose between 0 and 1", 2)

    # def conversation(self):
    #
    #     """
    #     开始对话
    #     :return:
    #     """
    #     self.log.add_log("XiaolanInit: Start new conversation", 1)
    #
    #     self.player.ding()
    #     self.recorder.record()
    #     self.player.dong()
    #
    #     text = self.stt.start()
    #     if text is None:
    #         self.log.add_log("XiaolanInit: Text is none, play text_none(online tts)", 1)
    #         self.tts.start("抱歉，我好像没听清")
    #         return
    #     else:
    #         intent = self.nlu.get_intent(text)
    #         if intent[0] is None:
    #             self.log.add_log("XiaolanInit: Intent is none, play intent_none(online tts)", 1)
    #             self.tts.start("我不是很明白你的意思")
    #             return
    #         else:
    #             if intent[0] == "call_skill":
    #                 self.skills.skill_skills_list[intent[1]](self.log, self.setting, text).start()
    #             else:
    #                 self.skills.intent_skills_list[intent[0]](self.log, self.setting, text).start()
