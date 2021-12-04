import json
import requests

url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer_custom?charset=UTF-8&access_token="
headers = {"Content-Type": "application/json"}
body = {"text": "帮我在党员活动室预约一个周一晚上八点半的会议"}
body = json.dumps(body)
token = "24.eb5a47acf29c38e1c8501b395dc4f751.2592000.1641228504.282335-10835645"


def a():
    r = requests.post(url+token,
                      data=body,
                      headers=headers)

    if r.status_code == 200:
        res = r.json()
        return res
    else:
        return False


if __name__ == "__main__":
    print(a())
