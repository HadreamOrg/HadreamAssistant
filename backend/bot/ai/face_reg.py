# coding=utf-8
# author: Lan_zhijiang
# date: 2020/12/6
# description: baidu face recognize

from urllib import parse
import urllib
import json
import requests
import base64


class HAAiFaceReg:

    def __init__(self, ba):

        self.ba = ba
        self.log = ba.log
        self.face_abi_setting = ba.setting["bot"]["ai"]["faceReg"]

        self.ak = self.face_abi_setting["appKey"]  # "n8C6ht73hh75pgYUtwgbviVB"
        self.sk = self.face_abi_setting["secretKey"]  # "FwnT6QdW1TRvkVTNTFWuR1G6pG4vpser"
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
            self.log.add_log("HAAiFaceReg: Sorry! We don't support this type of img data!", 2)

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
            print('FaceReg: Token request failed.')

    def analyze_face(self, face):

        """
        分析人脸
        :param face: 人脸图片数据
        :return
        """
        self.log.add_log("HAAiFaceReg: start analyzing face", 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v3/detect" + "?access_token=" + self.token
        headers = {"Content-Type": "application/json"}
        base64data = base64.b64encode(face)
        data = {
            "image": str(base64data, "utf-8"),
            "image_type": "BASE64",
            "face_field": "age,gender,landmark,quality,facetype"
        }

        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceReg: token is invalid", 2)
            except KeyError:
                self.log.add_log("HAAiFaceReg: face verify success", 1)
                return res
        else:
            self.log.add_log("HAAiFaceReg: http error, code-%s" % r.status_code, 3)

    def face_detect(self, face):

        """
        检测人脸
        :param face:
        :return:
        """
        self.log.add_log("HAAiFaceReg: start detecting face", 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v3/detect" + "?access_token=" + self.token
        headers = {"Content-Type": "application/json"}
        data = {
                "image": str(base64.b64encode(face), "utf-8"),
                "image_type": "BASE64"
        }

        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceReg: token is invalid", 2)
            except KeyError:
                self.log.add_log("HAAiFaceReg: face verify success", 1)
                return res
        else:
            self.log.add_log("HAAiFaceReg: http error, code-%s" % r.status_code, 3)

    def compare_face(self, face1, face2):

        """
        人脸比较
        :param face1: 比较人脸1
        :param face2: 比较人脸2
        :return
        """
        self.log.add_log("HAAiFaceReg: start comparing face", 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v3/match" + "?access_token=" + self.token
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

        if r.status_code == 200:
            res = r.json()
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceReg: token is invalid", 2)
            except KeyError:
                self.log.add_log("HAAiFaceReg: face comparing request success, socre-%s" % res["score"], 1)
                if res["score"] >= 80:
                    self.log.add_log("HAAiFaceReg: according to the result, they are the same one", 1)
                    return True
                else:
                    return False
        else:
            self.log.add_log("HAAiFaceReg: http error, code-%s" % r.status_code, 3)

    def face_identify(self, face, group_id="all"):

        """
        人脸认证
        :param: face: 人脸图片数据
        :param group_id: 用户组
        :return
        """
        self.log.add_log("HAAiFaceReg: start identifying face", 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v3/search" + "?access_token=" + self.token
        headers = {"Content-Type": "application/json"}
        data = {
            "image": str(base64.b64encode(face), "utf-8"),
            "image_type": "BASE64",
            "group_id_list": group_id
        }

        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            # print(res)
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceReg: token is invalid", 3)
            except KeyError:
                self.log.add_log("HAAiFaceReg: face identify success", 1)
                return res
            else:
                if res["error_code"] == 0:
                    self.log.add_log("HAAiFaceReg: face identify success", 1)
                    return res
                elif res["error_code"] == 222202:
                    self.log.add_log("HAAiFaceReg: face not found in picture", 1)
                else:
                    self.log.add_log("HAAiFaceReg: face identify failed, res-%s" % res, 3)
                    return False
        else:
            self.log.add_log("HAAiFaceReg: http error, code-%s" % r.status_code, 3)

    def face_search(self):

        """
        人脸搜索(M:N)
        :return:
        """
        self.log.add_log("HAAiFaceReg: start searching face(M:N)", 1)

    def face_sign_up(self, face, user_id, group_id="all"):

        """
        人脸注册
        :param face: 人脸图片数据
        :param user_id: 用户id
        :param group_id: 组id
        :return
        """
        self.log.add_log("HAAiFaceReg: start signing up face", 1)
        url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/user/add?access_token=%s" % self.token
        headers = {"Content-Type": "application/json"}
        data = {
            "image": str(base64.b64encode(face), "utf-8"),
            "image_type": "BASE64",
            "group_id": group_id,
            "user_id": str(user_id)
        }

        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            try:
                if res["error_code"] == 110:
                    self.log.add_log("HAAiFaceReg: token is invalid", 2)
            except KeyError:
                self.log.add_log("HAAiFaceReg: face sign_up success", 1)
                return res
        else:
            self.log.add_log("HAAiFaceReg: http error, code-%s" % r.status_code, 3)

    def face_delete(self, face):

        """
        删除人脸
        :param face: 人脸数据
        :return:
        """
        self.log.add_log("HAAiFaceReg: start deleting face", 1)

        user_info = self.face_identify(face)["user_list"][0]

        url = "https://aip.baidubce.com/rest/2.0/face/v3/faceset/face/delete"
        headers = {"Content-Type": "application/json"}
        data = {
            "face_token": user_info["face_token"],
            "group_id": user_info["group_id"],
            "user_id": str(user_info["user_id"])
        }

        r = requests.post(url,
                          headers=headers,
                          data=json.dumps(data))

        if r.status_code == 200:
            res = r.json()
            if res["error_code"] == 110:
                self.log.add_log("HAAiFaceReg: token is invalid", 2)
            elif res["error_code"] == 0:
                self.log.add_log("HAAiFaceReg: face delete success", 1)
                return res
        else:
            self.log.add_log("HAAiFaceReg: http error, code-%s" % r.status_code, 3)


# face_reg = FaceReg()
# img_data = face_reg.read_img("F:\\000000各班照片\\23OK\\袁翊闳.jpg", "file_path")
# print(face_reg.face_search(img_data))




