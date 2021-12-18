import urllib.parse
import requests
import json


class HANlp:

    def __init__(self):

        self.app_key = "EzSEdCoje0SVvCUsFmI7bLwG"
        self.secret_key = "Zsyx4x9LiuzNMfhyAH2B4yCBluYCRnS2"
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
            return ""

    def lexer(self, text):

        """
        词法分析
        :param text: 原始文本
        :return:
        """
        print("HANlp: start text lexer: text-%s" % text)

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer_custom?charset=UTF-8&access_token="
        headers = {"Content-Type": "application/json"}
        body = {"text": text}
        body = json.dumps(body)

        def a():
            r = requests.post(url + self.token,
                              data=body,
                              headers=headers)

            if r.status_code == 200:
                res = r.json()
                try:
                    if res["error_code"] == 110:
                        self.get_token()
                        result = a()
                    else:
                        result = False
                except KeyError:
                    result = res
                return result
            else:
                print("HANlp: text lexer meet an http error, code-%s" % r.status_code)
                return False

        return a()

    def ecnet(self, text):

        """
        文本纠错
        :param text: 原始文本
        :return:
        """
        text = str(text, "utf-8")
        print("HANlp: start text ecnet: text-%s" % text)

        url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/ecnet?charset=UTF-8&access_token="
        headers = {"Content-Type": "application/json"}
        body = {"text": text}
        body = json.dumps(body)

        def a():
            r = requests.post(url + self.token,
                              data=body,
                              headers=headers)

            if r.status_code == 200:
                res = r.json()
                try:
                    if res["error_code"] == 110:
                        self.get_token()
                        result = a()
                    else:
                        print("HANlp: ecnet meet an error, res-%s" % res)
                        result = text
                except KeyError:
                    result = res["item"]["correct_query"]

                return result
            else:
                print("HANlp: text ecnet meet an http error, code-%s" % r.status_code)
                return False

        return a()

    def lexer_result_process(self, lexer_result):

        """
        对语法分析结果进行加工
        :param lexer_result: 语法分析结果
        :return: dict
        """
        print("HANlp: start lexer result process")
        result = {
            "ne": {},
            "pos": {}
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


from pypinyin import lazy_pinyin
nlp = HANlp()
personnel_list = json.load(open("./data/json/personnel_list.json", "r", encoding="utf-8"))
text = "袁艺红"
text_type = "word"
result_list = []

if text_type == "sentence":
    # nlp mode
    nlp_result = nlp.lexer_result_process(nlp.lexer(text))
    print(nlp_result)
    per_result = nlp_result["ne"]["PER"]
    for i in per_result:
        name = i["content"]
        result = ""
        word_pinyin = lazy_pinyin(name)
        for a in word_pinyin:
            result = result + a[0]
        result_list.append(result)
    # [{'offset': 5, 'length': 3, 'content': '玫红红', 'basic_words': ['玫', '红红'], 'ne': 'PER', 'pos': ''}]

elif text_type == "word":
    result = ""
    # nickname mode
    nickname_list = personnel_list["nickname"]
    for nickname_group in nickname_list:
        for nickname in nickname_group[0]:
            if nickname == text:
                result = nickname_group[-1]
                break
        if result != "":
            break

    if result == "":
        # pinyin head mode
        word_pinyin = lazy_pinyin(text)
        for a in word_pinyin:
            result = result + a[0]

    result_list.append(result)

if not result_list:
    print("HAPersonnelManager: failed to analyze person_id from text")
else:
    print("HAPersonnelManager: person_id analyze success, result-%s" % result_list)

print(result_list)