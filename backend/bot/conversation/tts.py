# coding=utf-8
# author: Lan_zhijiang
# description: tts class
# date: 2020/10/1

import requests
import urllib.request
import urllib.parse


class HATts:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.tts_setting = ba.setting["bot"]["conversation"]["tts"]
        self.player = ba.player

        self.token = ""
        self.app_key = self.tts_setting["appKey"]
        self.secret_key = self.tts_setting["secretKey"]

        self.get_token()
        
    def get_token(self):

        """
        获取token
        :return:
        """
        param = {'grant_type': 'client_credentials',
                 'client_id': self.app_key,
                 'client_secret': self.secret_key}
        params = urllib.parse.urlencode(param)
        r = requests.get('http://openapi.baidu.com/oauth/2.0/token', params=params)
        try:
            r.raise_for_status()
            token = r.json()['access_token']
            self.token = token
            return token
        except requests.exceptions.HTTPError:
            self.log.add_log("HATts: failed to get token, http error, code-%s " % r.status_code, 3)
            return ""

    # def put_data(self, data):
    #
    #     """
    #     将数据放入player的输出队列中（2号线程）
    #     :param data: 要被放入的总数据
    #     :return:
    #     """
    #     self.log.add_log("BaiduTts: Putting data start, put chunk data into player's queue", 1)
    #
    #     start = 0
    #     end = self.read_chunk-1
    #
    #     c_data = data[start:end]
    #     while c_data != b'':
    #         self.log.add_log("BaiduTts: Send chunk to player's queue", 0, is_print=False)
    #         self.player.put(c_data)
    #         start = end + 1
    #         end+=self.read_chunk
    #         c_data = data[start:end]
    #
    #     for i in range(0, 2):
    #         time.sleep(0.05)
    #         self.player.put('')

    def start(self, text, is_play=True):

        """
        开始生成语音
        :param text: 要转换的文本
        :param is_play: 是否立即播放
        :return:
        """
        self.log.add_log("HATts: start tts, text-%s" % text, 1)
        text = urllib.parse.quote_plus(text)
        data = {
            'tex': text,
            'lan': 'zh',
            'tok': self.token,
            'ctp': 1,
            'cuid': 'hadream_assistant',
            'per': self.tts_setting["per"],
            'aue': 6
        }

        data = urllib.parse.urlencode(data)
        req = urllib.request.Request('http://tsn.baidu.com/text2audio', 
                              data.encode('utf-8'))

        f = urllib.request.urlopen(req)
        result_str = f.read()

        headers = dict((name.lower(), value) for name, value in f.headers.items())

        if "audio" in headers["content-type"]:
            self.log.add_log("HATts: tts request succeed", 1)
            with open("./backend/data/audio/say.wav", "wb+") as f:
                f.write(result_str)
            if is_play:
                self.player.say()
            return True
            # if is_play:
            #     put_data_t = threading.Thread(target=self.put_data, args=(result_str,))
            #     stream_out_t = threading.Thread(target=self.player.stream_output, args=())
            #     put_data_t.start()
            #     stream_out_t.start()
            # else:
            #     with open("./data/audio/say.wav", "wb+") as f:
            #         f.write(result_str)
            #     self.player.say()
            #     return True
        else:
            self.get_token()
            self.log.add_log("HATts: Tts meet an error! Response: %s" % str(result_str), 3)
            return False
