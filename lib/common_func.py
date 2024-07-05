# author: Lanzhijiang
# date: 2023/06/28
# desc: 通用/常用/共用函数

import time
import requests
import hashlib
from lib.led import pixels
from lib.exceptions import NetworkFatal

Pixels = pixels.Pixels()


def get_token(cls=None, appkey=None, secretkey=None):

    if appkey is None or secretkey is None:
        appkey = cls.setting["appKey"]
        secretkey = cls.setting["secretKey"]

    param_str = "client_id=%s&client_secret=%s" % (appkey, secretkey)
    url = "https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&%s" % param_str

    def send():
        res = requests.post(url)

        try:
            res.raise_for_status()
        except requests.exceptions.HTTPError:
            raise NetworkFatal("百度API鉴权token")
        else:
            return res
    
    try:
        res = send()
    except NetworkFatal:
        time.wait(1)
        res = send()
    
    token = res.json()['access_token']
    try:
        cls.token = token
    except AttributeError:
        pass
    res.close()
    return token
    

    
# get_token({"token": None}, "fDHdGCpq4uNzBYb4Rtxw2nts", "pmRuKBFRmR22xAljpNp5hQTyv4n49Sep")
    

def input_packed():
    Pixels.listen()
    input_ = input("你 > ")
    Pixels.think()
    return input_

def print_packed(output):
    Pixels.speak()
    print("我 > " % output)
    Pixels.off()   

def voice_input_packed():

    from conversation.input.recorder import HARecorder
    from conversation.input.stt import HASTT
    from conversation.output.player import HAPlayer
    
    Pixels.listen()
    HAPlayer.start_recording()
    HARecorder.vad_record()
    HAPlayer.stop_recording()
    Pixels.think()
    return HASTT.start() 

def voice_output_packed(output):

    from conversation.output.tts import HATTS
    # Pixels.speak()
    HATTS.start(output)
    Pixels.off()


def get_socket_input_packed(client):

    def socket_input_packed():
        return str(client.recv(1024), encoding="utf-8")
    return socket_input_packed

def get_socket_output_packed(client):

    def socket_output_packed(output):
        return client.send(bytes(output, encoding="utf-8"))
    return socket_output_packed


def generate_sign(accesstoken, nonce, timestamp, **sth) -> str:

    """
    生成签名
    """
    m = hashlib.md5()

    raw = "Appid=%s&Keyid=%s&Nonce=%s&Time=%s%s" % (
        sth["Appid"], sth["Keyid"], nonce, timestamp, sth["Appkey"]
    )
    if accesstoken is not None:
        raw = "Accesstoken=%s&%s" % (accesstoken, raw)
    raw = raw.lower().encode(encoding="utf-8")
    
    m.update(raw)
    return m.hexdigest()

def send_request_to_aqara(intent, data: dict):

    """
    发送请求给绿米
        生成headers内容,并结合body,发起请求
    """
    headers = {
        "Accesstoken": "da16d2df0e1f44e6fb3a5e74eb7df9da",
        "Appid": "9326741751927357445c6b5a",
        "Appkey": "h14qlzk7z9zx8xlgcyu9tvrz9i845295",
        "Keyid": "K.932674175230484480",
        "Nonce": "",
        "Time": "",
        "Sign": ""
    }

    timestamp = str(int(time.time() * 1000))
    nonce: str =  timestamp  # generate_random_string()
    headers["Nonce"] = nonce
    headers["Time"] = timestamp
    headers["Sign"] = generate_sign(headers["Accesstoken"], nonce, timestamp, **headers)

    return requests.post(
        url="https://open-cn.aqara.com/v3.0/open/api",
        headers=headers,
        json={
            "intent": intent,
            "data": data
        }
    )