# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's startup script
# date: 2021/11/4

import json
import os
from backend.base import HABase
from backend


class HARun:

    def __init__(self):

        self.setting = json.load(open("./data/json/setting.json", "r", encoding="utf-8"))
        self.log = XiaolanLog()

    def run(self):

        """
        启动小蓝
        :return:
        """
        print("""
        
            ########################################
                  小蓝-中文智能家居语音交互机器人
              (c)Lan_zhijiang all rights reserved
              http://github.com/xiaoland/xiaolan
                E-mail: lanzhijiang@foxmail.com
            ########################################
        
        """)
        self.log.add_log("Xiaolan start! ", 1)
        self.log.add_log("Self checking...", 1)

        self.log.add_log("XiaolanInit: Play the welcome speech(online tts)", 1)
        self.tts.start("你好啊，主人~这里是小蓝哦！")

        self.log.add_log("Start pulseaudio", 1)
        os.system("pulseaudio --start")

        self.log.add_log("Run snowboy awaken engine", 1)
        self.snowboy.run(self.callback)

    def callback(self):

        """
        回调函数
        :return:
        """
        self.log.add_log("XiaolanInit: Detected awaken from snowboy", 1)
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