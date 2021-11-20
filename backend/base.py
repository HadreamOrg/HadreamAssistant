# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's startup script
# date: 2021/11/4

import json
import os
import threading

from backend.data.log import HALog
from backend.bot.conversation.tts import HATts
from backend.bot.snowboy.snowboy import HASnowboy


class HABaseAbilities:

    def __init__(self):

        self.setting = json.load(open("./backend/data/json/setting.json", "r", encoding="utf-8"))
        self.log = HALog()


class HAInit:

    def __init__(self):

        self.base_abilities = HABaseAbilities()
        self.setting = self.base_abilities.setting
        self.log = self.base_abilities.log

        self.tts = HATts(self.base_abilities)
        self.snowboy = HASnowboy(self.base_abilities)

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
        self.tts.start("你好啊，主人~这里是小蓝，你可以叫我小蓝同学~")

        self.log.add_log("HABackendInit: Start pulseaudio", 1)
        os.system("pulseaudio --start")

        self.log.add_log("HABackendInit: Run snowboy awaken engine in a thread", 1)

        self.snowboy.run(self.callback)

    def callback(self):

        """
        回调函数
        :return:
        """
        self.log.add_log("HAInit: Detected awaken from snowboy", 1)
        self.conversation()

    def conversation(self):

        """
        开始对话
        :return:
        """
        self.log.add_log("XiaolanInit: Start new conversation", 1)

        self.player.ding()
        self.recorder.record()
        self.player.dong()

        text = self.stt.start()
        if text is None:
            self.log.add_log("XiaolanInit: Text is none, play text_none(online tts)", 1)
            self.tts.start("抱歉，我好像没听清")
            return
        else:
            intent = self.nlu.get_intent(text)
            if intent[0] is None:
                self.log.add_log("XiaolanInit: Intent is none, play intent_none(online tts)", 1)
                self.tts.start("我不是很明白你的意思")
                return
            else:
                if intent[0] == "call_skill":
                    self.skills.skill_skills_list[intent[1]](self.log, self.setting, text).start()
                else:
                    self.skills.intent_skills_list[intent[0]](self.log, self.setting, text).start()


if __name__ == "__main__":
    init = XiaolanInit()
    init.run()