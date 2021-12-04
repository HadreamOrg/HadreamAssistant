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

    def original_intent_analyze(self, text):

        """
        原生语意识别引擎
        :param text: 文本
        :return: str
        """
        intent = [0, 0, 0, 0] # intent["operation", "intent_name", "handle_skill", "slot"]
        slot = {}

        if "打开" in text:
            # open skill
            intent[0] = "open_skill"
            intent[1] = "launch"
            try:
                skill_name = self.skill_manager.name_skills_list[text[2:]]
            except KeyError:
                self.log.add_log("HANlu: skill_name-%s does not exist, open_skill fail" % text[2:], 3)
                intent = ["error", "skill_name_not_exist", None, None]
            else:
                intent[2] = skill_name
        else:
            # 原生意图识别（包含词槽）
            for group in self.skill_manager.keyword_intent_list.keys():
                # 意图组循环（以一个技能能处理的意图为一组）
                skill_compared = True
                if len(group[1]) > 1:
                    multiple_intents = True
                else:
                    multiple_intents = False

                last_one_index = len(group[0])
                for i in range(0, len(group[0])):
                    # 技能内意图匹配
                    intent_compared = True
                    for word in group[0][i]:
                        # 关键词组匹配
                        if word not in text:
                            intent_compared = False
                            break
                    if intent_compared:
                        # 第i个意图已经被匹配
                        if multiple_intents:
                            intent[1] = group[1][i]
                            slot_group = group[2][i]
                        else:
                            intent[1] = group[1][0]
                            slot_group = group[2][0]
                        intent[2] = group[-1]

                        # 开始解析词槽
                        nlp_result = self.nlp.analyze_text(text)
                        nlp_result = self.nlp.lexer_result_process(nlp_result)
                        for slot in slot_group:
                            if "!" in slot[1]:
                                ask = True
                            else:
                                ask = False

                            slot_result = {}
                            if "$" in slot[1]:
                                # dict mode
                                slot_dict = json.load(open("./backend/data/json/skill_slots/%s.json" % slot[1].replace("$", "").replace("!", "")))
                                if slot_dict["canNlp"]:
                                    try:
                                        slot_result[slot[0]] = nlp_result[slot_dict["nlpCheckingParam"]][slot_dict["nlpCheckingContent"]]
                                    except KeyError:
                                        self.log.add_log("HANlu: cannot resolve slot from nlp's preset", 1)
                                        slot_dict_content = slot_dict["content"]
                                        compared = False
                                        for content_group in slot_dict_content:
                                            real_word = content_group[0]
                                            for word in content_group:
                                                if word in text:
                                                    # 词槽存在
                                                    compared = True
                                                    break
                                            if compared:
                                                slot_result[slot[0]] = real_word
                                                break
                                        if not compared:
                                            slot_result[slot[0]] = None

                            elif "*" in slot[1]:
                                # rule mode
                                slot_rule = json.load(open("./backend/data/json/skill_slots/rule_%s.json" % slot[1].replace("*", "").replace("!", "")))

                        break
                    
                    if i == last_one_index and not intent_compared:
                        skill_compared = False

                if skill_compared:
                    break

        return intent

    def skill_nlu(self, text, skill):

        """
        技能内部意图识别
        :param text: 文本
        :param skill: 技能名称
        :return: intent_name(str)
        """
        intent = None
        slot = None

        for keyword in data.keys():
            if keyword in text:
                intent = data[keyword]
                slot = text[len(keyword)-1:]
                return intent, slot

        return intent, slot

    def ask_slots(self, slot_name, slot_asking, slot_dict, retry_time=2):

        """
        询问词槽
        :param slot_name: 词槽名称
        :param slot_asking: 询问话术
        :param slot_dict: 匹配字典
        :param retyr_time: 重试次数
        :type retry_time: int
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
