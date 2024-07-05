# coding=utf-8
# author: Lan_zhijiang
# description: skill: turing chat robot
# date: 2020/10/4

import json
import requests

# from conversation.output.tts import HATTS
from lib.log import HALog


log = HALog("HASkillTuring")
setting = json.load(open("./data/skill_config/turing_setting.json", "r"))
conversation = None

tuling_api_key = setting["apiKey"][0] # 869429e05ea142ef9e3784f8e7965d1c
tuling_user_id = setting["userId"] # "167031"

def chat(text, api_key=tuling_api_key):

    """
    进行聊天
    :return:
    """
    log.add_log("图灵机器人处理中...", 1)
    data = json.load(open("./data/json/tuling_request_template.json", "r", encoding="utf-8"))
    data["perception"]["inputText"]["text"] = text
    data["userInfo"]["userId"] = str(tuling_user_id.encode("GBK"), "utf-8")

    if api_key is None:
        case = 0
        data["userInfo"]["apiKey"] = str(tuling_api_key.encode("GBK"), "utf-8")
    else:
        case = 1
        data["userInfo"]["apiKey"] = str(api_key.encode("GBK"), "utf-8")

    try:
        result = requests.post('http://openapi.tuling123.com/openapi/api/v2',
                                data=json.dumps(data))
    except TypeError:
        log.add_log("request type error", 3)
        conversation.output_func("出了点小错误，请检查后台")
        return

    try:
        res_text = result.json()["results"][-1]["values"]["text"]
    except KeyError:
        log.add_log("Can not find text in response", 3)
        conversation.output_func("出了点小错误，请检查后台")
        return

    if "请求" in text and "超限制" in res_text:
        if case == 0:
            chat(text, api_key=setting["apiKey"][1]) # c88026c156ec49099510625329f9b79d
        elif case == 1:
            chat(text, api_key=setting["apiKey"][2]) # 1f39526b070d4f2791b4c3347033f191
    else:
        conversation.output_func(res_text)
