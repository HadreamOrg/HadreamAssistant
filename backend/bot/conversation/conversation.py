# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's bot conversation module
# date: 2021/11/20


class HAConversation:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.player = self.ba.player
        self.recorder = self.ba.recorder
        self.stt = self.ba.stt
        self.tts = self.ba.tts
        self.nlu = self.ba.nlu
        self.skill_manager = self.ba.skill_manager

    def new_conversation(self, interface_mode):

        """
        启动新的对话
        :param interface_mode: 交互模式 1/0
        :return:
        """
        self.log.add_log("HAConversation: start new conversation", 1)

        if interface_mode == 1:
            self.log.add_log("HAConversation: start recording command", 1)
            self.player.start_recording()
            self.recorder.record()
            self.player.stop_recording()
            self.log.add_log("HAConversation: start speech to text", 1)
            text = self.stt.start()
        elif interface_mode == 0:
            self.log.add_log("HAConversation: please input your words", 1)
            text = input()
            if text == "":
                text = None
        else:
            text = None

        if text is None:
            self.log.add_log("HAConversation: text is unclear, speak text_none", 1)
            self.tts.start("抱歉，我听不清楚")  # should be replaced by local playing
            return
        else:
            self.log.add_log("HAConversation: start recognizing the intent and slots", 1)
            nlu_result = self.nlu.analyze_intent(text)
            if nlu_result[0] == "open_skill":
                if nlu_result[2] is None:
                    self.log.add_log("HAConversation: open_skill failed, skill_name is None", 3)
                    return
                self.skill_manager.name_skill_list[nlu_result[2]](self.ba, text, nlu_result).start()
            elif nlu_result[0] == "error":
                self.player.baisc_play("./backend/data/audio/%s.wav" % nlu_result[2])
            else:
                self.skill_manager.skills_list[nlu_result[2]](self.ba, text, nlu_result).start()

    def skill_conversation(self, skill_name):

        """
        开始技能内对话
        :param skill_name: 技能名称，用于提交给skill_nlu
        :return:
        """
        self.log.add_log("HAConversation: start skill conversation, skill-%s" % skill_name, 1)

        self.log.add_log("HAConversation: start recording command", 1)
        self.player.start_recording()
        self.recorder.record()
        self.player.stop_recording()
        self.log.add_log("HAConversation: start speech to text", 1)
        text = self.stt.start()

        if text is None:
            self.log.add_log("HAConversation: text is unclear, speak text_none", 1)
            self.tts.start("抱歉，我听不清楚")  # should be replaced by local playing
            return None
        else:
            self.log.add_log("HAConversation: start analyzing the intent and slots", 1)
            nlu_result = self.nlu.skill_analyze_intent(text)
            if nlu_result[0] == "error":
                self.player.baisc_play("./backend/data/audio/%s.wav" % nlu_result[2])
                return None
            else:
                return nlu_result

