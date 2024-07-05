# coding=utf-8
# author: Lan_zhijiang
# description: https awaken enginbe
# date: 2023/07/04

import socket

from lib.settings import Settings
from lib.log import HALog
from lib.exceptions import Fatal
from conversation.output.tts import HATTS
from lib.common_func import Pixels

from flask import Flask, request
from flask_cors import CORS
from flask import make_response
import json


setting = Settings.get_json_setting("awaken_engine")["http"]
log = HALog("HttpAwakenEngine")

app = Flask("HttpAwakenEngine")
callback = None
# app.debug=True
# CORS(app, resources=r'/api/*')


@app.route('/<op>', methods=["post", "options"])
def api_endpoint(op=None):

    log.add_log("接收到请求-%s, path-%s" %
                 (request.remote_addr, request.path), 1, is_print=False)

    resp = make_response({}, 200)
    if request.method == "OPTIONS":
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Methods'] = 'GET,POST'
        resp.headers['Access-Control-Allow-Headers'] = 'Method,Content-Type,Resource-Fill-Path,Device-Fill-Path'
    else:
        if op == "awaken":
            callback()
        elif op == "speak":
            speak_content = request.get_json(force=True)["speak"]
            # todo 通过http传递要说的内容
            Pixels.speak()
            HATTS.start(speak_content)
            Pixels.off()

    return resp


def run_in_thread(callback_func):
    log.add_log("现在启动... 绑定端口：%s" % setting["port"], 1)
    
    global callback
    callback = callback_func

    app.run("0.0.0.0", setting["port"], ssl_context=(
        "data/cert/server-cert.pem", "data/cert/server-key.pem"
    ))
