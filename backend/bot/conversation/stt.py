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
        
    def start(self, fp="./data/audio/record.wav"):

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
            "speech": base_data,
            "cuid": 'b0-10-41-92-84-4d',
            "channel": 1
        }
        
        data = json.dumps(data)
        
        r = requests.post('http://vop.baidu.com/server_api',
                          data=data,
                          headers={'content-type': 'application/json'})
        
        try:
            r.raise_for_status()
            text = ""
            if 'result' in r.json():
                text = r.json()['result'][0].encode('utf-8')
                return text
        except requests.exceptions.HTTPError:
            self.log.add_log('HAStt: Request failed with response: %r'%r.text, 1)
            return None
        except requests.exceptions.RequestException:
            print ('Request failed.')
            return None
        except ValueError as e:
            print ('HAStt: Cannot parse response: %s'%e.args[0], 1)
            return None
        except KeyError:
            self.log.add_log('HAStt: Cannot parse response', 1)
            return None
        else:
            transcribed = []
            if text:
                transcribed.append(text.upper())
            self.log.add_log("HAStt: " + str(r.json()), 1)
        
