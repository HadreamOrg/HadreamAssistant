# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant's Nlp Engine(Baidu Nlp API)
# date: 2021/12/04

import urllib.parse
import requests
import json


class HANlp:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.nlp_setting = ba.setting["bot"]["conversation"]["nlp"]

        self.app_key = self.nlp_setting["appKey"]
        self.secret_key = self.nlp_setting["secretKey"]
        self.token = ""

        self.get_token()

    def get_token(self):

        """
        获取token
        :return: str
        """
        url = 'http://openapi.baidu.com/oauth/2.0/token'
        param = {
            'grant_type': 'client_credentials',
            'client_id': self.app_key,
            'client_secret': self.secret_key
        }
        params = urllib.parse.urlencode(param)

        r = requests.get(url, params=params)
        try:
            r.raise_for_status()
            token = r.json()['access_token']
            self.token = token
            return token
        except requests.exceptions.HTTPError:
            self.log.add_log("HANlp: Cannot get token successfully", 3)
            return ""

    def lexer(self, text):

        """
        词法分析
        :param text: 原始文本
        :return:
        """
        self.log.add_log("HANlp: start text lexer: text-%s" % text, 1)

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer_custom?charset=UTF-8&access_token="
        headers = {"Content-Type": "application/json"}
        body = {"text": text}
        body = json.dumps(body)

        def a():
            r = requests.post(url+self.token,
                              data=body,
                              headers=headers)

            if r.status_code == 200:
                res = r.json()
                try:
                    if res["error_code"] == 110:
                        self.get_token()
                        result = a()
                    else:
                        result = False
                except KeyError:
                    result = res
                return result
            else:
                self.log.add_log("HANlp: text lexer meet an http error, code-%s" % r.status_code, 3)
                return False

        return a()

    def ecnet(self, text):

        """
        文本纠错
        :param text: 原始文本
        :return:
        """
        text = str(text, "utf-8")
        self.log.add_log("HANlp: start text ecnet: text-%s" % text, 1)

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/ecnet?charset=UTF-8&access_token="
        headers = {"Content-Type": "application/json"}
        body = {"text": text}
        body = json.dumps(body)

        def a():
            r = requests.post(url+self.token,
                              data=body,
                              headers=headers)

            if r.status_code == 200:
                res = r.json()
                try:
                    if res["error_code"] == 110:
                        self.get_token()
                        result = a()
                    else:
                        self.log.add_log("HANlp: ecnet meet an error, res-%s" % res, 3)
                        result = text
                except KeyError:
                    result = res["item"]["correct_query"]
                    
                return result
            else:
                self.log.add_log("HANlp: text ecnet meet an http error, code-%s" % r.status_code, 3)
                return False

        return a()

    def lexer_result_process(self, lexer_result):

        """
        对语法分析结果进行加工
        :param lexer_result: 语法分析结果
        :return: dict
        """
        self.log.add_log("HANlp: start lexer result process", 1)
        result = {
            "ne": {},  # ne: 实体类型
            "pos": {}  # pos: 词语类型 n adj adv...
        }

        items = lexer_result["items"]
        for item in items:
            now_item_info = {
                "offset": int(item["byte_offset"] / 3),
                "length": int(item["byte_length"] / 3),
                "content": item["item"],
                "basic_words": item["basic_words"],
                "ne": item["ne"],
                "pos": item["pos"]
            }
            if item["ne"] != "":
                try:
                    result["ne"][item["ne"]].append(now_item_info)
                except KeyError:
                    result["ne"][item["ne"]] = [now_item_info]
            if item["pos"] != "":
                try:
                    result["pos"][item["pos"]].append(now_item_info)
                except KeyError:
                    result["pos"][item["pos"]] = [now_item_info]

        return result

