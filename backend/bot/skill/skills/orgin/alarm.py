# coding=utf-8
# author: Lan_zhijiang
# description: skill: clock
# date: 2020/10/4


class HASkillAlarm():

    def __init__(self, ba, text, nlu_result):

        self.log = ba.log
        self.setting = ba.setting
        self.tts = ba.tts
        self.player = ba.player

        self.text = text
        self.nlu_result = nlu_result

    def start(self):

        """
        主运行函数
        :return:
        """


        
    
