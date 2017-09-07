#!/usr/bin/env python
# -*- coding:utf-8 -*-

import socket
import sys
import re
import time
import gevent


class WSGI():
    def __init__(self, port):
        # 创建套接字
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # 设置套接字
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR,1)
        # 绑定端口
        self.server_socket.bind(("", port))
        # 设置套接字为监听状态
        self.server_socket.listen(128)
        self.DOCUMENT = "./html"

    def nostop_server(self):
        """等待客户端接入"""
        while True:
            # 为新接入的客户端创建一个套接字
            self.client_socket, client_addr = self.server_socket.accept()
            gevent.spawn(self.handle())
        # 关闭套接字
        self.server_socket.close()

    def handle(self):
        """处理客户端发来的数据并回复"""
        while True:
            client_data =self.client_socket.recv(1024)
            # 判断客户端发来的数据是否为空，空表示客户端下线
            if client_data:
                client_data =client_data.decode("utf-8", errors="ignore")
                client_data = client_data.splitlines()
                # 将客户端发来的数据取第一行，再分割出客户端想要得内容
                file_name = re.match(r"[^/]+(/[^ ]*)", client_data[0]).group(1)
                if file_name:
                    if file_name == "/":
                        file_name = "/index.html"
                    else:
                        file_name = file_name
                try:
                    f = open(self.DOCUMENT + file_name, "rb")
                except:
                    res_body = "未找到该页面"
                    res_head = "HTTP/ 404 Forbidden\r\n"
                    res_head += "Content-Type:text/html;charset=utf-8\r\n"   
                    res_head += "Content-Length:%s\r\n" % (len(es_body.decode("utf-8")))
                    res_head += "\r\n"
                    msg = res_head + res_body
                    self.client_socket.send(msg.encode("utf-8"))
                else:
                    content = f.read()
                    res_body = content
                    res_head = "HTTP/ 200 OK\r\n"
                    res_head += "Content-Type:text/html;charset=utf-8\r\n"   
                    res_head += "Content-Length:%s\r\n" % (len(res_body))
                    res_head += "\r\n"
                    self.client_socket.send(res_head.encode("utf-8"))
                    self.client_socket.send(res_body)
            else:
                break
        # 关闭为客户端服务的套接字
        self.client_socket.close()


def main():
    """主控制程序"""
    # 输入一个端口
    if len(sys.argv) == 2:
        print(sys.argv)
        port = int(sys.argv[1])
    else:
        return
    wsgi = WSGI(port)
    wsgi.nostop_server()

if __name__ == "__main__":
    main()
