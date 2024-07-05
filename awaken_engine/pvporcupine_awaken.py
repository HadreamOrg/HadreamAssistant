# coding=utf-8
# author: Lanzhijiang
# email: lanzhijiang@foxmail.com
# desc: 使用picovoice的porcupine产品实现中文唤醒词

import struct
import pvporcupine
import pyaudio

from lib.log import HALog
from lib.settings import Settings


log = HALog("PorcupineAwakenEngine")
setting = Settings.get_json_setting("awaken_engine")["porcupine"]



def run_in_thread(callback):

    log.add_log("现在启动...", 1)

    porcupine = pvporcupine.create(
        access_key=setting["accessKey"],
        keyword_paths=[setting["keywordPath"]],
        model_path=setting["modelPath"],
    )

    # pv_recorder = PvRecorder(
    #     # device_index=-1,
    #     frame_length=porcupine.frame_length
    # )
    # pv_recorder.start()
    recorder = pyaudio.PyAudio().open(
        format=pyaudio.paInt16,
        channels=1,
        rate=porcupine.sample_rate,
        input=True,
        frames_per_buffer=porcupine.frame_length
    )


    while True:
        # pcm = recorder.read()
        pcm = recorder.read(porcupine.frame_length)
        pcm = struct.unpack_from("h" * porcupine.frame_length, pcm)
        result = porcupine.process(pcm)

        if result >= 0:
            recorder.stop_stream()
            recorder.close()
            callback()
            break

    # recorder.delete()
    porcupine.delete()

