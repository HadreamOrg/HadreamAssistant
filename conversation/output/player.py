# coding=utf-8
# author: Lan_zhijiang
# description: 管理音频输出；支持流式和文件输出
# date: 2021/11/27
# last_edit: 2023/06/27

import pyaudio
# import queue
import wave
import os

from lib.log import HALog
from lib.settings import Settings


class HAPlayer:

    log = HALog("HAPlayer")
    setting = Settings.get_json_setting("output")["player"]

    stop = False  # 表示，播放器的停止状态；不等于暂停
    # output_queue = queue.Queue(8)

    pyaudio_obj = pyaudio.PyAudio()
    stream = None

    # @classmethod
    # def put(cls, data):

    #     """
    #     将块音频数据放入输出队列
    #     :param data: 要被放入的块数据
    #     :return:
    #     """
    #     cls.log.add_log("推入数据", 0, is_print=False)
    #     cls.output_queue.put(data)

    # @classmethod
    # def stream_output(cls):

    #     """
    #     流式输出音频
    #     :return:
    #     """
    #     cls.log.add_log("开始流式输出", 1)

    #     p = pyaudio.PyAudio()

    #     stream = p.open(
    #         format=p.get_format_from_width(2),
    #         channels=1,
    #         rate=160000,
    #         output=True)

    #     c_data = cls.output_queue.get()
    #     while c_data != b'':
    #         stream.write(c_data)
    #         c_data = cls.output_queue.get()

    #     stream.stop_stream()
    #     stream.close()

    #     p.terminate()

    @classmethod
    def file_play(cls, fp):

        """
        文件式播放
        :param fp: 文件路径
        :return:
        """
        cls.log.add_log("播放音频文件: %s" % fp, 0)
        try:
            wf = wave.open(fp, "rb")
        except wave.Error:
            cls.log.add_log("无法打开音频文件", 3)
            return
        
        stream = cls.pyaudio_obj.open(
            format=cls.pyaudio_obj.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True
        )

        data = wf.readframes(1024)
        while data != b'' and not cls.stop:
            stream.write(data)
            data = wf.readframes(1024)

        cls.stop = False

        stream.stop_stream()
        stream.close()

        cls.log.add_log("播放结束", 0)

    @classmethod
    def data_play(cls, data):

        """
        数据式播放
        """
        cls.log.add_log("播放数据", 0)


    @classmethod
    def say(cls, **sth):

        """
        播放say.wav
        :return:
        """
        cls.file_play(cls.setting["say"])

    @classmethod
    def start_recording(cls):

        """
        播放开始录音提示音
        :return:
        """
        cls.file_play(cls.setting["start_recording"])

    @classmethod
    def stop_recording(cls):

        """
        播放录音结束提示音
        :return:
        """
        cls.file_play(cls.setting["stop_recording"])

    @classmethod
    def convert_format(cls, fp, ori, goal):

        """
        音频文件格式转换
        :param fp: 文件路径
        :param ori: 原格式
        :param goal: 目标格式
        :return:
        """
        cls.log.add_log("Convert " + fp + " to " + goal, 1)
        soundpcm = os.getcwd() + fp.replace(ori, goal)
        cmd = 'ffmpeg -y -i ' + os.getcwd() + fp + ' -acodec pcm_u16 ' + soundpcm + ' '
        os.system(cmd)
