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

    def new_conversation(self):

        """
        启动新的对话
        :return:
        """
        self.log.add_log("HAConversation: start new conversation", 1)

        self.log.add_log("HAConversation: start recording command", 1)
        self.player.start_recording()
        self.recorder.record()
        self.player.stop_recording()
        self.log.add_log("HAConversation: start speech to text", 1)

        text = self.stt.start()
        if text is None:
            self.log.add_log("HAConversation: text is unclear, speak text_none", 1)
            self.tts.start("抱歉，我好像没有听清呢")
            return
        else:
            self.log.add_log("HAConversation: start recognizing the intent and slots", 1)
            intent = self.nlu.analyze_intent(text)
            if intent[0] == "open_skill":
                self.skill_manager.name_skill_list[intent[1]](self.ba, text, intent).start()
            elif intent[0] == "error":
                self.player.play("%s.wav" % intent[1])
            else:
                self.skill_manager.skills_list[intent[1]](self.ba, text, intent).start()

