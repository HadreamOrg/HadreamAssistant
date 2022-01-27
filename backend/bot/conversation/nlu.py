# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant's Nlu Engine
# date: 2021/11/27

import json


class HANlu:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.nlu_setting = ba.setting["bot"]["conversation"]["nlu"]

        self.skill_manager = self.ba.skill_manager
        self.nlp = self.ba.nlp
        self.tts = ba.tts
        self.stt = ba.stt
        self.recorder = ba.recorder
        self.player = ba.player

    def analyze_intent(self, text):

        """
        原生语意识别引擎
        :param text: 文本
        :return: str
        """
        nlu_result = [0, 0, 0, 0]  # intent["operation", "intent_name", "handle_skill", "slot"]
        slot_result = {}

        if "打开" in text:
            # open skill
            nlu_result[0] = "open_skill"
            nlu_result[1] = "launch"
            try:
                open_char_index = text.index("打开")+2
                skill_called = text[open_char_index:]
                self.log.add_log("HANlu: detect open_skill, skill_called-%s" % skill_called, 0)
                skill_name = None
                for a in self.skill_manager.name_skills_list:
                    for skill_name_group in a:
                        if skill_called in skill_name_group:
                            # compared
                            skill_name = a[-1]
                            self.log.add_log("HANlu: open_skill name compared, skill-%s" % skill_name, 1)
                            break
                    if skill_name is not None:
                        break
            except KeyError:
                self.log.add_log("HANlu: skill_name-%s does not exist, open_skill fail" % text[2:], 3)
                nlu_result = ["error", None, "skill_name_not_exist", None]
            else:
                nlu_result[2] = skill_name
        else:
            # 原生意图识别（包含词槽）
            group_last_one_index = len(self.skill_manager.keyword_intent_list)
            for skill_intent_group_index in range(0, group_last_one_index):
                # 意图组循环（以一个技能能处理的意图为一组）
                # group[keywords, intents, slots, skill_name]
                # intent["operation", "intent_name", "handle_skill", "slot"]
                skill_group = self.skill_manager.keyword_intent_list[skill_intent_group_index]
                # print(skill_intent_group_index)

                skill_compared = False
                if len(skill_group[1]) > 1:
                    multiple_intents = True
                else:
                    multiple_intents = False

                intent_word_group_last_index = len(skill_group[0])
                for i in range(0, len(skill_group[0])):
                    # 技能内意图匹配
                    # print(i)
                    # print("  %s" % intent)
                    intent_word_group = skill_group[0][i]
                    intent_compared = False
                    # 关键词组匹配
                    # print(intent_word_group)
                    for word_group in intent_word_group:
                        # print(word_group)
                        word_group_compared = True
                        for word in word_group:
                            # print(word)
                            if word not in text:
                                word_group_compared = False
                                break
                        if word_group_compared:
                            intent_compared = True
                            break

                    if intent_compared:
                        # 第i个意图已经被匹配
                        # intent[2] = group[2]
                        self.log.add_log("HANlu: skill intent compared, %s-%s" % (skill_group[-1], skill_group[1][i]), 1)
                        if multiple_intents:
                            nlu_result[1] = skill_group[1][i]
                            slot_group = skill_group[2][i]
                        else:
                            nlu_result[1] = skill_group[1][0]
                            slot_group = skill_group[2][0]
                        skill_compared = True
                        nlu_result[2] = skill_group[-1]
                        # print(intent)

                        # 开始解析词槽
                        slot_result = self.get_slot(text, slot_group)
                        break
                    
                    if i == intent_word_group_last_index-1 and not intent_compared:
                        break

                if (group_last_one_index == group_last_one_index-1 and not skill_compared) or (nlu_result[1] == 0):
                    nlu_result[2] = "tuling"
                    nlu_result[1] = "launch"

                if skill_compared:
                    break

        nlu_result[-1] = slot_result

        self.log.add_log("HANlu: analyze result: %s" % nlu_result, 0)
        return nlu_result

    def skill_analyze_intent(self, text, skill_name):

        """
        技能内部意图分析
        :param text: 文本
        :param skill_name: 技能名称
        :return: list[0, "intent_name", $skill_name, "slot"]
        """
        nlu_result = [0, 0, skill_name, 0]  # intent["operation", "intent_name", "handle_skill", "slot"]

    def get_slot(self, text, slots):

        """
        提取词槽
        :param text: 文本
        :param slots: 要获取的词槽名称及其对应数据 [(name, dict/rule), (...)]
        :return: {}
        注意！！！来自于ask_slot的解析请求，不允许再次ask，否则将会陷入死循环

        STEPS:
            for slot in slots:
                加载slot的参数(slot_name, slot_data)
                    slot_data是"$"，那就是dict模式，可以使用nlp和字典匹配；如果是"*"，那就是规则模式，有前后文规则，语法规则和最垃圾的句子规则三种方式获取词槽
                    如果slot_data还带有"!"，就意味着识别不到之后需要请求ask_slot进行询问
                在字典模式中，可以通过nlp匹配，也可以通过关键词匹配，判断指标是key-canNlp
                    nlp匹配通过nlpItemType和nlpItemType2获得结果。
                        nlpItemType是ne或者pos
                        nlpItemType2是ne或者pos的下游key，即PLACE/PERSON;n/adj/adv...这些
                    词匹配通过for遍历fst词典文件

        """
        self.log.add_log("HANlu: start analyzing slots...", 1)
        slot_result = {}

        nlp_result = self.nlp.lexer(text)
        nlp_result = self.nlp.lexer_result_process(nlp_result)

        for slot in slots:
            ask = False
            if "!" in slot[1]:
                ask = True

            if "$" in slot[1]:
                # dict mode
                slot_dict = json.load(open("./backend/data/json/skill_slots/dict_%s.json" % slot[1].replace("$", "").replace("!", "")))
                if slot_dict["canNlp"]:
                    # nlp法
                    self.log.add_log("HANlu: start filling slot-%s in nlp mode" % slot[0], 1)
                    try:
                        slot_result[slot[0]] = nlp_result[slot_dict["nlpItemType"]][slot_dict["nlpItemType2"]]
                    except KeyError:
                        self.log.add_log("HANlu: cannot resolve slot from nlp's preset", 1)
                        if ask:
                            slot_result[slot[0]] = self.ask_slot([slot])[slot[0]]
                        self.log.add_log("HANlu: ask slot is not available, skip the slot", 1)
                else:
                    # 词匹配法
                    slot_dict_content = slot_dict["content"] # read dict
                    slot_compared = False
                    for content_group in slot_dict_content:
                        real_word = content_group[0]
                        referring_dict = False
                        if "$" in real_word:
                            referring_dict = True
                            content_group = json.load(open("./backend/data/json/notion/personnel_list.json", "r", encoding="utf-8"))
                        for word in content_group:
                            if word in text:
                                # 词槽存在
                                if referring_dict:
                                    real_word = word
                                slot_compared = True
                                break
                        if slot_compared:
                            slot_result[slot[0]] = real_word
                            break
                    if not slot_compared:
                        slot_result[slot[0]] = None

            elif "*" in slot[1]:
                # rule mode
                slot_rule = json.load(open("./backend/data/json/skill_slots/rule_%s.json" % slot[1].replace("*", "").replace("!", "")))

                self.log.add_log("HANlu: start filling slot-%s in rule_%s mode" % (slot[0], slot_rule["mode"]), 1)
                if slot_rule["mode"] == "sentence_mode":
                    # sentence rule mode
                    slot_rule_content = slot_rule["content"]
                    for sentence in slot_rule_content:
                        a = sentence.split("$")
                        compared_b = True
                        for i in a:
                            if i not in text:
                                compared_b = False
                        if compared_b:
                            slot_result[slot[0]] = text[text.index(a[0][-1]) + 1:text.index(a[1][0])]
                    try:
                        c = slot_result[slot[0]]
                    except KeyError:
                        if ask:
                            self.log.add_log("HANlu: ask slot is available, request asking slot", 1)
                            slot_result[slot[0]] = self.ask_slot([slot])[slot[0]]
                            # self.tts.start(slot[2])
                            # self.player.start_recording()
                            # self.recorder.record()
                            # asking_result = self.stt.start()
                            # compared_b = True
                            # for sentence in slot_rule_content:
                            #     a = sentence.split("$")
                            #     for i in a:
                            #         if i not in asking_result:
                            #             compared_b = False
                            #     if compared_b:
                            #         slot_result[slot[0]] = asking_result[text.index(a[0][-1]) + 1:asking_result.index(a[1][0])]
                        else:
                            self.log.add_log("HANlu: ask slot is not available, skip slot", 1)
                elif slot_rule["mode"] == "pos_mode":
                    # pos rule mode
                    pass
                # [sentence x rule]-mix mode
        return slot_result

    def ask_slot(self, slots_param, retried_limit=2):

        """
        询问词槽
        :param slots_param: 词槽参数[slot1_param(name, data, asking), slot2_param]
        :param retried_limit: 重试次数
        :type retried_limit: int
        :return dict{slot_name: target}

        STEPS:
            1.load the slot's info(name)
            2.
        """
        self.log.add_log("HANlu: start asking slot", 1)

        result = {}
        for slot in slots_param:
            retried = 0
            slot_name = slot[0]
            asking_text = slot[-1]
            self.log.add_log("HANlu: now asking slot-%s" % slot_name)

            if "!" in slot[1]:
                self.log.add_log("HANlu: force ask is not allowed in ask_slot, skip", 2)
                continue

            tts = self.tts
            stt = self.stt
            player = self.player
            recorder = self.recorder

            def ask():
                tts.start(asking_text)
                player.start_recording()
                recorder.record()
                a = stt.start()
                player.stop_recording()
                return a

            text = ask()
            while True:
                if text is None:
                    if retried > retried_limit:
                        self.log.add_log("HANlu: ask for slot-%s failed, text is empty, skip(over limit)" % slot[0], 3)
                        break
                    else:
                        retried += 1
                        self.log.add_log("HANlu: text is empty, retry...", 2)
                        text = ask()
                else:
                    nlu_result = self.get_slot(text, [(slot_name, slot[1])])
                    try:
                        result[slot_name] = nlu_result[slot_name]
                    except KeyError:
                        self.log.add_log("HASkillNotion: ask for place fail, can't get the slot, skip", 2)
                        continue
                    break

        return result
