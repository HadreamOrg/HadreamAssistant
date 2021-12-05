import json
import requests

url = "https://aip.baidubce.com/rpc/2.0/nlp/v1/lexer_custom?charset=UTF-8&access_token="
headers = {"Content-Type": "application/json"}
body = {"text": "帮我预约一个周一晚上八点半在党员活动室举行的会议"}
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

import snowboydecoder
import sys
import signal

interrupted = False


def signal_handler(signal, frame):
    global interrupted
    interrupted = True


def interrupt_callback():
    global interrupted
    return interrupted

if len(sys.argv) == 1:
    print("Error: need to specify model name")
    print("Usage: python demo.py your.model")
    sys.exit(-1)

model = sys.argv[1]

# capture SIGINT signal, e.g., Ctrl+C
signal.signal(signal.SIGINT, signal_handler)

detector = snowboydecoder.HotwordDetector(model, sensitivity=0.5)
print('Listening... Press Ctrl+C to exit')

# main loop
detector.start(detected_callback=snowboydecoder.play_audio_file,
               interrupt_check=interrupt_callback,
               sleep_time=0.03)

detector.terminate()


