# coding=utf-8
# author: Lan_zhijiang
# description: HadreamAssistant's Nlp Engine(Baidu Nlp API)
# date: 2021/12/04

# AK: EzSEdCoje0SVvCUsFmI7bLwG
# SK: Zsyx4x9LiuzNMfhyAH2B4yCBluYCRnS2

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

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer?charset=UTF-8&access_token="
        headers = {"Content-Type": "application/json"}
        body = {"text": text}
        body = json.dumps(body)

        r = requests.post(url+self.token,
                          data=body,
                          headers=headers)

        if if token

