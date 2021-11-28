# coding=utf-8
# author: Lan_zhijiang
# description: old_xiaolan's nlu engine
# date: 2020/10/3

import time
import requests
import base64
import hashlib


class HANlu:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.setting = ba.setting

        self.nlu_settings = self.setting["bot"]["conversation"]["nlu"]
        self.skill_manager = self.ba.skill_manager

    def original_intent_analyze(self, text):

        """
        原生语意识别引擎
        :param text: 文本
        :return: str
        """
        intent = []
        if "打开" in text:
            # open skill
            intent.append("open_skill")
            try:
                skill_name = self.skill_manager.name_skills_list[text[2:]]
            except KeyError:
                self.log.add_log("HANlu: skill_name-%s does not exist, open_skill fail" % text[2:], 3)
                intent = ["error", "skill_name_not_exist"]
            else:
                intent.append(skill_name)
        else:
            # other intents
            for group in self.skill_manager.keyword_intent_list.keys():
                # 意图组循环（以一个技能能处理的意图为一组）
                if len(group[1]) > 1:
                    multiple_intents = True
                else:
                    multiple_intents = False

                for i in range(0, len(group[0])):
                    # 技能内意图匹配
                    compared = True
                    for word in group[0][i]:
                        # 关键词组匹配
                        if word not in text:
                            compared = False
                            break
                    if compared:
                        # the i intent was compared
                        if multiple_intents:
                            intent.append(group[1][i])
                        else:
                            intent.append(group[1][0])
                        intent.append("")

        return intent

        # returns = []

        #
        # returns.append("talk")
        # return returns

    def skill_nlu(self, text, data):

        """
        技能专用nlu
        :param text: 要处理的文本
        :param data: 对应识别典
        :return:
        """
        intent = None
        slot = None

        for keyword in data.keys():
            if keyword in text:
                intent = data[keyword]
                slot = text[len(keyword)-1:]
                return intent, slot

        return intent, slot

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
