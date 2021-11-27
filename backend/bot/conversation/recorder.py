# -*- coding: utf-8 -*-
# 录制系统

import wave
import pyaudio


class XiaolanRecorder():

    def __init__(self, log, setting):
        
        self.log = log
        self.setting = setting

        self.recorder_setting = setting["bot"]["conversation"]["recorder"]
        self.format = pyaudio.paInt16
    
    def record(self, time=None):

        """
        录音
        :param time: 录音时间
        :return:
        """
        if time is None:
            time = self.recorder_setting["recordTime"]

        p = pyaudio.PyAudio()
        stream = p.open(format=self.format,
                        channels=self.recorder_setting["channel"],
                        rate=self.recorder_setting["rate"],
                        input=True,
                        frames_per_buffer=self.recorder_setting["chunk"])

        self.log.add_log("HARecorder: Start recording...", 1)

        frames = []
        for i in range(0, int(self.recorder_setting["rate"] / self.recorder_setting["chunk"] * time)):
            data = stream.read(self.recorder_setting["chunk"])
            frames.append(data)

        self.log.add_log("HARecorder: Record end", 1)

        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(self.recorder_setting["outputPath"], 'wb')
        wf.setnchannels(self.recorder_setting["channel"])
        wf.setsampwidth(p.get_sample_size(self.format))
        wf.setframerate(self.recorder_setting["rate"])
        wf.writeframes(b''.join(frames))
        wf.close()
