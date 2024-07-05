# coding=utf-8
# author: Lan_zhijiang
# description: STT engine
# date: 2020/10/3

import requests
import json
import wave
import base64
import urllib.parse
import time

# from urllib.request import urlopen
# from urllib.request import Request
from urllib.error import URLError
# from urllib.parse import urlencode
timer = time.perf_counter

from conversation.process.nlp import HANLP
from lib.log import HALog
from lib.settings import Settings
from lib.exceptions import NetworkFatal
from lib.common_func import get_token


class HASTT:

    log = HALog("HASTT")
    setting = Settings.get_json_setting("input")

    token = None

    @classmethod
    def start(cls, fp=None, ecnet=False):
        
        """
        开始语音识别
        :param fp 识别文件路径
        :return string
        """
        if cls.token is None:
            get_token(cls, cls.setting["stt"]["appKey"], cls.setting["stt"]["secretKey"])
        if fp is None:
            fp = cls.setting["recorder"]["outputPath"]

        cls.log.add_log("开始语音转文字", 1)

        speech_data = []
        try:
            with open(fp, 'rb') as speech_file:
                speech_data = speech_file.read()
        except IOError:
            cls.log.add_log("音频文件错误", 3)
            return None
        else:
            if not speech_data:
                cls.log.add_log("音频文件为空", 3)
                return None

        speech = base64.b64encode(speech_data)

        speech = str(speech, 'utf-8')
        params = {
            'dev_pid': 80001,
            'format': "wav",
            'rate': 16000,
            'token': cls.token,
            'cuid': "codemao_ha_cutomization",
            'channel': 1,
            'speech': speech,
            'len': len(speech_data)
        }
        headers = {'Content-Type': 'application/json'}

        # post_data = json.dumps(params, sort_keys=False)
        # req = Request("http://vop.baidu.com/pro_api", post_data.encode('utf-8'))
        # req.add_header()
        try:
            begin = timer()
            # f = urlopen(req)
            res = requests.post("http://vop.baidu.com/pro_api", json=params, headers=headers)
            # result_str = str(f.read(), "utf-8")
            if res.status_code == 200:
                result_obj = res.json()
            # result_obj = eval(result_str)
            cls.log.add_log("语音识别耗时： %f" % (timer() - begin), 0)
            try:
                text = result_obj["result"][0]
            except KeyError:
                cls.log.add_log("语音识别失败, API返回-%s" % result_obj, 3)
                text = None
            else:
                if ecnet:
                    text = HANLP.ecnet(text)
                cls.log.add_log("语音识别结果: %s" % text, 1)
        except URLError as err:
            cls.log.add_log('语音识别失败, 网络错误, 代码-%s' % err.code, 3)
            print(err.read())
            text = None
        
        return text
