# -*- encoding=utf-8 -*-

import json
import urllib
from urllib import parse
import requests
import base64
# import cv2


class HAAiFaceAbility:
    
    def __init__(self, ba):
        
        self.ba = ba
        self.log = ba.log
        self.face_abi_setting = ba.setting["bot"]["ai"]["faceAbility"]

        self.ak = self.face_abi_setting["appKey"] # "n8C6ht73hh75pgYUtwgbviVB"
        self.sk = self.face_abi_setting["secretKey"] # "FwnT6QdW1TRvkVTNTFWuR1G6pG4vpser"
        self.token = ""

        self.get_token()
        
    def read_img(self, img, img_type):
        
        """
        读取图片数据
        :return
        """
        if img_type == "file_path":
            file = open(img, "rb")
            return_data = file.read()
            file.close()
            return return_data
        elif img_type == "file_data":
            return img
        else:
            self.log.add_log("HAAiFaceAbility: Sorry! We don't support this type of img data!", 2)
    
    def get_token(self):
        
        """
        获取token
        :return 
        """
        url = 'http://openapi.baidu.com/oauth/2.0/token'
        
        params = urllib.parse.urlencode({'grant_type': 'client_credentials',
                                         'client_id': self.ak,
                                         'client_secret': self.sk})
        
        r = requests.get(url, params=params)
        try:
            r.raise_for_status()
            token = r.json()['access_token']
            self.token = token
            return token
        except requests.exceptions.HTTPError:
            self._logger.critical('Token request failed with response: %r',
                                  r.text,
                                  exc_info=True)

    def analyze_face(self, face):
        
        """
        分析人脸
        :param face: 人脸图片数据
        :return
        """
        url = "https://aip.baidubce.com/rest/2.0/face/v2/detect?access_token=%s" % self.token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        face = parse.urlencode(base64.b64encode(face))
        data = {
            "image": str(face, "utf-8"),
            "image_type": "BASE64",
            "face_field": "age,beauty,expression,faceshape,gender,glasses,landmark,race,quality,facetype"
        }
        
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))
        
        return r.json()
        
    def compare_face(self, face1, face2):
        
        """
        人脸对比
        :param face1: 比较人脸1
        :param face2: 比较人脸2
        :return
        """
        url = "https://aip.baidubce.com/rest/2.0/face/v2/match" + "?access_token=" + self.token
        headers = {"Content-Type": "application/json"}
        data = [
            {
                "image": str(base64.b64encode(face1), "utf-8"),
                "image_type": "BASE64"
            },
            {
                "image": str(base64.b64encode(face2), "utf-8"),
                "image_type": "BASE64"
            }
        ]
        
        r = requests.post(url,
                         headers=headers,
                         data=json.dumps(data))
        
        return r.json()
    
    def face_identify(self, face, group_id="all"):
        
        """
        人脸认证 1:N(mode1)
        :param: face: 人脸图片数据
        :return 
        """
        self.log.add_log("HAAiFaceAbility: start face identify, group_id-%s" % group_id, 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v2/identify?access_token=%s" % self.token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        face = parse.urlencode(base64.b64encode(face))
        data = {
            "image": str(face, "utf-8"),
            "image_type": "BASE64",
            "user_top_num": 3,
            "group_id": group_id
        }
        
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceAbility: token is invalid", 2)
            except KeyError:
                self.log.add_log("HAAiFaceAbility: face verify success", 1)
                return {"counts": res["result_num"], "result": res["result"]}

    def face_identify_uid(self, face, uid, group_id):

        """
        人脸校验 1:N(mode2)
        :param: face: 人脸图片数据
        :param: uid: 人脸uid
        :param: group_id: 人脸所在数组
        :return
        """
        self.log.add_log("HAAiFaceAbility: start face verify, uid-%s, group_id-%s" % (uid, group_id), 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v2/verify" + "?access_token=" + self.token
        headers = {"Content-Type": "application/x-www-form-urlencoded"}
        face = parse.urlencode(base64.b64encode(face))
        data = {
            "image": str(face, "utf-8"),
            "top_num": 2,
            "uid": uid,
            "group_id": face_group_id
        }

        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceAbility: token is invalid", 2)
            except KeyError:
                self.log.add_log("HAAiFaceAbility: face verify success", 1)
                return {"result": res["result"]}
        
    def face_sign_up(self, face, user_id, face_group_id=None):
        
        """
        人脸注册
        :param face: 人脸图片数据
        :param user_id: 用户id
        :return
        """
        if face_group_id is None:
            face_group_id = self.face_group_id
        url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add" + "?access_token=" + self.token
        headers = {"Content-Type": "application/json"}
        data = {
            "image": str(base64.b64encode(face), "utf-8"),
            "image_type": "BASE64",
            "group_id": face_group_id,
            "user_id": str(user_id)
        }
        
        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))
        
        return r.json()

    # def detect_face(self, img):

    #     """
    #     人脸检测(cv2)
    #     :param: 图片
    #     :return
    #     """
    #     img = cv2.imread(img)
    #     gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #     classifier = cv2.CascadeClassifier("D:\Hadream\下载\haarcascade_frontalface_default.xml")
    #     color = (0, 255, 0)
    #     classifier.detectMultiScale(gray, scaleFactor=1.2, minNeighbors=3, minSize=(32, 32))
    #     if len(faceRects) > 0:
    #         for faceRect in faceRects:
    #             x, y, w, h = faceRect
    #             cv2.rectangle(img, (x, y), (x + h, y + w), color, 2)
    #             cv2.circle(img, (x + w // 4, y + h // 4 + 30), min(w // 8, h // 8), color)
    #             cv2.circle(img, (x + 3 * w // 4, y + h // 4 + 30), min(w // 8, h // 8), color)
    #             cv2.rectangle(img, (x + 3 * w // 8, y + 3 * h // 4), (x + 5 * w // 8, y + 7 * h // 8), color)
    #     return img
