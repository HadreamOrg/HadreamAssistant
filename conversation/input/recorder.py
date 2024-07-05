# -*- coding: utf-8 -*-
# author: Lanzhijiang
# desc: 录制音频，支持vad与定时两种模式
# date: 2023/06/27

import time
import webrtcvad
import collections
import sys
import wave
import pyaudio
from array import array
from struct import pack

from conversation.output.player import HAPlayer
from lib.settings import Settings
from lib.log import HALog


class HARecorder:

    setting = Settings.get_json_setting("input")["recorder"]
    log = HALog("HARecorder")

    pyaudio_obj = pyaudio.PyAudio()
    vad = webrtcvad.Vad(1)
    stream = None

    rate = setting["rate"]
    
    # vad param
    CHUNK_SIZE = int(rate * 30 / 1000)
    CHUNK_BYTES = CHUNK_SIZE * 2
    NUM_PADDING_CHUNKS = int(1500 / 30)
    NUM_WINDOW_CHUNKS = int(400 / 30) 
    NUM_WINDOW_CHUNKS_END = NUM_WINDOW_CHUNKS * 2
    START_OFFSET = int(NUM_WINDOW_CHUNKS * 30 * 0.5 * rate)

    got_a_sentence = False
    leave = False   
    
    @classmethod
    def open_stream(cls, chunk_size: int = None):

        if chunk_size is None:
            chunk_size = cls.setting["chunkSize"]

        cls.stream = cls.pyaudio_obj.open(
            format=pyaudio.paInt16,
            channels=cls.setting["channels"],
            rate=cls.rate,
            input=True,
            start=False,
            # input_device_index=2,
            frames_per_buffer=chunk_size
        )

    @classmethod
    def handle_int(cls, sig, chunk):
        cls.leave = True
        cls.got_a_sentence = True

    @classmethod
    def save(cls, path, data, sample_width):
            
        data = pack('<' + ('h' * len(data)), *data)
        wf = wave.open(path, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(sample_width)
        wf.setframerate(cls.rate)
        wf.writeframes(data)
        wf.close()

    @classmethod
    def normalize(cls, snd_data):
        "Average the volume out"
        MAXIMUM = 32767  # 16384
        times = float(MAXIMUM) / max(abs(i) for i in snd_data)
        r = array('h')
        for i in snd_data:
            r.append(int(i * times))
        return r

    @classmethod
    def vad_record(cls, fp: str = None):

        """
        录音(vad)
        :return
        """
        cls.log.add_log("start record(vad)", 1)

        if fp is None:
            fp = cls.setting["outputPath"]

        # HAPlayer.start_recording()

        cls.open_stream()
        while not cls.leave:
            ring_buffer = collections.deque(maxlen=cls.NUM_PADDING_CHUNKS)
            triggered = False
            voiced_frames = []
            ring_buffer_flags = [0] * cls.NUM_WINDOW_CHUNKS
            ring_buffer_index = 0

            ring_buffer_flags_end = [0] * cls.NUM_WINDOW_CHUNKS_END
            ring_buffer_index_end = 0
            buffer_in = ''
            # WangS
            raw_data = array('h')
            index = 0
            start_point = 0
            StartTime = time.time()
            sys.stdout.write('\n')
            print("* 录音中...")
            cls.stream.start_stream()

            while not cls.got_a_sentence and not cls.leave:
                chunk = cls.stream.read(cls.CHUNK_SIZE)
                # add WangS
                raw_data.extend(array('h', chunk))
                index += cls.CHUNK_SIZE
                TimeUse = time.time() - StartTime

                active = cls.vad.is_speech(chunk, cls.rate)

                sys.stdout.write('-' if active else '_')
                ring_buffer_flags[ring_buffer_index] = 1 if active else 0
                ring_buffer_index += 1
                ring_buffer_index %= cls.NUM_WINDOW_CHUNKS

                ring_buffer_flags_end[ring_buffer_index_end] = 1 if active else 0
                ring_buffer_index_end += 1
                ring_buffer_index_end %= cls.NUM_WINDOW_CHUNKS_END

                # start point detection
                if not triggered:
                    ring_buffer.append(chunk)
                    num_voiced = sum(ring_buffer_flags)
                    if num_voiced > 0.8 * cls.NUM_WINDOW_CHUNKS:
                        sys.stdout.write(' 语音起点 ')
                        triggered = True
                        start_point = index - cls.CHUNK_SIZE * 20  # start point
                        # voiced_frames.extend(ring_buffer)
                        ring_buffer.clear()
                    if TimeUse > cls.setting["maxRecordTime"]:
                        triggered = True
                # end point detection
                else:
                    # voiced_frames.append(chunk)
                    ring_buffer.append(chunk)
                    num_unvoiced = cls.NUM_WINDOW_CHUNKS_END - sum(ring_buffer_flags_end)
                    if num_unvoiced > 0.90 * cls.NUM_WINDOW_CHUNKS_END or TimeUse > cls.setting["maxRecordTime"]:
                        sys.stdout.write(' 语音结束 ')
                        triggered = False
                        cls.got_a_sentence = True

                sys.stdout.flush()

            sys.stdout.write('\n')
            # data = b''.join(voiced_frames)

            cls.stream.stop_stream()
            print("* 录音结束")
            sys.stdout.write('\n')
            cls.got_a_sentence = False

            # write to file
            raw_data.reverse()
            for index in range(start_point):
                raw_data.pop()
            raw_data.reverse()
            raw_data = cls.normalize(raw_data)
            cls.save(fp, raw_data, 2)
            cls.leave = True

        cls.leave = False
        cls.stream.close()
        cls.stream = None

        # HAPlayer.stop_recording()

    @classmethod
    def timing_record(cls, time: int = None):

        """
        录音（时间限制）
        :param time: 录音时间(s) 5
        :return:
        """
        if time is None:
            time = cls.setting["recordTime"]

        # HAPlayer.start_recording()

        cls.open_stream()

        cls.log.add_log("开始录音...", 1)

        chunk = cls.setting["chunk"]
        frames = []
        for i in range(0, int(cls.rate / chunk * time)):
            data = cls.stream.read(chunk)
            frames.append(data)

        cls.log.add_log("record end", 1)

        cls.stream.stop_stream()
        cls.stream.close()
        cls.stream = None

        wf = wave.open(cls.setting["outputPath"], 'wb')
        wf.setnchannels(cls.setting["channels"])
        wf.setsampwidth(cls.stream.get_sample_size(pyaudio.paInt16))
        wf.setframerate(cls.rate)
        wf.writeframes(b''.join(frames))
        wf.close()

        # HAPlayer.stop_recording()
