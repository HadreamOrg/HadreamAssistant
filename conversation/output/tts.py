# coding=utf-8
# author: Lan_zhijiang
# description: tts class
# date: 2020/10/1

import requests
import urllib.request
import urllib.parse

from conversation.output.player import HAPlayer
from lib.settings import Settings
from lib.log import HALog
from lib.exceptions import NetworkFatal
from lib.common_func import get_token


class HATTS:

    setting = Settings.get_json_setting("output")
    log = HALog("HATTS")

    token = None

    # def put_data(cls, data):
    
    #     """
    #     将数据放入player的输出队列中
    #     :param data: 要被放入的总数据
    #     :return:
    #     """
    #     cls.log.add_log("BaiduTts: Putting data start, put chunk data into player's queue", 1)
    
    #     start = 0
    #     end = cls.read_chunk-1
    
    #     c_data = data[start:end]
    #     while c_data != b'':
    #         cls.log.add_log("BaiduTts: Send chunk to player's queue", 0, is_print=False)
    #         cls.player.put(c_data)
    #         start = end + 1
    #         end+=cls.read_chunk
    #         c_data = data[start:end]
    
    #     for i in range(0, 2):
    #         time.sleep(0.05)
    #         cls.player.put('')

    @classmethod
    def start(cls, text, is_play=True):

        """
        开始生成语音
        :param text: 要转换的文本
        :param is_play: 是否立即播放
        :return:
        """
        if cls.token is None:
            get_token(cls, cls.setting["tts"]["appKey"], cls.setting["tts"]["secretKey"])

        cls.log.add_log("开始语音合成, 文本：%s" % text, 1)
        text = urllib.parse.quote_plus(text)
        data = {
            'tex': text,
            'lan': 'zh',
            'tok': cls.token,
            'ctp': 1,
            'cuid': 'codemao_ha_cutomization',
            'per': cls.setting["tts"]["per"],
            'aue': 6
        }

        data = urllib.parse.urlencode(data)
        req = urllib.request.Request('http://tsn.baidu.com/text2audio', data.encode('utf-8'))

        f = urllib.request.urlopen(req)
        result_str = f.read()
        # res = requests.post('http://tsn.baidu.com/text2audio', json=data)

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        if "audio" in headers["content-type"]:
        # if "audio" in res.headers.get("Content-Type"):
            cls.log.add_log("tts request succeed", 1)
            with open(cls.setting["player"]["say"], "wb+") as f:
                # f.write(res.content)  # error might be here
                f.write(result_str)
            if is_play:
                HAPlayer.say()
                # play_method(fp=cls.setting["player"]["say"], content=res.content)
            return True
        else:
            get_token(cls, cls.setting["tts"]["appKey"], cls.setting["tts"]["secretKey"])
            cls.log.add_log("语音合成失败 响应: %s" % result_str, 3)
            return False
