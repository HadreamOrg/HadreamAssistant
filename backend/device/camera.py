# coding=utf-8
# author: Lan_zhijiang
# date: 2020/12/6
# description: opencv camera operations

# from openni import openni2
import numpy as np
import cv2
import threading
import os


class HACamera:

    def __init__(self, ba):

        self.log = ba.log
        self.camera_setting = ba.setting["device"]["camera"]

        self.camera_id = self.camera_setting["cameraId"]
        self.photo_resolution = self.camera_setting["photoResolution"]
        self.video_resolution = self.camera_setting["videoResolution"]
        self.video_fps = self.camera_setting["videoFps"]

        # self.cv2_camera = cv2.VideoCapture(self.camera_id)

    def capture_image_fswebcam(self, fp="./backend/data/image/capture.jpg", display=False):

        """
        拍照(fswebcam办法) 无法指定拍照设备
        :param fp: 文件名
        :param display: 拍照完以后是否显示
        :return: fp
        """
        self.log.add_log("HACamera: capturing one image using fswebcam in resolution-%s" % self.photo_resolution, 1)

        os.system("fswebcam --no-banner -r %s %s" % (self.photo_resolution, fp))

        self.log.add_log("HACamera: image captured", 1)

        if display:
            display_image_thread = threading.Thread(target=self.show_image, args=(fp, "img_path"))
            display_image_thread.start()

        return fp

    def capture_image_cv(self, fp="./backend/data/image/capture.jpg", display=False):

        """
        拍照(opencv办法) 可以指定拍照设备
        :param fp: 文件名
        :param display: 拍完以后是否显示
        :return: img_data
        """
        self.log.add_log("HACamera: capturing one image using opencv2", 1)

        cv2_camera = cv2.VideoCapture(self.camera_id)
        a, img = cv2_camera.read()
        cv2.imwrite(fp, img)
        cv2_camera.release()

        self.log.add_log("HACamera: image captured", 1)
        if display:
            display_image_thread = threading.Thread(target=self.show_image, args=(img, "img_data"))
            display_image_thread.start()

        return img

    def capture_video(self, fp="./backend/data/video/video.avi", size=None, fps=None):

        """
        录制视频
        :param fp: 文件名
        :param size: 帧大小
        :return:
        """
        if size is None:
            size_split = self.video_resolution.split("x")
            size = (size_split[0], size_split[1])
        if fps is None:
            fps = self.video_fps
        self.log.add_log("HACamera: capturing one video...", 1)
        writer = cv2.VideoWriter(fp, cv2.VideoWriter_fourcc(*'MJPG'), fps, size)

        cv2_camera = cv2.VideoCapture(self.camera_id)
        while cv2_camera.isOpened():
            ret, frame = cv2_camera.read()
            if ret:
                writer.write((frame))
                cv2.imshow('Now capturing...', frame)
                if cv2.waitKey(25) == ord('q'):
                    break
            else:
                break

        writer.release()
        cv2_camera.release()
        cv2.destroyAllWindows()
        self.log.add_log("HACamera: video captured", 1)

    def show_image(self, img, img_type):

        """
        显示图片
        :param img: 要显示的图片 opencv2 image object / 图片路径
        :param img_type: img_data/img_path
        :return:
        """
        if img_type == "img_data":
            self.log.add_log("HACamera: display the img from opencv2 image object", 1)
            cv2.imshow("the image", img)
        elif img_type == "img_path":
            self.log.add_log("HACamera: display the img from file-%s" % img, 1)
            img_data = cv2.imread(img, cv2.IMREAD_COLOR)
            cv2.imshow("the %s" % img, img_data)

        if cv2.waitKey(1) == ord("q"):
            cv2.destroyAllWindows()

