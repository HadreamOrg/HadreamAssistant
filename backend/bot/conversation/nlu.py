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

        if text[0:2] == "打开":
            # open skill
            nlu_result[0] = "open_skill"
            nlu_result[1] = "launch"
            try:
                skill_called = text[2:]
                self.log.add_log("HANlu: open_skill, skill_called-%s" % skill_called, 0)
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
                        if slot_group:
                            nlp_result = self.nlp.lexer(text)
                            nlp_result = self.nlp.lexer_result_process(nlp_result)
                            # print(nlp_result)
                            for slot in slot_group:
                                ask = False
                                if "!" in slot[1]:
                                    ask = True
                                
                                if "$" in slot[1]:
                                    # dict mode
                                    slot_dict = json.load(open("./backend/data/json/skill_slots/dict_%s.json" % slot[1].replace("$", "").replace("!", "")))
                                    # print(slot_dict)
                                    if slot_dict["canNlp"]:
                                        # nlp法
                                        self.log.add_log("HANlu: start filling slot-%s in nlp mode" % slot[0], 1)
                                        try:
                                            slot_result[slot[0]] = nlp_result[slot_dict["nlpItemType"]][slot_dict["nlpItemType2"]]
                                        except KeyError:
                                            self.log.add_log("HANlu: cannot resolve slot from nlp's preset", 1)
                                            if ask:
                                                self.log.add_log("HANlu: ask slot is available, start ask slot", 1)
                                                self.tts.start(slot[2])
                                                self.player.start_recording()
                                                self.recorder.record()
                                                self.player.stop_recording()
                                                nlp_result_ = self.nlp.lexer_result_process(self.nlp.lexer(self.stt.start()))
                                                print(nlp_result_)
                                                try:
                                                    slot_result[slot[0]] = nlp_result_[slot_dict["nlpItemType"]][slot_dict["nlpItemType2"]]
                                                except KeyError:
                                                    self.tts.start("没有匹配到词槽呢，您可以在下一次提问中换一个表述试试呢")
                                                    self.log.add_log("HANlu: ask slot-%s failed, no word compared" % slot[0], 1)
                                            self.log.add_log("HANlu: ask slot is not available, skip slot", 1)
                                    else:
                                        # 自带词语匹配法
                                        slot_dict_content = slot_dict["content"]
                                        slot_compared = False
                                        for content_group in slot_dict_content:
                                            real_word = content_group[0]
                                            referring_dict = False
                                            if "$" in real_word:
                                                referring_dict = True
                                                content_group = json.load(open("./backend/data/json/skill_dicts/all_personnel.json", "r", encoding="utf-8"))
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
                                                slot_result[slot[0]] = text[text.index(a[0][-1])+1:text.index(a[1][0])]
                                        try:
                                            c = slot_result[slot[0]]
                                        except KeyError:
                                            if ask:
                                                self.log.add_log("HANlu: ask slot is available, start ask slot", 1)
                                                self.tts.start(slot[2])
                                                self.player.start_recording()
                                                self.recorder.record()
                                                asking_result = self.stt.start()
                                                compared_b = True
                                                for sentence in slot_rule_content:
                                                    a = sentence.split("$")
                                                    for i in a:
                                                        if i not in asking_result:
                                                            compared_b = False
                                                    if compared_b:
                                                        slot_result[slot[0]] = asking_result[text.index(a[0][-1]) + 1:asking_result.index(a[1][0])]
                                            else:
                                                self.log.add_log("HANlu: ask slot is not available, skip slot", 1)
                                    elif slot_rule["mode"] == "pos_mode":
                                        # pos rule mode
                                        pass
                                    # sentence and rule combiation mode
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

    def ask_slots(self, slot_name, slot_asking, slot_dict, retried_limit=2):

        """
        询问词槽
        :param slot_name: 词槽名称
        :param slot_asking: 询问话术
        :param slot_dict: 匹配字典
        :param retried_limit: 重试次数
        :type retried_limit: int
        :return dict{slot_name: target}
        """

    # def xfyun_intent_analyze(self, text):
    #
    #     """
    #     讯飞语意识别模块
    #     :param text: 文本
    #     :return:
    #     """
    #     self.log.add_log("XiaolanNlu: Getting intent with ifly nlu engine")
    #
    #     url = 'http://api.xfyun.cn/v1/aiui/v1/text_semantic?text='
    #     app_id = self.nlu_settings["appId"]  # ''
    #     api_key = self.nlu_settings["appKey"]  # ''
    #     lastmdl = self.nlu_settings["lastMdl"]  # ''
    #
    #     time_stamp = str(int(time.time()))
    #
    #     try:
    #         base64_text = base64.b64encode(text)
    #     except TypeError:
    #         intent = None
    #         return intent
    #
    #     text = 'text=' + text
    #
    #     raw = api_key + time_stamp + lastmdl + text
    #
    #     hash = hashlib.md5()
    #     hash.update(raw)
    #     check_sum = hash.hexdigest()
    #
    #     headers = {'X-Appid': app_id,
    #                'Content-type': 'application/x-www-form-urlencoded; charset=utf-8',
    #                'X-CurTime': time_stamp,
    #                'X-Param': 'eyJ1c2VyaWQiOiIxMyIsInNjZW5lIjoibWFpbiJ9',
    #                'X-CheckSum': check_sum}
    #     url = url + base64_text
    #
    #     r = requests.post(url,
    #                       headers=headers)
    #     try:
    #         json = r.json()
    #     except:
    #         return self.keyword_compare(text)
    #
    #     try:
    #         intent = json['data']['service']
    #     except KeyError:
    #         return self.keyword_compare(text)
    #     except TypeError:
    #         return self.keyword_compare(text)
    #
    #     if intent is not None:
    #         return [intent]
    #     else:
    #         return [None]
