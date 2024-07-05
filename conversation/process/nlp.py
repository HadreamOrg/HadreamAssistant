# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant's Nlp Engine(Baidu Nlp API)
# date: 2021/12/04

import urllib.parse
import requests
import json

from lib.settings import Settings
from lib.log import HALog
from lib.exceptions import NetworkFatal
from lib.common_func import get_token


class HANLP:

    log = HALog("HANLP")
    setting = Settings.get_json_setting("process")["nlp"]

    token = None

    @classmethod
    def lexer(cls, text):

        """
        词法分析
        :param text: 原始文本
        :return:
        """
        if cls.token is None:
            cls.token = get_token(cls)

        cls.log.add_log("开始词法分析 文本：%s" % text, 1)

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer_custom?charset=UTF-8&access_token=%s" % cls.token
        headers = {"Content-Type": "application/json"}
        body = {"text": text}
        body = json.dumps(body)

        def real():
            r = requests.post(url,
                              data=body,
                              headers=headers)

            if r.status_code == 200:
                res = r.json()
                try:
                    if res["error_code"] == 110:
                        get_token(cls)
                        result = real()
                    else:
                        result = False
                except KeyError:
                    result = res
                return result
            else:
                cls.log.add_log("词法分析失败, 代码-%s" % r.status_code, 3)
                return False

        return real()

    @classmethod
    def ecnet(cls, text):

        """
        文本纠错
        :param text: 原始文本
        :return:
        """
        if cls.token is None:
            get_token(cls)

        text = str(text, "utf-8")
        cls.log.add_log("start text ecnet: text-%s" % text, 1)

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/ecnet?charset=UTF-8&access_token=%s" % cls.token
        headers = {"Content-Type": "application/json", 'Accept': 'application/json'}
        body = {"text": text}
        body = json.dumps(body)

        def real():
            r = requests.post(url, data=body, headers=headers)

            if r.status_code == 200:
                res = r.json()
                try:
                    if res["error_code"] == 110:
                        get_token(cls)
                        result = real()
                    else:
                        cls.log.add_log("文本纠错失败, 响应-%s" % res, 3)
                        result = text
                except KeyError:
                    result = res["item"]["correct_query"]
                    
                return result
            else:
                cls.log.add_log("文本纠错失败, 代码-%s" % r.status_code, 3)
                return text

        return real()

    @classmethod
    def lexer_result_process(cls, lexer_result):

        """
        对语法分析结果进行加工
        :param lexer_result: 语法分析结果
        :return: dict
        """
        cls.log.add_log("start lexer result process", 1)
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


# HANLP.token = '24.0cc43b1ca58294c8a6041c38f3473cc4.2592000.1690549952.282335-35371432'
# HANLP.ecnet("你叫什么名字？") 
