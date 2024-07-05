# coding=utf-8
# author: Lan_zhijiang
# description: socket awaken enginbe
# date: 2023/06/28
# last_edit: 2023/06/28

import socket

from lib.settings import Settings
from lib.log import HALog

setting = Settings.get_json_setting("awaken_engine")["socket"]
log = HALog("SocketAwakenEngine")


def create_bind_server():

    server_addr = ('0.0.0.0', setting["port"]) 
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
    server.bind(server_addr) 
    server.listen(5) 
    return server


def run_in_process(pipe):

    log.add_log("现在启动...", 1)
    server = create_bind_server()
    log.add_log("Socket已经绑定", 1)

    while True:
        client, client_addr = server.accept()
        while True :
            data = client.recv(64)
            pipe[1].send("SocketAwakenEngine")
    
    server.close()


def run_in_thread(callback):
 
    log.add_log("现在启动...", 1)
    server = create_bind_server()
    log.add_log("Socket已经绑定", 1)

    while True:
        client, client_addr = server.accept()
        while True :
            log.add_log("接收到客户端连接: %s" % client_addr[0], 1)
            data = client.recv(64)
            if data == b"awaken":
                callback(client=client)
                break
    
    server.close()
