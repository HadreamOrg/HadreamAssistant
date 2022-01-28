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
                        slot_result = self.get_slot(text, [slot_group])
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
        :param slots: 要获取的词槽名称及其对应数据 [(slot_name, slot_data, asking), (...)]
        :return: {}
        注意！！！来自于ask_slot的解析请求，不允许再次ask，否则将会陷入死循环

        STEPS:
            for slot in slots:
                加载slot的参数(slot_name, slot_data)
                    slot_data是"$"，那就是dict模式，可以使用nlp和字典匹配；如果是"*"，那就是规则模式，有前后文规则，词性规则和最垃圾的句子规则三种方式获取词槽
                    如果slot_data还带有"!"，就意味着识别不到之后需要请求ask_slot进行询问
                在字典模式中，可以通过nlp匹配，也可以通过关键词匹配，判断指标是key-canNlp
                    nlp匹配通过nlpItemType和nlpItemType2获得结果。
                        nlpItemType是ne或者pos
                        nlpItemType2是ne或者pos的下游key，即PLACE/PERSON;n/adj/adv...这些
                    词匹配通过for遍历key-content下的内容
                        key-content: [[real_word, SMW1, SMW2, SMWn], [real_word, ...]]
                在规则模式中，可以通过前后文锁定词槽，也可以通过词性提取，还可以通过句子格式匹配
                    前后文锁定模式(context_mode)
                        其content为{"length": [int, int], "last": ["xxx", "zzz"], "next": ["yyy", None]}
                    词性模式(pos_mode)
                        其content为[{"pos": "", "length": [], "max": int}]
                    句子格式模式(sentence_mode)
                        其content为["xxxx&xxxx,xxxx", "xxxxxx&"]这样的
        """
        self.log.add_log("HANlu: start analyzing slots...", 1)
        slot_result = {}

        nlp_result = self.nlp.lexer(text)
        nlp_result = self.nlp.lexer_result_process(nlp_result)

        for slot in slots:
            slot_name = slot[0]
            slot_result[slot_name] = []

            ask = False
            if "!" in slot[1]:
                ask = True

            if "$" in slot[1]:
                # dict mode
                slot_dict = json.load(open(r"./backend/data/json/skill_slots/dict_%s.json" % slot[1].replace("$", "").replace("!", "")))
                if slot_dict["canNlp"]:
                    # nlp法
                    self.log.add_log("HANlu: start analyzing slot-%s in nlp mode" % slot_name, 1)
                    try:
                        slot_result[slot_name].append(nlp_result[slot_dict["nlpItemType"]][slot_dict["nlpItemType2"]])
                    except KeyError:
                        self.log.add_log("HANlu: cannot resolve slot from nlp's preset", 1)
                        if ask:
                            self.log.add_log("HANlu: slot-%s not compared and asking is available, request ask_slot" % slot_name, 1)
                            slot_result[slot_name] = self.ask_slot([slot])[slot_name]
                        else:
                            self.log.add_log("HANlu: asking slot is not required, skip the slot", 1)
                else:
                    # 词匹配法
                    slot_dict_content = slot_dict["content"] # read word list
                    slot_compared = False
                    for content_group in slot_dict_content:
                        group_compared = False
                        real_word = content_group[0]
                        if "$" in real_word:
                            # 引用了字典文件，加载字典文件
                            content_group = json.load(open(r"./backend/data/json/skill_dicts/%s.json" % real_word.replace("$", ""), "r", encoding="utf-8"))
                            real_word = content_group[0]
                        for word in content_group:
                            if word in text:
                                # 词语存在，该组已匹配
                                group_compared = True
                                slot_compared = True
                                break
                        if group_compared:
                            slot_result[slot_name].append(real_word)

                    if not slot_compared:
                        if ask:
                            self.log.add_log("HANlu: slot-%s not compared and asking is available, request ask_slot" % slot_name, 1)
                            slot_result[slot_name] = self.ask_slot([slot])[slot_name]
                        else:
                            self.log.add_log("HANlu: asking slot is not required, skip the slot", 1)

            elif "*" in slot[1]:
                # rule mode
                slot_rule = json.load(open(r"./backend/data/json/skill_slots/rule_%s.json" % slot[1].replace("*", "").replace("!", "")))

                self.log.add_log("HANlu: start analyzing slot-%s in rule_%s mode" % (slot_name, slot_rule["mode"]), 1)
                mode = slot_rule["mode"]
                slot_compared = False

                if mode == "context_mode":
                    try:
                        length_group = slot_rule["content"]["length"]
                    except KeyError:
                        length_group = None
                    last_group = slot_rule["content"]["last"]
                    next_group = slot_rule["content"]["next"]
                    # both; 1,None
                    for i in range(0, len(last_group)):
                        last_word = last_group[i]
                        next_word = next_group[i]

                        try:
                            offset = text.index(last_word) + len(last_word)
                            if (next_word is None or next_word == "") and length_group is not None:
                                end = offset + length_group[i]
                                word = text[offset:end]
                            else:
                                end = text.index(next_word)
                                word = text[offset:end]
                                if length_group is not None:
                                    if len(word) != length_group[i]:
                                        self.log.add_log("HANlu: word's length not matched, skip", 3)
                                        continue
                                    else:
                                        slot_compared = True
                        except ValueError:
                            self.log.add_log("HANlu: last/next_word was not found in text(context_mode), continue", 2)
                            continue
                        else:
                            slot_result[slot_name].append(word)
                elif mode == "pos_mode":
                    for group in slot_rule["content"]:
                        pos = group["pos"]
                        length = group["length"]
                        max_ = group["max"]

                        count = 0
                        for word_data in nlp_result["pos"][pos]:
                            if word_data["length"] in length:  # 注意这里是in哦
                                count += 1
                                slot_compared = True
                                slot_result[slot_name].append(word_data["content"])
                                if count >= max_:
                                    break
                elif mode == "sentence_mode":
                    # sentence mode
                    sentence_group = slot_rule["content"]

                    for sentence in sentence_group:
                        sentence_parts = sentence.split("$")
                        sentence_compared = True
                        for part in sentence_parts:
                            if part not in text:
                                sentence_compared = False

                        if sentence_compared:
                            # 句型完全匹配
                            for i in range(0, len(sentence_parts)):
                                part = sentence_parts[i]
                                next_part = sentence_parts[i+1]
                                offset = text.index(part) + len(part)
                                end = offset + text.index(next_part)
                                slot_result[slot_name].append(text[offset:end])
                            slot_compared = True
                            break  # sentence_mode是这样的
                else:
                    self.log.add_log("HANlu: rule_mode-mode-%s does not supported" % mode, 2)
                    continue

                if slot_compared is False:
                    if ask:
                        self.log.add_log("HANlu: slot-%s not compared and asking is available, request ask_slot" % slot_name, 1)
                        slot_result[slot_name] = self.ask_slot([slot])[slot_name]
                    else:
                        self.log.add_log("HANlu: asking slot is not required, skip the slot", 1)
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
            result[slot_name] = []
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
                        result[slot_name].append(nlu_result[slot_name])
                    except KeyError:
                        self.log.add_log("HASkillNotion: ask for place fail, can't get the slot, skip", 2)
                        continue
                    break

        return result
