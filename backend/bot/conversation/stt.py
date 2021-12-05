# coding=utf-8
# author: Lan_zhijiang
# description: STT engine
# date: 2020/10/3
import sys
import requests
import json
import wave
import base64
import urllib.parse


class HAStt:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.stt_setting = ba.setting["bot"]["conversation"]["stt"]
        self.nlp = ba.nlp

        self.app_key = self.stt_setting["appKey"]
        self.secret_key = self.stt_setting["secretKey"]
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
            self.log.add_log("HAStt: Cannot get token successfully", 3)
            return ""
        
    def start(self, fp="./backend/data/audio/record.wav"):

        """
        开始语音识别
        :param fp: 要识别的文件路径
        :return:
        """
        try:
            wav_file = wave.open(fp, 'rb')
        except IOError:
            self.log.add_log("HAStt: Can't find or open the file %s"%fp, 1)
            return []
        n_frames = wav_file.getnframes()
        frame_rate = wav_file.getframerate()
        audio = wav_file.readframes(n_frames)
        base_data = base64.b64encode(audio)

        if self.token == "":
            self.token = self.get_token()

        data = {
            "format": "wav",
            "token": self.token,
            "len": len(audio),
            "rate": frame_rate,
            "speech": str(base_data),
            "dev_pid": 80001,
            "cuid": 'b0-10-41-92-84-4d',
            "channel": 1
        }

        data = json.dumps(data)

        r = requests.post('http://vop.baidu.com/server_api',
                          data=data,
                          headers={'content-type': 'application/json'})

        print(r.json())
        if r.status_code == 200:
            res = r.json()
            text = res['result'][0].encode('utf-8')
            text = self.nlp.ecnet(text)
            self.log.add_log("HAStt: speech recognition result(after text fixing): %s" % text, 1)
            print(text)
            return text
