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

from urllib.request import urlopen
from urllib.request import Request
from urllib.error import URLError
from urllib.parse import urlencode
timer = time.perf_counter


class HAStt:

    def __init__(self):

        self.app_key = "TSFp0BKH547h7Agjf2WkV2Ll"
        self.secret_key = "c9RZ1ZLxPe6wQVWOUwjaWOLvM7EpXHwe"
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
            print("HAStt: Cannot get token successfully")
            return ""

    def start(self, fp="./record.wav"):
        
        """
        开始语音识别
        :param fp 识别文件路径
        :return string
        """
        print("HAStt: start speech to text")
        speech_data = []
        with open(fp, 'rb') as speech_file:
            speech_data = speech_file.read()

        length = len(speech_data)
        # if length == 0:
        #     raise DemoError('file %s length read 0 bytes' % AUDIO_FILE)
        speech = base64.b64encode(speech_data)

        speech = str(speech, 'utf-8')
        params = {
            'dev_pid': 80001,
            'format': "wav",
            'rate': 16000,
            'token': self.token,
            'cuid': "hadream_assistant",
            'channel': 1,
            'speech': speech,
            'len': length
        }

        post_data = json.dumps(params, sort_keys=False)
        req = Request("http://vop.baidu.com/pro_api", post_data.encode('utf-8'))
        req.add_header('Content-Type', 'application/json')
        try:
            begin = timer()
            f = urlopen(req)
            result_str = str(f.read(), "utf-8")
            # printtype(result_str))
            result_str = eval(result_str)
            print("HAStt: stt request time cost %f" % (timer() - begin))
            print("HAStt: stt response %s" % result_str, 0)
            text = result_str["result"][0].encode("utf-8")
            print("HAStt: speech recognition result(after text fixing): %s" % text)
        except URLError as err:
            print('HAStt: stt http response http code : ' + str(err.code))
            print(err.read())
            text = None

        # result_str = str(result_str, 'utf-8')
        
        return text
    
    
stt = HAStt()
print(stt.start())
