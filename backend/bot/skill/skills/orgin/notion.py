# coding=utf-8
# author: Lan_zhijiang
# description: skill: tuling-robot
# date: 2020/10/4

import json
import requests


class HASkillNotion:

    def __init__(self, ba, text, nlu_result):

        self.log = ba.log
        self.setting = ba.setting
        self.tts = ba.tts
        self.player = ba.player

        self.text = text
        self.nlu_result = nlu_result

    def start(self, api_key=None):

        """
        请求tuling
        :param api_key: apikey
        :return:
        """

        data = json.load(open("./data/json/tuling_request_template.json", "r", encoding="utf-8"))
        data["perception"]["inputText"]["text"] = self.text
        data["userInfo"]["userId"] = str(self.tuling_user_id.encode("GBK"), "utf-8")

        if api_key is None:
            case = 0
            data["userInfo"]["apiKey"] = str(self.tuling_api_key.encode("GBK"), "utf-8")
        else:
            case = 1
            data["userInfo"]["apiKey"] = str(api_key.encode("GBK"), "utf-8")

        try:
            result = requests.post('http://openapi.tuling123.com/openapi/api/v2',
                                   data=json.dumps(data))
        except TypeError:
            self.log.add_log("XialanSkillTuling: request type error", 3)
            self.tts.start("出了点小错误，请检查后台")
            return

        try:
            text = result.json()["results"][-1]["values"]["text"]
        except KeyError:
            self.log.add_log("XialanSkillTuling: Can not find text in response", 3)
            self.tts.start("出了点小错误，请检查后台")
            return

        if "请求" in text and "超限制" in text:
            if case == 0:
                self.start(api_key=self.setting["apiSettings"]["tuling"]["apiKey"][1]) # c88026c156ec49099510625329f9b79d
            elif case == 1:
                self.start(api_key=self.setting["apiSettings"]["tuling"]["apiKey"][2]) # 1f39526b070d4f2791b4c3347033f191
        else:
            self.tts.start(text)
