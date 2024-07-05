# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant: HA's bot conversation module
# date: 2021/11/20
# last_edit: 2023/06/28

import time

from lib.log import HALog
from lib.settings import Settings
from lib.common_func import input_packed, print_packed, voice_input_packed, get_socket_output_packed, voice_output_packed

from skill.skill_manager_new import get_skill_func_by_intent, get_skill_func_config, get_slot_config
from conversation.output.tts import HATTS
from conversation.process.nlu_new import HANLU


log = HALog("HAConversation")
process_setting = Settings.get_json_setting("process")


class Conversation:
    
    """
    an object store the context and some attributes of the conversation.
    
    >concepts:
    conversation:
        a conversation must complete a user's command, which based on text interaction
        it can be finished within few rounds
    round:
        a round is a single interaction between user and bot
    intent:
        represents user's intention. refering to a specific skill_func
        if the intent changed, the conversation has to be recreate

    >attributes:
    state: 
        None: 
        intent_identifying: means the intent is not accurate
        responding
        ask_for_more: means the bot need ask user more information to reach the command, 
            can attach to or cover raw 
        confirming: need user's confirmation. true of false, when false, require more info
        done: the conversation is over
    skill:
        which skill will handle the conversation
        when it's:
            None: means it's the first round, we need to use nlu to get what user wants and how to do
            <skill_func>: when a round receive the after-nlu data, it will be called with the data as param. 
                          And the func is desired to reach user's goal
    asking: 
        None: normally case
        dict: when state is ask_for_more, contains
    history: 
        a list store the conversation history. every element is a dict called round
        a round should contain: 
            bot_text
            user_text(str)
            nlu_result(dict): intent,keyword_extract,tags
    slots:
        the param needed by the skill_func to reach the command
    intent:
        skill + skill_func
        when it's a list, means not accurate, need identifying
            
    """
    def __init__(self, interface_mode: int, **sth) -> None:
        
        self.id = time.time() * 1000
        
        self.interface_mode = interface_mode
        if self.interface_mode == 0:
            input_func = input_packed
            output_func = print_packed
        elif self.interface_mode == 1:
            input_func = voice_input_packed
            output_func = voice_output_packed
        elif self.interface_mode == 2:
            input_func = sth["client"].recv
            output_func = get_socket_output_packed(sth["client"])
        self.input_func = input_func
        self.output_func = output_func

        self.state = None

        self.skill = None
        self.asking_config = None
        self.identifying_intent_config = None

        self.history = []
        self.slots_config = None
        self.slots = {}
    
    def new_round(self, ask_for_more=False, identifying_intent=False):
        
        """
        start a new round with user（bot ask or user arise）
        user_text -> nlu process text(intent_regenerate+slot_extract / intent analyze) -> 
            (state: None)arrange skill_func -> call skill_func
            store to history -> new_round/done
        :param ask: 提问参数
        """
        log.add_log("开始新ROUND, conversation_id-%s" % self.id, 1)
        round_record = {
            "mode": None, "botText": None, "userText": None, "result": None
        }

        user_text = None; bot_text = None
        if identifying_intent:
            round_record["mode"] = "identifying_intent"
            user_text, bot_text = self.identifying_intent(self.identifying_intent_config)
        if ask_for_more:
            round_record["mode"] = "ask_for_more"
            user_text, bot_text = self.ask_for_more(self.asking_config)
        if user_text is None:
            log.add_log("等待用户文本, 交互模式-%s" % self.interface_mode, 1)
            user_text = self.input_func()
        
        round_record["userText"] = user_text
        round_record["botText"] = bot_text

        if (user_text == "" or user_text is None) and not ask_for_more and not identifying_intent:
            round_record["result"] = "unclear"
            self.state = "done"
            self.output_func("抱歉，我听不清你说什么，你可以试着再说一遍")
            return

        if not ask_for_more:
            if identifying_intent:
                intent, flag = HANLU.identifying_intent(user_text, self.identifying_intent_config[1])
                if not flag:
                    log.add_log("多次尝试，仍然无法确定意图，结束对话", 1)
                    self.history.append(round_record)
                    self.end_conversation()
                    return
            else:
                intent, flag = HANLU.get_intent(user_text, self)
                if not flag and not identifying_intent:
                    round_record["result"] = "identifying_intent"
                    self.set_identifying_intent_config(intent)
                    self.history.append(round_record)
                    self.new_round(identifying_intent=True)
                    return

            self.state = "responding"
            self.intent = (intent[0],)
        
        self.skill_config: dict = get_skill_func_config(self.intent[0][0], self.intent[0][1])
        self.slot_config: list = get_slot_config(self.intent[0][0], self.skill_config["slots"])
        slots, lack_slots = HANLU.get_slot(user_text, self.slot_config)
        self.slots.update(slots)
        if lack_slots:
            round_record["result"] = "ask_for_more"
            self.state = "ask_for_more"
            self.history.append(round_record)
            self.set_asking_config(lack_slots)
            self.new_round(ask_for_more=True)
            return

        round_record["result"] = "call_skill_func"
        self.history.append(round_record)
        self.call_skill_func(user_text)
        self.state = "done"
        return

    def call_skill_func(self, user_text):

        skill_func = get_skill_func_by_intent(self.intent[0], self)
        skill_func(self.history[-1]["userText"])

    def identifying_intent(self, config):
        
        log.add_log("进入意图确认流程", 1)
        
        self.output_func(config[0])
        user_text = self.input_func()

        self.identifying_intent_config = None

        return user_text, config[0]

    def ask_for_more(self, config):
        
        """
        提问以获取更多信息
            每round只问一个
        config: asking_config
            0: length
            1:-1: ask_item[exp]
        """
        log.add_log("进入获取更多信息流程", 1)
        ask_item = config[config[0]-1]

        self.output_func(ask_item[0])
        user_text = self.input_func()

        if len(self.asking_config) == 1:
            self.asking_config = None
        self.asking_config[0] -= 1
        return user_text, ask_item[0]

    def set_asking_config(self, *asking):

        self.asking_config

    def set_identifying_intent_config(self, nlu_intent_result):
        
        exp = "抱歉，但我理解得不太清楚。请问您是想使用"
        intent_keyword_list = []
        l_l1_exp = None; l_l2_exp = None
        for i in nlu_intent_result:
            l1_exp = process_setting["intentIdentifyingExpressions"][i[0]] if i[0] is not None else ""
            l2_exp = process_setting["intentIdentifyingExpressions"][i[1]] if i[1] is not None else ""
            connctor = "的" if l2_exp != "" else ""
            intent_keyword_list.append(())

            if id(i) == id(nlu_intent_result[-1]):
                l_l1_exp = l1_exp; l_l2_exp = l2_exp
                break

            exp += "%s%s%s、" % (l1_exp, connctor, l2_exp)
        
        if len(nlu_intent_result) != 1:
            connctor = "的" if l2_exp != "" else ""
            exp += "还是%s%s%s" % (l_l1_exp, connctor, l_l2_exp)
        
        exp += "。请选择一个告诉我。"
        self.identifying_intent_config = (exp, nlu_intent_result)

    def end_conversation(self):

        """
        结束对话
        """
        self.state = "done"


class HAConversation:

    setting = Settings.get_json_setting("overall")

    current_conversation = None

    @classmethod
    def new_conversation(cls, interface_mode, **sth):

        cls.current_conversation = Conversation(interface_mode, **sth)
    
    @classmethod
    def start_conversation(cls, interface_mode, **sth):

        """
        启动新的对话
        :param interface_mode: 交互模式 1/0/2
        :return:
        """
        log.add_log("开始处理对话", 1)

        print(cls.current_conversation)
        if cls.current_conversation is None:
            cls.new_conversation(interface_mode, **sth)
        print(cls.current_conversation)
        cls.current_conversation.new_round()
        cls.current_conversation.end_conversation()
        cls.current_conversation = None

    @classmethod
    def skill_conversation(cls, skill_name):

        """
        开始技能内对话
        :param skill_name: 技能名称,用于提交给skill_nlu
        :return:
        """
        log.add_log("start skill conversation, skill-%s" % skill_name, 1)

        log.add_log("start recording command", 1)
        cls.player.start_recording()
        cls.recorder.record()
        cls.player.stop_recording()
        log.add_log("start speech to text", 1)
        text = cls.stt.start()

        if text is None:
            log.add_log("text is unclear, speak text_none", 1)
            cls.tts.start("抱歉，我听不清楚")  # should be replaced by local playing
            return None
        else:
            log.add_log("start analyzing the intent and slots", 1)
            nlu_result = cls.nlu.skill_analyze_intent(text)
            if nlu_result[0] == "error":
                cls.player.baisc_play("./data/audio/%s.wav" % nlu_result[2])
                return None
            else:
                return nlu_result

