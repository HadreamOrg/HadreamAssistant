import json
import requests 
import pyaudio
import json
import wave
import base64
import urllib.parse

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

def b():

    p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.recorder_setting["channel"],
                        rate=self.recorder_setting["rate"],
                        input=True,
                        frames_per_buffer=self.recorder_setting["chunk"])

        print("start record")

        frames = []
        for i in range(0, int(self.recorder_setting["rate"] / self.recorder_setting["chunk"] * time)):
            data = stream.read(self.recorder_setting["chunk"])
            frames.append(data)

        print("record stop")

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open("./record.wav", 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()

    fp = "./record.wav"
    try:
        wav_file = wave.open(fp, 'rb')
    except IOError:
        print("IO ERROR")
    n_frames = wav_file.getnframes()
    frame_rate = wav_file.getframerate()
    audio = wav_file.readframes(n_frames)

    


if __name__ == "__main__":
    print(a())

