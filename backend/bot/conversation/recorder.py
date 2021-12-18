# -*- coding: utf-8 -*-
# 录制系统

import wave
import pyaudio
import backend.bot.conversation.recorder_with_vad


class HARecorder():

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.recorder_setting = ba.setting["bot"]["conversation"]["recorder"]
    
    def record(self):

        """
        录音(vad)
        :return bool
        """
        self.log.add_log("HARecorder: start vad record(record_with_vad module)", 1)
        backend.bot.conversation.recorder_with_vad.start_record_with_vad(self.recorder_setting["outputPath"])

    def record_time_limitied(self, time=None):

        """
        录音（时间限制）
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

        self.log.add_log("HARecorder: Start record...", 1)

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
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(self.recorder_setting["rate"])
        wf.writeframes(b''.join(frames))
        wf.close()
